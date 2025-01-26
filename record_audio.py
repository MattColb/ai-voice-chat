import pyaudio
import wave
import threading
import asyncio

def wait_for_input():
    input()
    global recording
    recording = False

recording = True
chunk = 1024
sample_format = pyaudio.paInt16  
channels = 1
fs = 16000
filename = "output.wav"

async def recording():
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print("----------------------record device list---------------------")
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

    print("-------------------------------------------------------------")

    index = int(input())
    print("recording via index "+str(index)+"Press enter when done")

    thread = threading.Thread(target=wait_for_input)
    thread.start()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True, input_device_index=index)

    frames = [] 

    while recording:
        data = stream.read(chunk)
        frames.append(data)

    thread.join()

    stream.stop_stream()
    stream.close()
    p.terminate()
    return frames, p

async def main():
    frames, p = await recording()
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    asyncio.run(main())