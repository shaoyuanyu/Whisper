import librosa
import soundfile

# 加载音频文件
audio, sr = librosa.load('./test_data/wei.wav', sr=None)

# 降低采样率
audio_resampled = librosa.resample(audio, orig_sr=sr, target_sr=16000)

# 保存音频文件
#librosa.output.write_wav('./test_data/wei16.wav', y=audio_resampled, sr=16000)
soundfile.write('./test_data/wei16.wav', audio_resampled, 16000)
