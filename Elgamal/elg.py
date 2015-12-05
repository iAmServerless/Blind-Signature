from fractions import gcd
from random import randrange, random
from collections import namedtuple
from math import log
from binascii import hexlify, unhexlify

def is_prime(n, k=30):
    # http://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test
    if n <= 3:
        return n == 2 or n == 3
    neg_one = n - 1

    # write n-1 as 2^s*d where d is odd
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

def findelement(prime):
	element=random()*(prime-1)	
	b=int(element)
	return b

def keygen(N, public=None):
	prime=randprime(N)
	x=findelement(prime)
	alpha=findelement(prime)
	y=pow(alpha,x,prime)
	return (x,prime),(y,alpha,prime)

def findrandom(prime):
	k=randrange(1,prime-1)
	while(gcd(k,prime-1)!=1):
		k=k+1
	return k

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

def blind(pubkey):
	k=findrandom(pubkey[2])
	r=pow(pubkey[1],k,pubkey[2])
	#h is blinding factor
	h=findrandom(pubkey[2])
	f=open('msg')
	msg=f.read()
	msg=msg.rstrip()
	print "Real Message " + msg
	m=int(msg)
	mdash=(h*m) % (pubkey[2]-1)
	g=open('blindmsg','w')
	g.write(str(mdash))
	return k,r,h,mdash

def signature(privkey,k,r):
	f=open('blindmsg')
	msg=f.read()
	print "Blinded Message "+msg
	mdash=int(msg)
	sdash=((mdash-privkey[0]*r)*multinv(privkey[1]-1,k)) % (privkey[1]-1)
	g=open('signedblindmsg','w')
	g.write(str(sdash))

def unblind(pubkey,k,r,h,mdash):
	f=open('signedblindmsg')
	g=open('signedmsg','w')
	msg=f.read()
	print "Signed Blinded Message "+ msg
	sdash=int(msg)
	#ks=(multinv(privkey[1]-1,h)*(privkey[0]*r+k*sdash)-privkey[0]*r)% (privkey[1]-1)
	#s=multinv(privkey[1]-1,k)*ks%(privkey[1]-1)
	s=((multinv(pubkey[2]-1,h)-1)*mdash*multinv(pubkey[2]-1,k)+sdash)% (pubkey[2]-1)
    #s=(privkey[0]*r*multinv(privkey[1],k)*(multinv(privkey[1],h)-1)+(multinv(privkey[1],h)*sdash))%(privkey[1]-1)
	#print (privkey[0]*r+k*s) % (privkey[1]-1)
	g.write(str(s))
	print "Real Signed Message "+str(s)

def verefy(pubkey,r):
	f=open('msg')
	g=open('signedmsg')
	m=int(f.read())
	s=int(g.read())
	a=pow(pubkey[1],m,pubkey[2])
	b=(pow(pubkey[0],r,pubkey[2])*pow(r,s,pubkey[2]))%pubkey[2]
	print a
	print b
if __name__ == '__main__':
	privkey, pubkey = keygen(2**64)
   	#Bob should do the following
	k,r,h,mdash=blind(pubkey)
	
	#Alice (Signer) will do the following
	signature(privkey,k,r)

	#Bob receives the blinded signed message and unblinds it
	unblind(pubkey,k,r,h,mdash)
	verefy(pubkey,r)





