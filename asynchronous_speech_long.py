import os
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Martin/Git/keys/speech2text-1597656821253-be85a49eb749.json"


def sample_long_running_recognize(storage_uri):
    client = speech_v1.SpeechClient()

    sample_rate_hertz = 16000

    language_code = "cs-CZ"

    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "sample_rate_hertz": sample_rate_hertz,
        "language_code": language_code,
        "encoding": encoding,
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    print("Waiting for operation to complete...")
    response = operation.result()

    for result in response.results:
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))
    return response


if __name__ == '__main__':
    storage_uri = "gs://pdtsc-audio/audio/pdtsc_001.wav"

    response = sample_long_running_recognize(storage_uri)