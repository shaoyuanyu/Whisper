# 导入需要的模块
import soundfile as sf
import numpy as np
import librosa
import os
from random import randint
from time import sleep
import logging

def culSr(a, b, sr_a, sr_b):
	# 检查两个音频的采样率是否相同，如果不同，需要进行重采样
	if sr_a != sr_b:
		# 选择较高的采样率作为目标采样率
		sr = max(sr_a, sr_b)
		# 对较低的采样率的音频进行重采样
		if sr_a < sr_b:
			print("resample noise from " + str(sr_a) + " to " + str(sr) + "...")
			a = librosa.resample(a, orig_sr=sr_a, target_sr=sr)
		else:
			print("resample noise from " + str(sr_b) + " to " + str(sr) + "...")
			b = librosa.resample(b, orig_sr=sr_b, target_sr=sr)
	else:
		# 如果两个音频的采样率相同，直接使用
		sr = sr_a
	return a, b, sr

# 定义一个函数，用于将两个单通道音轨合并成双通道，并返回新的数据和参数
def mergeAudio(array1, array2):
    # 检查两个数组的长度是否相同，如果不同，则无法合并
    if len(array1) != len(array2):
        raise("两个音轨的长度不同，无法合并")
	
    # 将两个数组堆叠成一个二维数组，表示左右声道
    array3 = np.stack((array1, array2), axis=1)

    return array3

def mixAudio(noise, clean, sr_noise, sr_clean):
	# 采样率统一
	noise, clean, sr_output = culSr(noise, clean, sr_noise, sr_clean)
	print(sr_output)
	
	# 音频叠加
	noise_len = len(noise)
	clean_len = len(clean)
	if noise_len < clean_len:
		# 计算需要重复的次数和余数
		times, remainder = divmod(clean_len, noise_len)

		print("叠加noise音源 " + str(times) + " 次，余" + str(remainder))

		# 重复叠加数组1，直到长度等于或超过数组2
		noise = np.concatenate((np.tile(noise, times), noise[0:remainder]))
	elif noise_len > clean_len:
		print("裁切noise音源")
		noise = noise[0:clean_len]
	
	# clean单声道变双声道
	clean_shape = np.shape(clean)
	if len(clean_shape) == 1:
		#单通道
		clean = mergeAudio(clean, clean)
	elif len(clean_shape) == 2 and clean_shape[1] == 2:
		# 双通道
		pass
	else:
		raise("clean音源通道数出错")
	
	# 叠加
	output = np.clip(noise+clean, -32768, 32767)

	return output, sr_output

def mixNoise(noise_path, clean_path, save_path):

	# 创建log
	mylogger = logging.getLogger('mylogger')
	mylogger.setLevel(logging.DEBUG)
	file_handler = logging.FileHandler('logfile.log', mode='w', encoding='utf-8')
	file_handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	mylogger.addHandler(file_handler)

	# 加载noise音源
	print("loading noises")
	noise_files = os.listdir(noise_path)
	noises = []
	sr_noises = []
	for noise_file in noise_files:
		n, sr_n = sf.read(noise_path + "/" + noise_file)
		print(noise_file, sr_n)
		noises.append(n)
		sr_noises.append(sr_n)
	print("一共" + str(len(noises)) + "段noise音频")

	print()
	print("loading cleans")
	clean_files = os.walk(clean_path)
	for (dir_path, dir_names, file_names) in clean_files:
		# 路劲规范化
		dir_path = dir_path.replace("\\", "/")
		for i, file_name in enumerate(file_names):
			if i%10 == 0:
				sleep(0.5)
			print()
			print("进度: ", str(i) + "/" + str(len(file_names)))
			# 读取clean音源
			clean, sr_clean = sf.read(dir_path + "/" + file_name)
			print(dir_path + "/" + file_name, sr_clean)

			# 随机选择noise音源
			random_noise_index = randint(0, len(noises)-1)
			noise = noises[random_noise_index]
			sr_noise = sr_noises[random_noise_index]

			# 混合noise和clean音源
			try:
				output, sr_output = mixAudio(noise, clean, sr_noise, sr_clean)
			except Exception as e:
				print("叠加错误: ", dir_path + "/" + file_name)
				mylogger.debug("叠加错误: " + dir_path + "/" + file_name + " - " + str(e))
				continue

			print("clean path: ", clean_path)
			print("save path:", save_path + dir_path.replace(clean_path, "") + "/" + file_name)
			try:
				sf.write(save_path + dir_path.replace(clean_path, "") + "/" + file_name, output, sr_output)
			except:
				try:
					os.makedirs(save_path + dir_path.replace(clean_path, ""))
					sf.write(save_path + dir_path.replace(clean_path, "") + "/" + file_name, output, sr_output)
				except:
					raise

def singleAudioChannel(array2):
	array_l = array2[:, 0]
	array_r = array2[:, 1]

	# 左右声道平均
	array = np.average([array_l, array_r], axis=0)

	return array

def dbAjust(db):
	print("adjusting audios to" + str(db) + "db...")

	noise_path = "C://Projects/Whisper/train_data/noise/dormitory"
	noise_files = os.listdir(noise_path)

	for noise_file in noise_files:
		noise, sr = sf.read(noise_path + '/' + noise_file)

		noise = singleAudioChannel(noise)

		avg_db = np.mean(librosa.amplitude_to_db(np.abs(noise)))
		factor = 10 ** ((db - avg_db) / 20)
		print(noise_file, avg_db, factor)

		noise_adjusted = noise * factor

		sf.write("C://Projects/Whisper/train_data/noise/dormitory_adjusted" + '/' + str(db) + 'db/' + noise_file, noise_adjusted, sr)
	
	print("adjusting finished\n")

def main():
	dbAjust(-50)
	dbAjust(-40)
	dbAjust(-30)
	dbAjust(-20)
	# mixNoise("C://Projects/Whisper/train_data/noise/dormitory_adjusted/-40db", "C://Projects/Whisper/train_data/primewords_md_2018_set1/audio_files", "C://Projects/Whisper/train_data/noised_primewords_md_2018_set1")

if __name__ == '__main__':
	main()