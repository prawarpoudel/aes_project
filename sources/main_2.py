import os
import io
import sys
import random
from PIL import Image
from Crypto.Cipher import AES
import matplotlib.pyplot as plt 

debug = False

def find_ones(number):
	'''
	This function takes in a number and returns the number of set bits in that number
	'''
	count = 0
	while number:
		number &= number-1
		count+=1
	return count

def hamming_distance(ref_cipher,new_cipher):
	'''
	This function returns the number of different bits in two numbers
	'''
	int_ref = int.from_bytes(ref_cipher,"big") 
	int_new = int.from_bytes(new_cipher,"big") 

	dif = int_new^int_ref;
	return find_ones(dif)

def create_ch_bits():
	# This section populates the list which is used to determine the 
	# .. change in bits
	ch_bit_list = list()
	for num_bits in range(1,(int)(128//2)+1,1):
		ch_bits = 1
		for b_idx in range(num_bits,1,-1):
			ch_bits = (ch_bits*10)+1
		ch_bit_list.append(ch_bits)
	return ch_bit_list

def circular_left_shift(in_number,position,length):
	'''
	Input: a number
	Does: circular left shit the 'number' by 'position' bits
	Output: a number
	'''
	part_1 = in_number<<position
	part_2 = in_number>>(length-position)
	return (part_1|part_2)&0xffffffffffffffffffffffffffffffff

def generate_IV():
	# 128 bit random number
	# .. let us not worry about seed
	myNum = random.randint(1,0xffffffffffffffffffffffffffffffff)
	return myNum.to_bytes(16,"big")

def aes_encrypt(key,file_name,iv,num_bits=16*8):
	'''
	Perform AES encryption of 'file_name' in AES CBC mode with iv
	The block size is 128 bit. key used is 'key'
	'''
	my_enc_list = list()
	aes_engine = AES.new(key,AES.MODE_CBC,iv=iv)

	with open(file_name,'rb') as in_file:
		while True:
			in_chunk = in_file.read(num_bits)
			if len(in_chunk)==0:
				if debug:
					print(f".. file read finished")
				break
			elif len(in_chunk)%16:
				in_chunk += b' '*(16-len(in_chunk)%16)
			my_enc_list.append(aes_engine.encrypt(in_chunk))

	return my_enc_list

def operate(infile):
	if not os.path.isfile(infile):
		print(f"Input image file \"{infile}\" does not exist")
		print(f".. program exiting")
		return

	# define key as some 128-bit data
	key = b'This is my key!!'
	IV = generate_IV()

	return_dict = {}

	my_original_cipher = aes_encrypt(key,infile,IV,128)
	my_chipher_list = list()

	ch_bit_list = create_ch_bits()

	# change some bits in key and evaluate difference in the cipher generated
	for ch_bits in ch_bit_list:		
		key_int = int.from_bytes(key,"big")

		for i in range(128):
			# flip one bit in key,
			# .. generate byte type again 16-byte wide
			key_ = (key_int^(circular_left_shift(ch_bits,i,128))).to_bytes(16,"big")
			# obtain cipher on new key
			my_chipher_list.append(aes_encrypt(key_,infile,IV))

	return_dict['reference'] = my_original_cipher
	return_dict['others'] = my_chipher_list
	return return_dict

def analyze_hist(dict_cipher):
	ref_cipher = dict_cipher["reference"]
	other_cipher = dict_cipher["others"]

	hist_list = list()

	output_dir_name = os.path.join("..","Images","exp2")
	if not os.path.isdir(output_dir_name):
		os.mkdirs(output_dir_name)

	# for every cipher created using all the keys changed
	for comp_cipher in other_cipher:
		temp_list = list()
		for idx,each_block in enumerate(ref_cipher):
			comp_cipher_block = comp_cipher[idx]
			temp_list.append(hamming_distance(each_block,comp_cipher_block))

			plt.hist(temp_list)
			plt.title(f"Histogram {idx} idx")
			plt.xlim(0,128)
			plt.ylim(0,128)
			
			png1 = io.BytesIO()
			plt.savefig(png1,format="png")
			png2 = Image.open(png1)

			image_output_name = os.path.join(output_dir_name,f"hist_{idx}.tiff")
			png2.save(image_output_name)
			png1.close()
			png2.close()
			plt.close("all")
		hist_list.append(temp_list)

	for each_list in hist_list:
		plt.hist(temp_list)
		plt.title(f"Histogram Id idx")
		plt.xlim(0,128)
		plt.ylim(0,128)
		
	plt.savefig("hist_overall.png")
	plt.close("all")

def main(input_image_name="overall_histogram.png"):
	input_image = os.path.join("..","Images","exp1",input_image_name)
	print(f"Provided input image name is {input_image}")
	cipher_dict = operate(input_image)

	analyze_hist(cipher_dict)

if __name__=="__main__":
	if len(sys.argv)>1:
		main(str(sys.argv[1]))
	else:
		main()