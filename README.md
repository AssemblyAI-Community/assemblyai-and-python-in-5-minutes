# speech-recognition-in-5-minutes-with-python

Repo for hosting tutorial code associated with the [Speech-to-Text in 5 Minutes with Python](www.assemblyai.com/blog/speech-to-text-in-5-minutes-with-python/) blog by [AssemblyAI](https://www.assemblyai.com/)


## Requirements

```console
$ pip install requests
```

## Usage:

If your AssemblyAI API key is stored in the `api_key.txt` file, then you can omit the optional `--api_key` argument.

```console
$ python transcribe.py audio_file [--local] [--api_key=<YOUR-API-KEY>"]
```

Example for hosted file:

```console
$ python transcribe.py https://github.com/AssemblyAI-Examples/speech-recognition-in-5-minutes-with-python/raw/main/audio.mp3 --api_key=<YOUR-API-KEY>
```

Example for local file:

```console
$ python transcribe.py <YOUR-API-KEY> audio.mp3 --local --api_key=<YOUR-API-KEY>
```
