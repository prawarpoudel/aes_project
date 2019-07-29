import os
import io
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

def operate():
	# define key as some 128-bit data
	key = b'This is my key!!'
	my_plain_text = b"is my Plain text"

	# ECB because no dependency required
	cipher = AES.new(key,AES.MODE_ECB)
	my_cipher = cipher.encrypt(my_plain_text)
	
	print(f"Input Plain Text: {my_plain_text}\n\t\tgives cipher:{my_cipher} using key {key}")
	cipher2 = AES.new(key,AES.MODE_ECB)
	my_dec_bytes = cipher2.decrypt(my_cipher)
	# my_dec = "".join(map(chr, my_dec_bytes))
	print(f"\t\t.. decrypting gives {my_dec_bytes}")
	print(f"\t\t.. hamming distance here is {hamming_distance(my_dec_bytes,my_plain_text)}")


	ch_bit_list = create_ch_bits()

	# change some bits in key and evaluate difference in the cipher generated
	for ch_bits in ch_bit_list:
		hw_1 = list()
		key_int = int.from_bytes(key,"big")
		if debug:
			print(f".. key_int = 0x{hex(key_int)}")

		for i in range(128):
			# flip one bit in key,
			# .. generate byte type again 16-byte wide
			key_ = (key_int^(circular_left_shift(ch_bits,i,128))).to_bytes(16,"big")
			# create a new cipher object
			cipher = AES.new(key_,AES.MODE_ECB)
			# encrypt ECB again
			my_plain_inner = cipher.decrypt(my_cipher)
			hw_1.append(hamming_distance(my_plain_text,my_plain_inner))
			if debug:
				my_dec = "".join(map(chr, my_plain_inner))
				print(f"InnerCipher={my_dec}")

		plt.figure(0)
		plt.hist(hw_1)
		plt.xlim(0,128)
		plt.ylim(0,128)
		
	png1 = io.BytesIO()
	plt.savefig(png1,format="png")
	png2 = Image.open(png1)

	if (not os.path.isdir(os.path.join("..","Images"))) or (not os.path.isdir(os.path.join("..","Images","exp3"))):
		os.makedirs(os.path.join("..","Images","exp3"))
	# image_output_name = os.path.join("..","Images",str(ch_bits)+"_histogram.tiff")
	# change the following to .tiff if needed
	image_output_name = os.path.join("..","Images","exp3","overall_histogram.png")	
	if debug:
		print(f".. saving as {image_output_name}")
	png2.save(image_output_name)
	png1.close()
	png2.close()

if __name__=="__main__":
	operate()