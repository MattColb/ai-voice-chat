import asyncio
import record_audio
import sys

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1

# An example file can be found at tests/integration/assets/test.wav
AUDIO_PATH = "./output.wav"
CHUNK_SIZE = 1024
REGION = "us-east-1"

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream):
        super().__init__(output_stream)
        self.end_idx = 0
        self.current_transcription = ""

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This may need to be changed to handle updates to the previous context?
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                self.current_transcription = alt.transcript
                newly_transcribed = self.current_transcription[self.end_idx:]
                self.end_idx = len(self.current_transcription)
                print(newly_transcribed, end="")
                sys.stdout.flush()

async def basic_transcribe():
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region=REGION)

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=SAMPLE_RATE,
        media_encoding="pcm",
    )

    async def write_chunks():
        async for chunk in record_audio.recording():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())
    return handler.current_transcription

async def get_transcription():
    current_transcription = await basic_transcribe()
    return current_transcription

if __name__ == "__main__":
    asyncio.run(get_transcription())