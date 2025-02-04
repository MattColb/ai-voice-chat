from boto3 import client
import pyaudio

polly = client("polly", region_name="us-east-1")

response = polly.synthesize_speech(
        Text="Hi. My name is Joanna.",
        OutputFormat="mp3",
        VoiceId="Joanna")

print(response)
with open("test.wav", "wb") as f:
    f.write(response["AudioStream"].read())

def test_function(audio_bytes):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True)
    
    stream.write(audio_bytes)

    stream.stop_stream()
    stream.close()
    p.terminate()

test_function(response["AudioStream"].read())