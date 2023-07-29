import argparse
import os
import utils
from google.cloud import storage, bigquery

# Hardcoded bucket name.  
# To replicate, you'd need to create your own GCP bucket, Big Query data set, and have google_application_credentials
BUCKET_NAME = 'assemblyai_transcripts'
# Hardcoded BigQuery dataset and table name
DATASET_NAME = 'assemblyai'
TABLE_NAME = 'transcript'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('audio_file', help='url to file or local audio filename')
    parser.add_argument('--local', action='store_true', help='must be set if audio_file is a local filename')
    parser.add_argument('--api_key', action='store', help='<YOUR-API-KEY>')

    args = parser.parse_args()

    if args.api_key is None:
        args.api_key = os.getenv("AAI_API_KEY")
        if args.api_key is None:
            raise RuntimeError("AAI_API_KEY environment variable not set. Try setting it now, or passing in your "
                               "API key as a command line argument with `--api_key`.")

    # Create header with authorization along with content-type
    header = {
        'authorization': args.api_key,
        'content-type': 'application/json'
    }

    if args.local:
        # Upload the audio file to AssemblyAI
        upload_url = utils.upload_file(args.audio_file, header)
    else:
        upload_url = {'upload_url': args.audio_file}

    # Request a transcription
    transcript_response = utils.request_transcript(upload_url, header)

    # Create a polling endpoint that will let us check when the transcription is complete
    polling_endpoint = utils.make_polling_endpoint(transcript_response)

    # Wait until the transcription is complete
    utils.wait_for_completion(polling_endpoint, header)

    # Request the paragraphs of the transcript
    paragraphs = utils.get_paragraphs(polling_endpoint, header)

    # Create a single long string containing the entire transcript
    transcript_text = ""
    for para in paragraphs:
        transcript_text += para['text'] + '\n'

    # Store the transcription in Google Cloud Storage
    store_in_gcs(transcript_text)

    # Load the transcript into BigQuery
    load_into_bigquery(transcript_text)

    return


def store_in_gcs(transcript_text):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("transcript.txt")
    blob.upload_from_string(transcript_text)
    print(f"Transcription stored in Google Cloud Storage bucket '{BUCKET_NAME}' as 'transcript.txt'.")


def load_into_bigquery(transcript_text):
    bq_client = bigquery.Client()
    dataset_ref = bq_client.dataset(DATASET_NAME)
    table_ref = dataset_ref.table(TABLE_NAME)

    # Define the schema of the table
    schema = [bigquery.SchemaField('transcript', 'STRING')]

    # Create the table if it does not exist
    table = bigquery.Table(table_ref, schema=schema)
    table = bq_client.create_table(table, exists_ok=True)

    # Insert the transcript text into the table as a single row
    row = {'transcript': transcript_text}
    errors = bq_client.insert_rows(table, [row])

    if errors == []:
        print("Transcript data loaded into BigQuery successfully.")
    else:
        print(f"Error loading transcript data into BigQuery: {errors}")


if __name__ == '__main__':
    main()
