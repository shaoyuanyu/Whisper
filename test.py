import soundfile as sf
import librosa
import numpy as np

audio1, sr1 = sf.read("C://Projects/Whisper/00ac2a6e-7e4e-4793-acaa-24f21b06627c.wav")
audio2, sr2 = sf.read("C://Projects/Whisper/3d0bb967-551f-427f-ac23-fe3c1d1e0a09.wav")
audio3, sr3 = sf.read("C://Projects/Whisper/3d0ea4ea-e4d2-47ff-9c7a-d5a23907c7e9.wav")

print(len(audio1), len(audio2), len(audio3))
