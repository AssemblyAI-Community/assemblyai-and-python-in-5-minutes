import sys
import requests
import time


upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"


# Adds a progress bar to the terminal
def progress(count, total=5 * 60, status=''):
    """
    Copied from https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    """

    bar_len = 60
    capped_count = min(count, 300)
    filled_len = int(round(bar_len * capped_count / float(total)))
    percents = round(100.0 * capped_count / float(total), 1)
    bar = f"{'=' * filled_len}{'-' * (bar_len - filled_len)}"

    sys.stdout.write("\033[K")
    sys.stdout.write('%s: [%s] %s%s\r' % (status, bar, percents, '%'))
    sys.stdout.flush()


# Helper for `upload_file()`
def _read_file(filename, chunk_size=5242880):
    with open(filename, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


# Uploads a file to AAI servers
def upload_file(audio_file, header):
    upload_response = requests.post(
        upload_endpoint,
        headers=header, data=_read_file(audio_file)
    )
    return upload_response.json()


# Request transcript for file uploaded to AAI servers
def request_transcript(upload_url, header):
    transcript_request = {
        'audio_url': upload_url['upload_url']
    }
    transcript_response = requests.post(
        transcript_endpoint,
        json=transcript_request,
        headers=header
    )
    return transcript_response.json()


# Make a polling endpoint
def make_polling_endpoint(transcript_response):
    polling_endpoint = "https://api.assemblyai.com/v2/transcript/"
    polling_endpoint += transcript_response['id']
    return polling_endpoint


# Wait for the transcript to finish
def wait_for_completion(polling_endpoint, header):
    delay = 0.25
    backoff = 2

    progress_counter = 0
    progress(progress_counter, status="Transcribing")
    while True:
        polling_response = requests.get(polling_endpoint, headers=header)
        polling_response = polling_response.json()

        if polling_response['status'] == 'completed':
            progress(300, status="Completed")
            break

        time.sleep(delay)
        progress_counter += 2 * delay
        progress(progress_counter, status="Transcribing")
        if delay <= 5:
            delay *= backoff


# Get the paragraphs of the transcript
def get_paragraphs(polling_endpoint, header):
    paragraphs_response = requests.get(polling_endpoint + "/paragraphs", headers=header)
    paragraphs_response = paragraphs_response.json()

    paragraphs = []
    for para in paragraphs_response['paragraphs']:
        paragraphs.append(para)

    return paragraphs

