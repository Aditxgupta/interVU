import os
import threading
import asyncio
import pyaudio
import wave
import tempfile
import replicate
from queue import Queue
from google import genai
from google.genai.types import LiveConnectConfig, Modality, HttpOptions, SpeechConfig, VoiceConfig, PrebuiltVoiceConfig, Content, Part

# API key from environment variable
API_KEY = "AIzaSyDZ4xgDS0ZhcQTUutPfi0hN4AE-ePw17Zc"
MODEL_NAME = "gemini-2.0-flash-exp"

# Replicate API token
REPLICATE_API_TOKEN = "r8_4mrjqKxsndO0yqtYkMhahZdMnbiNfBQ4LnC5q" # get it from replicate's website 

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK_SIZE = 1024
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000

class InterviewManager:
    def __init__(self):
        self.is_active = False
        self.interview_thread = None
        self.audio_handler = None
        self.client = None
        self.session = None
        self.loop = None
        self.message_queue = Queue()
        
    def get_messages(self):
        """Get any new messages from the queue"""
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages
    
    async def _run_interview(self):
        try:
            # Setup audio handler
            self.audio_handler = AudioHandler()
            print("Setting up audio streams...")
            self.audio_handler.setup_streams()
            
            # Initialize Gemini client
            self.client = genai.Client(
                api_key=API_KEY,
                http_options=HttpOptions(api_version="v1alpha")
            )
            
            # Configure with Kore voice and system instruction
            config = LiveConnectConfig(
                response_modalities=["AUDIO"],
                speech_config=SpeechConfig(
                    voice_config=VoiceConfig(
                        prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Kore")
                    )
                ),
                system_instruction=Content(
                    parts=[
                        Part(
                            text="You should act as an interviewer, starting by gathering key details such as the candidate's name, background, experience level, and the role or domain they are interviewing for. Based on this information, it should dynamically generate relevant questions, adjusting the difficulty and focus accordingly. During the interview, it should encourage detailed responses, probe deeper where necessary, and maintain a natural conversational flow. At the end, when asked, you should provide constructive feedback on the candidate's answers, highlighting strengths, pointing out areas for improvement, and suggesting ways to enhance clarity, technical depth, or communication skills.."
                        )
                    ]
                )
            )
            
            print("\nStarting interview conversation...")
            
            async with self.client.aio.live.connect(model=MODEL_NAME, config=config) as session:
                self.session = session
                
                # Main interview loop
                while self.is_active:
                    # Record audio and convert to text
                    audio_data = self.audio_handler.record_audio()
                    text = self.audio_handler.audio_to_text(audio_data)
                    
                    if text is None or text == "":
                        print("No speech detected, please try again.")
                        continue
                    
                    print(f"User said: {text}")
                    
                    # Add user's message to queue
                    self.message_queue.put({
                        "type": "user",
                        "text": text
                    })
                    
                    try:
                        # Send text to Gemini
                        await session.send(input=text, end_of_turn=True)
                        print("Processing...")
                        
                        # Open new WAV file for response
                        with wave.open("output.wav", "wb") as output_wav:
                            output_wav.setnchannels(CHANNELS)
                            output_wav.setsampwidth(2)
                            output_wav.setframerate(OUTPUT_SAMPLE_RATE)
                            
                            async for response in session.receive():
                                if response.data:
                                    output_wav.writeframes(response.data)
                                elif response.text:
                                    print(f"AI response: {response.text}")
                                    # Add AI's response to queue
                                    self.message_queue.put({
                                        "type": "ai",
                                        "text": response.text
                                    })
                        
                        # Play the response
                        print("Playing response...")
                        with wave.open("output.wav", "rb") as wf:
                            self.audio_handler.output_stream.write(wf.readframes(wf.getnframes()))
                            
                    except Exception as e:
                        print(f"Error getting AI response: {e}")
                        self.message_queue.put({
                            "type": "system",
                            "text": "Error getting AI response. Please try again."
                        })
                    
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
            self.message_queue.put({
                "type": "system",
                "text": f"Error: {str(e)}"
            })
        finally:
            if self.audio_handler:
                self.audio_handler.close()
            print("\nSession ended.")
            self.message_queue.put({
                "type": "system",
                "text": "Interview session ended."
            })
            
    def _run_interview_async(self):
        """Run the asyncio event loop in a thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run_interview())
    
    def start_interview(self):
        """Start the interview process using the audio backend"""
        if self.is_active:
            return {"status": "error", "message": "Interview already in progress"}
        
        self.is_active = True
        self.loop = asyncio.new_event_loop()
        
        # Start interview in a separate thread
        self.interview_thread = threading.Thread(target=self._run_interview_async)
        self.interview_thread.daemon = True
        self.interview_thread.start()
        
        return {"status": "success", "message": "Interview started"}
    
    def stop_interview(self):
        """Stop the active interview"""
        if not self.is_active:
            return {"status": "error", "message": "No interview in progress"}
        
        self.is_active = False
        
        # Clean up resources
        if self.audio_handler:
            self.audio_handler.close()
            
        # Wait for thread to finish
        if self.interview_thread and self.interview_thread.is_alive():
            self.interview_thread.join(timeout=2.0)
            
        return {"status": "success", "message": "Interview stopped"}

# Create a singleton instance
interview_manager = InterviewManager()

# This function would be imported and used in your Flask routes
def get_interview_manager():
    return interview_manager

class AudioHandler:
    def __init__(self):
        print("Initializing AudioHandler...")
        self.pa = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        print("AudioHandler initialized")
        
    def setup_streams(self):
        try:
            print("\nSetting up audio streams...")
            print("Available audio devices:")
            for i in range(self.pa.get_device_count()):
                dev_info = self.pa.get_device_info_by_index(i)
                print(f"Device {i}: {dev_info['name']}")
                print(f"  Max Input Channels: {dev_info['maxInputChannels']}")
                print(f"  Max Output Channels: {dev_info['maxOutputChannels']}")
                print(f"  Default Sample Rate: {dev_info['defaultSampleRate']}")
            
            # Setup input stream (microphone)
            self.input_stream = self.pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=INPUT_SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            print("Input stream setup complete")
            
            # Setup output stream (speakers)
            self.output_stream = self.pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=OUTPUT_SAMPLE_RATE,
                output=True
            )
            print("Output stream setup complete")
            
            # Test audio playback
            print("Testing audio playback...")
            try:
                with wave.open('test_tone.wav', 'rb') as wf:
                    data = wf.readframes(wf.getnframes())
                    self.output_stream.write(data)
                print("Test audio playback completed successfully")
            except Exception as e:
                print(f"Error during test audio playback: {e}")
                
        except Exception as e:
            print(f"Error setting up audio streams: {e}")
            import traceback
            traceback.print_exc()
            raise
            
    def record_audio(self, duration=5):
        """Record audio from the microphone"""
        print("Recording... (Speak now)")
        frames = []
        
        # Calculate how many chunks to read based on duration
        num_chunks = int((INPUT_SAMPLE_RATE / CHUNK_SIZE) * duration)
        
        for _ in range(num_chunks):
            data = self.input_stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
            
        print("Recording complete")
        
        # Save the recorded audio to a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav_filename = temp_file.name
            
        # Write the WAV file
        with wave.open(temp_wav_filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 2 bytes for FORMAT = paInt16
            wf.setframerate(INPUT_SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
            
        return temp_wav_filename
    
    def audio_to_text(self, audio_file_path):
        """Convert audio to text using Replicate's Whisper model"""
        try:
            print(f"Converting audio to text using Replicate Whisper model...")
            
            # Set the API token for Replicate
            os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
            
            # Run Whisper model on the audio file
            input_data = {
                "audio": open(audio_file_path, "rb")
            }
            
            output = replicate.run(
                "openai/whisper:8099696689d249cf8b122d833c36ac3f75505c666a395ca40ef26f68e7d3d16e",
                input=input_data
            )
            
            # Extract the transcribed text from the output
            if output and "text" in output:
                transcribed_text = output["text"]
                return transcribed_text
            else:
                # If transcription has segments, extract text from all segments
                if output and "segments" in output and len(output["segments"]) > 0:
                    transcribed_text = " ".join([segment["text"] for segment in output["segments"]])
                    return transcribed_text.strip()
                    
            print("No text detected in the audio")
            return None
            
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Clean up the temporary file
            try:
                os.unlink(audio_file_path)
            except:
                pass
    
    def close(self):
        """Close audio streams"""
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            
        if self.pa:
            self.pa.terminate()