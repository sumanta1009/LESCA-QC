import hashlib
import secrets
import struct
import base64
import random
import string
import sys

# Constants
H = 32
# H = 16
DELTA = 64              
WORD_PRECISION = 64
# k = 1

def modified_ksa(key):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    return [x % H for x in s[:H]]


# XORShift64 PRNG
def xorshift64(seed):
    # Xorshift PRNG for 64-bit integers
    x = seed
    x ^= (x >> 12) #& 0xFFFFFFFFFFFFFFFF
    x ^= (x << 25) #& 0xFFFFFFFFFFFFFFFF
    x ^= (x >> 27) #& 0xFFFFFFFFFFFFFFFF
    return x


# Right rotation
def ror64(x, n):
    # Rotate right (circular right shift) for 64-bit integers
    return ((x >> n) | (x << (64 - n))) & 0xFFFFFFFFFFFFFFFF


# Right shift
def simon_r(x, y, z):
    return (x & y) ^ z # (vj and vj of pi1) xor vj of pi2


def setup_key(key):
    hashed_key = hashlib.sha512(key).digest()
    kp1 = hashed_key[:12]  #12 bytes
    kp2 = hashed_key[12:24]  # 12 bytes
    kp3 = hashed_key[24:36]  # 12 bytes
    kp4 = hashed_key[36:48]  # 12 bytes
    ks = hashed_key[48:64]  # 16 bytes
    pi1 = modified_ksa(kp1)
    pi2 = modified_ksa(kp2)
    pi3 = modified_ksa(kp3)
    pi4 = modified_ksa(kp4)
    seed = int.from_bytes(ks[:16], 'little')
    return pi1, pi2, pi3, pi4, seed


def update_primitives(v, pi1, pi2, pi3, pi4):
    new_v = []
    for t in range(H):
        if pi1[t] < len(v) and pi2[t] < len(v):
            new_v.append(simon_r(v[t],v[pi1[t]], v[pi2[t]]))
        else:
            raise IndexError(f"Index out of range in pi1 or pi2 at t={t} with pi1[t]={pi1[t]} and pi2[t]={pi2[t]}")
    new_pi1 = [pi3[i % H] for i in range(H)]
    new_pi2 = [pi4[i % H] for i in range(H)]
    new_pi3 = [pi4[pi3[i % H]] for i in range(H)]
    return new_v, new_pi1, new_pi2, new_pi3


def encrypt(plaintext, key):
    k = 1
    pi1, pi2, pi3, pi4, seed = setup_key(key)
    blocks = [plaintext[i:i+H*8] for i in range(0, len(plaintext), H*8)]
    ciphertext = b''
    keystream = []
    v = [0 for _ in range(H)]
    for i, block in enumerate(blocks):
        if i % DELTA == 0:
            v, pi1, pi2, pi3 = update_primitives(v, pi1, pi2, pi3, pi4)
        if i==0:
            v = []
            for _ in range(H):
                seed = xorshift64(seed)  # Update seed
                v.append(seed)
        x = []
        for w in range(H):
            value = v[w] ^ v[pi1[w]] ^ v[pi2[w]]
            x.append(value)

        v = [xorshift64(x[w]) for w in range(H)]
        v = [ror64(v[w], pi1[w]) for w in range(H)]        
        block = struct.unpack(f'{H}Q', block)        
        ciphertext += struct.pack(f'{H}Q', *[block[w] ^ v[w] for w in range(H)])
        keystream.append(v)    
    return ciphertext, keystream

characters = string.ascii_letters
# p = ''.join(random.choice(characters) for _ in range(10240))  ## uncomment the line and comment out the next line for generating random plaintext
p="The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, the grammar of the resulting language is more simple and regular than that of the individual languages. The new common language will be more simple and regular than the existing European languages. It will be as simple as Occidental; in fact, it will be Occidental. To an English person, it will seem like simplified English, as a skeptical Cambridge friend of mine told me what Occidental is. The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words. Everyone realizes why a new common language would be desirable: one could refuse to pay expensive translators. To achieve this, it would be necessary to have uniform grammar, pronunciation and more common words. If several languages coalesce, th"
k="if0IkJnlZ3IyKZMNLjyUnQSIcmKqkePc"
key=k.encode('utf-8')
plaintext=p.encode('utf-8')
ciphertext, keystream = encrypt(plaintext, key)

with open("test_case1.txt", "ab") as f: # A file named 'test_case.txt' will be created (if not already) in 'append binary' mode
    f.write(b'PLAINTEXT : ' + repr(plaintext).encode() + b'\n')
    f.write(b'\n\n\n\n\n')

    f.write(b'KEY : ' + repr(key).encode() + b'\n')
    f.write(b'\n\n\n\n\n')

    f.write(b'CIPHERTEXT : ' + repr(ciphertext).encode() + b'\n')
    f.write(b'\n\n\n\n\n')
    