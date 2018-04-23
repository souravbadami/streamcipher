from __future__ import print_function
import base64
import os
from StreamCipher import StreamCipher

def main():
  # Test utility to experiment the algorithm.
  key = base64.urlsafe_b64encode(os.urandom(16))
  instance = StreamCipher(key)
  print("key: {}".format(key))  
  encrypted_data = instance.encrypt(raw_input("Plaintext: "))
  print("encrypted data: {}".format(encrypted_data))
  decrypted_data = instance.decrypt(encrypted_data)
  print("decrypted data: {}".format(decrypted_data))

if __name__ == '__main__':
  main()