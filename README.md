# speech-recognition-in-5-minutes-with-python

Repo for hosting tutorial code associated with the [Speech-to-Text in 5 Minutes with Python](www.assemblyai.com/blog/speech-to-text-in-5-minutes-with-python/) blog by [AssemblyAI](https://www.assemblyai.com/)


## Requirements

```console
$ pip install requests
```

## Usage:

```console
$ python transcribe.py api_key audio_file [--local]
```

Example for hosted file:

```console
$ python transcribe.py <YOUR-API-KEY> https://github.com/AssemblyAI-Examples/speech-recognition-in-5-minutes-with-python/raw/main/audio.mp3
```

Example for local file:

```console
$ python transcribe.py <YOUR-API-KEY> audio.mp3 --local
```
