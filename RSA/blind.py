from fractions import gcd
from random import randrange, random
from collections import namedtuple
from math import log
from binascii import hexlify, unhexlify

def is_prime(n, k=30):
    if n <= 3:
        return n == 2 or n == 3
    neg_one = n - 1

    s, d = 0, neg_one
    while not d & 1:
        s, d = s+1, d>>1
    assert 2 ** s * d == neg_one and d & 1

    for i in xrange(k):
        a = randrange(2, neg_one)
        x = pow(a, d, n)
        if x in (1, neg_one):
            continue
        for r in xrange(1, s):
            x = x ** 2 % n
            if x == 1:
                return False
            if x == neg_one:
                break
        else:
            return False
    return True

def randprime(N=10**8):
    p = 1
    while not is_prime(p):
        p = randrange(N)
    return p

def multinv(modulus, value):
    x, lastx = 0, 1
    a, b = modulus, value
    while b:
        a, q, b = b, a // b, a % b
        x, lastx = lastx - q * x, x
    result = (1 - lastx * modulus) // value
    if result < 0:
        result += modulus
    assert 0 <= result < modulus and value * result % modulus == 1
    return result

KeyPair = namedtuple('KeyPair', 'public private')
Key = namedtuple('Key', 'exponent modulus')

def keygen(N, public=None):
    prime1 = randprime(N)
    prime2 = randprime(N)
    composite = prime1 * prime2
    totient = (prime1 - 1) * (prime2 - 1)
    if public is None:
        while True:
            private = randrange(totient)
            if gcd(private, totient) == 1:
                break
        public = multinv(totient, private)
    else:
        private = multinv(totient, public)
    assert public * private % totient == gcd(public, totient) == gcd(private, totient) == 1
    assert pow(pow(1234567, public, composite), private, composite) == 1234567
    return KeyPair(Key(public, composite), Key(private, composite))

def signature(msg, privkey):
    f=open('signedfile','w')
    coded = pow(int(msg), *privkey)% privkey[1]
    print "Blinded Signed Message "+str(coded)
    f.write(str(coded))

def blindingfactor(N):
    b=random()*(N-1)
    r=int(b)
    while (gcd(r,N)!=1):
        r=r+1
    return r

def blind(msg,pubkey):
    f=open('blindmsg','w')
    r=blindingfactor(pubkey[1])
    m=int(msg)
    blindmsg=(pow(r,*pubkey)*m)% pubkey[1]
    print "Blinded Message "+str(blindmsg)
    f.write(str(blindmsg))
    return r

def unblind(msg,r,pubkey):
	f=open('unblindsigned','w')
	bsm=int(msg)
	ubsm=(bsm*multinv(pubkey[1],r))% pubkey[1]
	print "Unblinded Signed Message "+str(ubsm)
	f.write(str(ubsm))

def verefy(msg,r,pubkey):
    print "Message After Verification "+str(pow(int(msg),*pubkey)%pubkey[1])

if __name__ == '__main__':
    
    # bob wants to send msg after blinding it
    f=open('msg')
    pubkey, privkey = keygen(2 ** 128)
    msg=f.read()
    msg=msg.rstrip()
    print "Original Message "+str(msg)
    r=blind(msg,pubkey)

    #Alice receives the blind message and signs it
    bf=open('blindmsg')
    m=bf.read()
    signature(m, privkey)

    #Bob recieves the signed message and unblinds it
    h=open('signedfile')
    signedmsg=h.read()
    unblind(signedmsg,r,pubkey)
    
    #verifier verefis the message
    i=open('unblindsigned')
    ubsignedmsg=i.read()
    verefy(ubsignedmsg,r,pubkey)

    '''print('-' * 20)
    print(msg)
    print(r)
    print('-'*20)
    a=5
    b=a*pow(19,11) % 77
    c=pow(b,11)%77
    print c
    d=(c*73) % 77
    print d
    print pow(d,11)%77 '''
