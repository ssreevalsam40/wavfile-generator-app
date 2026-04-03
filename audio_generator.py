import os
import datetime
from typing import Optional
from google.cloud import texttospeech as tts
from google.cloud import storage


class AudioGenerator:
    """Handles multi-speaker TTS synthesis and Cloud Storage integration."""

    def __init__(self, project_id: str, bucket_name: str, credentials: Optional[any] = None):
        """Initializes TTS and Storage clients with optional credentials."""
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.tts_client = tts.TextToSpeechClient(credentials=credentials)
        self.storage_client = storage.Client(project=project_id, credentials=credentials)

    def _convert_to_ssml(self, script: str) -> str:
        """Converts a script with speaker tags to SSML format."""
        ssml = "<speak>"
        lines = script.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '[Agent]:' in line:
                # Agent voice: en-AU-Neural2-A (Female)
                content = line.replace('[Agent]:', '').strip()
                ssml += f'<voice name="en-AU-Neural2-A">{content}</voice><break time="800ms"/>'
            elif '[Customer]:' in line:
                # Customer voice: en-AU-Neural2-B (Male)
                content = line.replace('[Customer]:', '').strip()
                ssml += f'<voice name="en-AU-Neural2-B">{content}</voice><break time="800ms"/>'
            else:
                # Default case for lines without explicit speaker tags
                ssml += f' {line} <break time="800ms"/>'
        
        ssml += "</speak>"
        return ssml

    def synthesise_audio(self, script: str) -> str:
        """Synthesises multi-speaker audio and returns the local file path."""
        ssml = self._convert_to_ssml(script)
        synthesis_input = tts.SynthesisInput(ssml=ssml)
        
        # Note: We set a base voice, but SSML <voice> tags perform speaker switching
        voice = tts.VoiceSelectionParams(
            language_code="en-AU",
            name="en-AU-Neural2-A"
        )
        
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )

        import wave
        import io

        # Google Cloud TTS returns mono (1 channel)
        # We convert it to 2-channel (stereo) by duplicating the samples
        with io.BytesIO(response.audio_content) as mono_io:
            with wave.open(mono_io, 'rb') as mono_wav:
                params = mono_wav.getparams()
                sample_width = mono_wav.getsampwidth()
                frame_rate = mono_wav.getframerate()
                n_frames = mono_wav.getnframes()
                mono_data = mono_wav.readframes(n_frames)

        # Create temporary file for stereo output
        filename = f"dialogue_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        filepath = os.path.join(os.getcwd(), filename)
        
        with wave.open(filepath, 'wb') as stereo_wav:
            # Set to 2 channels
            stereo_wav.setnchannels(2)
            stereo_wav.setsampwidth(sample_width)
            stereo_wav.setframerate(frame_rate)
            
            # Duplicate the mono data to create stereo (interleaved samples)
            # This is a naive but effective way for identical channels
            if sample_width == 2:  # Assuming 16-bit PCM (LINEAR16)
                import struct
                # Unpack short integers, duplicate, and pack back
                fmt = f"<{n_frames}h"
                samples = struct.unpack(fmt, mono_data)
                stereo_samples = []
                for s in samples:
                    stereo_samples.extend([s, s])
                
                stereo_data = struct.pack(f"<{2*n_frames}h", *stereo_samples)
                stereo_wav.writeframes(stereo_data)
            else:
                # Fallback for other bit depths (less common with LINEAR16)
                stereo_wav.writeframes(mono_data) 
            
        return filepath

    def upload_and_sign(self, filepath: str) -> str:
        """Uploads file to GCS and generates a V4 signed URL."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob_name = os.path.basename(filepath)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_filename(filepath)
        
        # Generate V4 Signed URL (valid for 1 hour)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=60),
            method="GET"
        )
        
        # Clean up local file after upload
        if os.path.exists(filepath):
            os.remove(filepath)
            
        return url


def example_audio_generation(project_id: str, bucket_name: str, script: str, credentials: Optional[any] = None):
    """Example function to demonstrate AudioGenerator functionality."""
    generator = AudioGenerator(project_id=project_id, bucket_name=bucket_name, credentials=credentials)
    filepath = generator.synthesise_audio(script)
    signed_url = generator.upload_and_sign(filepath)
    print(f"Signed URL: {signed_url}")
    return signed_url
