# AES Analysis

This project is intended to analyze the AES encryption algorithm. Specifically, a novel-o-classic method will be implemented to analyze the relation between the "key" and "plain text" to that of "encrypted sequence".

## Description 1

### TODO:

Following sees the block analysis operation.

```
-> choose a plain text 128-byte long, P
-> take a random key 128-byte long, k
-> encrypt the plain text with key, E
-> for each bit in key, k:
	-> flip the bit to generate, k'
	-> encrypt plain text with key, k' to give E'
	-> find hamming distance between E and E'
-> create a histogram of the hamming distance measured
```

