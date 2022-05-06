#https://en.wikipedia.org/wiki/SHA-2, replicated using the pseudocode from SHA256
#https://qvault.io/cryptography/how-sha-2-works-step-by-step-sha-256/

h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
#first 32 bits of the fractional parts of the square roots of the first 8 primes in hex rep


k =[0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
   0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
   0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
   0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
   0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
   0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
   0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
   0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
#first 32 bits of the fractional parts of the cube roots of the first 64 primes in hex rep


def NOT(x):         return ['0' if x_i=='1' else '1' for x_i in x]

def xor(x, y):      return '0' if x==y else '1'

def XOR(arr1, arr2): return [xor(x_i, y_i) for x_i, y_i in zip(arr1, arr2)]

def AND(arr1, arr2):               
    return ['1' if x_i == y_i and x_i == '1' else '0' for x_i, y_i in zip(arr1, arr2)]

def rrot(arr, n):
    return arr[-n:] + arr[:-n] #this right rotates the array by a specified number n

def rshift(arr, n):
    return n*['0'] + arr[:-n] #this right shifts the array appending 0's on the start

def add(arr1, arr2):
    c = '0' #carry
    arr = list(range(32))
    for i in range(31, -1, -1): #goes through the arrays right to left
        arr[i] = xor(xor(arr1[i], arr2[i]), c)
        if arr1[i] == arr2[i]:
            c = arr1[i]
    return arr


def SHA(input):
    K = []
    for i in range(len(k)):
        K.append(list(bin(k[i])[2:].zfill(32)))

    H = []
    for i in range(len(h)):
        H.append(list(bin(h[i])[2:].zfill(32)))
    #those turn them into binary in 2D arrarys    
    PreHash_bits = str(''.join(format(ord(i), '08b') for i in input))
    No_of_0 = (447 - len(PreHash_bits))%512  #this adds a padding that turns the message into 512 bit chunks
    PreHash_bits += '1'
    PreHash_bits += No_of_0*'0'
    PreHash_bits += str(''.join(format((len(input)*8), '064b')))

    n = int(len(PreHash_bits)/512)
    count = 0

    for chunk in range(n):
        W = [32*['0'] for j in range(64)]
        for row in range(16):
            for column in range(32):
                W[row][column] = PreHash_bits[count]
                count += 1
        for i in range(16, 64):
            S0 = XOR(XOR(rrot(W[i-15], 7), rrot(W[i-15], 18)), rshift(W[i-15], 3))
            S1 = XOR(XOR(rrot(W[i- 2], 17), rrot(W[i- 2], 19)), rshift(W[i- 2], 10))
            W[i] = add(add(add(W[i-16], S0), W[i-7]), S1)

        a, b, c, d, e, f, g, q = H
        

        for j in range(64):
            S1 = XOR(XOR(rrot(e, 6), rrot(e, 11)), rrot(e, 25))
            ch = XOR(AND(e, f), AND(NOT(e), g))
            temp1 = add(add(add(add(q, W[j]), ch), S1), K[j])
            S0 = XOR(XOR(rrot(a, 2), rrot(a, 13)), rrot(a, 22))
            maj = XOR(XOR(AND(a, b), AND(a, c)), AND(b, c))
            temp2 = add(S0, maj)
            q = g
            g = f
            f = e
            e = add(d, temp1)
            d = c
            c = b
            b = a
            a = add(temp1, temp2)
        H[0] = add(H[0], a)
        H[1] = add(H[1], b)
        H[2] = add(H[2], c)
        H[3] = add(H[3], d)
        H[4] = add(H[4], e)
        H[5] = add(H[5], f)
        H[6] = add(H[6], g)
        H[7] = add(H[7], q)
    
    array_to_bits(H)

    output = ''
    for row in arrays_to_hex(H):
        output += row
    return output
    
def array_to_bits(digest):
    for i, row in enumerate(digest):
        for j, k in enumerate(row):
            if digest[i][j] == '0':
                digest[i][j] = 0
            else:
                digest[i][j] = 1
                
def arrays_to_hex(arrs):
    return ('{:x}'.format(sum([x * 2**a for a, x in enumerate(arr[::-1])])) for arr in arrs)