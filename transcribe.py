import argparse
import math
import os
import sys
import utils


def write_welcome_banner():
    terminal_size = os.get_terminal_size().columns
    sys.stdout.write("#" * terminal_size + "\n")
    sys.stdout.write(
        "#" * math.floor((terminal_size - 15) / 2) +
        "  Assembly AI  " +
        "#" * math.ceil((terminal_size - 15) / 2) + "\n"
    )
    sys.stdout.write("#" * os.get_terminal_size().columns + "\n\n")


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

    write_welcome_banner()
    sys.stdout.write("Uploading files...\r")

    if args.local:
        # Upload the audio file to AssemblyAI
        upload_url = utils.upload_file(args.audio_file, header)
    else:
        upload_url = {'upload_url': args.audio_file}

    sys.stdout.write("Requesting Transcript...\r")
    # Request a transcription
    transcript_response = utils.request_transcript(upload_url, header)

    sys.stdout.write("Beginning Transcription...\r")
    # Create a polling endpoint that will let us check when the transcription is complete
    polling_endpoint = utils.make_polling_endpoint(transcript_response)

    # Wait until the transcription is complete
    utils.wait_for_completion(polling_endpoint, header)

    # Request the paragraphs of the transcript
    paragraphs = utils.get_paragraphs(polling_endpoint, header)

    # Save and print transcript
    with open('transcript.txt', 'w') as f:
        for para in paragraphs:
            print(para['text'] + '\n')
            f.write(para['text'] + '\n')

    return


if __name__ == '__main__':
    main()
