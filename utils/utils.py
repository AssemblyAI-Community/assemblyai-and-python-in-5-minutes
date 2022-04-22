import requests
import time
import json
#import youtube_dl

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = "https://api.assemblyai.com/v2/upload"

# Create youtube_dl options dictionary
def _make_ydl_opts(ffmpeg_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "ffmpeg_location": ffmpeg_path,
        "outtmpl": "./%(id)s.%(ext)s",
    }
    return ydl_opts

# Download youtube video
def download_video(ffmpeg_path=".\\FFmpeg\\bin", yt_link='https://www.youtube.com/watch?v=x_406XLbjxY'):
	ydl_opts = make_ydl_opts(ffmpeg_path=ffmpeg_path)

	yt_link.strip()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    meta = ydl.extract_info(yt_link)

	return meta

# Make headers for AAI API
def make_headers(api_key):
	headers_auth_only = {"authorization": api_key}
	headers = {
	    "authorization": api_key,
	    "content-type": "application/json"
	}
	return headers

# Helper for `upload_file()`
def _read_file(filename, chunk_size=5242880):
    with open(filename, "rb") as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data

# Uploads a file to AAI servers
def upload_file(audio_file, headers):
	upload_response = requests.post(
	    upload_endpoint,
	    headers=headers, data=_read_file(audio_file)
	)
	upload_url = upload_response.json()

	return upload_url

# Request transcript for file uploaded to AAI servers
def request_transcript(upload_url, headers):
	transcript_request = {
    	'audio_url': upload_url['upload_url']
	}
	transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
	transcript_response = transcript_response.json()
	return transcript_response

# Make a polling endpoint
def make_polling_endpoint(transcript_response):
	polling_endpoint = "https://api.assemblyai.com/v2/transcript/"
	polling_endpoint += transcript_response['id']
	return polling_endpoint

# Wait for the transcript to finish
def wait_for_completion(polling_endpoint, headers):
	while True:
	    polling_response = requests.get(polling_endpoint, headers=headers)    
	    polling_response = polling_response.json()

	    if polling_response['status'] == 'completed':
	        break
	    
	    time.sleep(5)

# Get the paragraphs of the transcript
def get_paragraphs(polling_endpoint, headers):
	paragraphs_response = requests.get(polling_endpoint + "/paragraphs", headers=headers)

	paragraphs = []
	paras = []
	for para in paragraphs_response.json()['paragraphs']:
	    paras.append(para)
	paragraphs.append(paras)

	return paras

