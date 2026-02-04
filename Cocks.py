import random,hashlib

small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
                43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109,
                113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191,
                193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269,
                271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353,
                359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439,
                443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523,
                541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617,
                619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709,
                719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
                821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907,
                911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

def is_prime(num):
    if num < 2:
        return False
    for prime in small_primes:
        if num % prime == 0:
            return False
    return miller_rabin(num)

def miller_rabin(num):
    s = num - 1
    t = 0
    while not s & 1:
        s >>= 1
        t += 1
    for _ in range(5):
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = v * v % num
    return True

def generate_prime(bits):
    while True:
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 3
        if is_prime(num):
            return num

def mod_inverse(a, n):
    lm, low, hm, high = 1, a % n, 0, n
    while low > 1:
        r = high // low
        lm, low, hm, high = hm - lm * r, high - low * r, lm, low
    return lm % n

def jacobi(a, n):
    a = a % n
    result = 1
    while a != 0:
        while a & 1 == 0:
            a >>= 1
            if n & 7 in (3, 5):
                result = -result
        a, n = n, a
        if a & 3 == 3 and n & 3 == 3:
            result = -result
        a = a % n
    return result if n == 1 else 0

def setup(bits=1024):
    p = generate_prime(bits//2)
    q = generate_prime(bits//2)
    n = p*q
    return (p,q),n

def ID2int(ID,n):
    ab = hashlib.sha256(ID).digest()
    while jacobi(int.from_bytes(ab,'little') % n,n) != 1:
        ab = hashlib.sha256(ab).digest()
    a = int.from_bytes(ab,'little') % n
    return a

def extract(ID,msk):
    p,q = msk
    n = p*q
    a = ID2int(ID,n)
    r = pow(a,(n+5-p-q)//8,n)
    return r

def encrypt(m,ID,mpk):
    n = mpk
    a = ID2int(ID,n)
    if m == 0:
        m = -1
    t1 = random.randint(2,n)
    while jacobi(t1,n) != m:
        t1 = random.randint(2,n)
    t2 = random.randint(2,n)
    while jacobi(t2,n) != m or t1 == t2:
        t2 = random.randint(2,n)
    c1 = (t1 + a*mod_inverse(t1,n)) % n
    c2 = (t2 - a*mod_inverse(t2,n)) % n
    return (c1,c2)

def decrypt(c,usk,ID,mpk):
    r = usk
    n = mpk
    c1,c2 = c
    a = ID2int(ID,n)
    alpha = c1 + 2*r if pow(r,2,n) == a else c2 + 2*r
    m = jacobi(alpha,n)
    if m == -1:
        m = 0
    return m

if __name__ == '__main__':
    message = [1,0,1,0,1,0,1,0]
    ID = b'Alice'
    msk,mpk = setup()
    usk = extract(ID,msk)
    cipher = []
    for m in message:
        c = encrypt(m,ID,mpk)
        cipher.append(c)
    message_prime = []
    for c in cipher:
        mp = decrypt(c,usk,ID,mpk)
        message_prime.append(mp)
    assert message == message_prime
