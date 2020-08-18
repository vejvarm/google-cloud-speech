import os
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Martin/Git/keys/speech2text-1597656821253-be85a49eb749.json"


def sample_recognize(storage_uri):
    """
    Performs synchronous speech recognition on an audio file
Speech2Text-bb59621b56c2
    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
    """

    client = speech_v1.SpeechClient()

    # storage_uri = 'gs://cloud-samples-data/speech/brooklyn_bridge.mp3'

    # The language of the supplied audio
    language_code = "cs-CZ"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 16000

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    audio = {"uri": storage_uri}

    response = client.recognize(config, audio)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))
    return response


if __name__ == '__main__':
    storage_uri = "gs://pdtsc-audio/audio/pdtsc_001_sample_2.wav"

    response = sample_recognize(storage_uri)