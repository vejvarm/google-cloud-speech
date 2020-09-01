import asyncio
import os
import re
import sys

from google.cloud import speech

from flags import FLAGS
from helpers import get_current_time, kw_spotter, kw_decoder
from Microphone import ResumableMicrophoneStream
from WizLights import WizLight, light_commands

# Audio recording parameters
STREAMING_LIMIT = FLAGS.streaming_limit
SAMPLE_RATE = FLAGS.sample_rate
CHUNK_SIZE = FLAGS.chunk_size

# Cloud permissions
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FLAGS.google_cloud_auth_key


RED = '\033[0;31m'
GREEN = '\033[0;32m'
LIGHT_GREEN = "\033[1;32m"
YELLOW = '\033[0;33m'

if len(sys.argv) > 1:
    if "offline" in sys.argv[1]:
        FLAGS.online = False


def listen_print_loop(responses, stream, lights=None):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """

    for response in responses:

        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        result_seconds = 0
        result_nanos = 0

        if result.result_end_time.seconds:
            result_seconds = result.result_end_time.seconds

        if result.result_end_time.nanos:
            result_nanos = result.result_end_time.nanos

        stream.result_end_time = int((result_seconds * 1000)
                                     + (result_nanos / 1000000))

        corrected_time = (stream.result_end_time - stream.bridging_offset
                          + (STREAMING_LIMIT * stream.restart_counter))
        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.

        if result.is_final:

            sys.stdout.write(GREEN)
            sys.stdout.write('\033[K')
            sys.stdout.write(str(corrected_time) + ': ' + transcript + '\n')

            stream.is_final_end_time = stream.result_end_time
            stream.last_transcript_was_final = True

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|ukončit)\b', transcript, re.I):
                sys.stdout.write(YELLOW)
                sys.stdout.write('Ukončuji...\n')
                stream.closed = True
                break

            # Keyword spotting
            matches = kw_spotter([transcript], FLAGS.keywords)
            kw_decoded = kw_decoder(matches, FLAGS.device_map, FLAGS.location_map, FLAGS.command_map)
            if kw_decoded:
                device, locations, command = kw_decoded[0]
                sys.stdout.write(LIGHT_GREEN)
                sys.stdout.write(f"device: {device} locations: {locations} command: {command}\n")

                if lights and "light" in device:
                    light_commands(lights, locations, command)

            kw_decoded.clear()

        else:
            sys.stdout.write(RED)
            sys.stdout.write('\033[K')
            sys.stdout.write(str(corrected_time) + ': ' + transcript + '\r')

            stream.last_transcript_was_final = False


def main():
    """start bidirectional streaming from microphone input to speech API"""

    client = speech.SpeechClient()
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code='cs-CZ',
        max_alternatives=1)
    streaming_config = speech.types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
    print(mic_manager.chunk_size)

    sys.stdout.write(GREEN)
    sys.stdout.write("Vytvářím smyčku.\n")
    loop = asyncio.get_event_loop()
    if FLAGS.online:
        sys.stdout.write("Připojuji se ke světlům.\n")
        lights = {k: WizLight(v, loop) for k, v in FLAGS.lights.items()}
    else:
        sys.stdout.write("Zahajuji offline režim.\n")
        lights = None

    sys.stdout.write(YELLOW)
    sys.stdout.write('\nPoslouchám, pro ukončení řekněte "Ukončit" nebo "Exit".\n\n')
    sys.stdout.write('Konec (ms)       Výsledky přepisů/Status\n')
    sys.stdout.write('=====================================================\n')

    with mic_manager as stream:

        while not stream.closed:
            sys.stdout.write(YELLOW)
            sys.stdout.write('\n' + str(
                STREAMING_LIMIT * stream.restart_counter) + ': NEW REQUEST\n')

            stream.audio_input = []
            audio_generator = stream.generator()

            requests = (speech.types.StreamingRecognizeRequest(
                audio_content=content)for content in audio_generator)

            responses = client.streaming_recognize(streaming_config,
                                                   requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses, stream, lights)

            if stream.result_end_time > 0:
                stream.final_request_end_time = stream.is_final_end_time
            stream.result_end_time = 0
            stream.last_audio_input = []
            stream.last_audio_input = stream.audio_input
            stream.audio_input = []
            stream.restart_counter = stream.restart_counter + 1

            if not stream.last_transcript_was_final:
                sys.stdout.write('\n')
            stream.new_stream = True


if __name__ == '__main__':

    main()
