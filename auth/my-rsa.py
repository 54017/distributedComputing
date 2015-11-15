# -*- coding: utf-8 -*-

import rsa


def main():
	(publicKey, privateKey) = rsa.newkeys(1024)

	pub = publicKey.save_pkcs1()
	pubfile = open('public.pem','w+')
	pubfile.write(pub)
	pubfile.close()

	pri = privateKey.save_pkcs1()
	prifile = open('private.pem','w+')
	prifile.write(pri)
	prifile.close()

	prifile = open('private.pem', 'r')
	p = prifile.read()
	privateKey = rsa.PrivateKey.load_pkcs1(p)
	prifile.close()

	pubfile = open('public.pem', 'r')
	p = pubfile.read()
	publicKey = rsa.PublicKey.load_pkcs1(p)
	pubfile.close()

	message = "lalalalal"

	secret = rsa.encrypt(message, publicKey)
	non_secret = rsa.decrypt(secret, privateKey)
	print non_secret

	signature = rsa.sign(message, privateKey, 'SHA-1')
	rsa.verify("lalalalal", signature, publicKey)



if __name__ == '__main__':
	main()