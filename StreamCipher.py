import base64
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import struct


class StreamCipher:
  def __init__(self, key, backend=None):
    if backend is None:
      backend = default_backend()

      key = base64.urlsafe_b64decode(key)
      if len(key) != 16:
        raise ValueError("AES key must be 16 bytes long and url-safe base64-encoded."  
              "Got: {} ({})".format(key, len(key)))
      self._encryption_key = key
      self._backend = backend
      self._block_size_bytes = algorithms.AES.block_size / 8 # algorithms.AES.block_size = 128
      print("_block_size_bytes: {}".format(self._block_size_bytes))
      self._nonce_size = self._block_size_bytes / 2
      print("_nonce_size: {}".format(self._nonce_size))

  def get_nonced_counters(self, nonce, numblocks):
    for ctr in xrange(numblocks):
      yield nonce + struct.pack('>Q', ctr)

  def encrypt_one_block(self, data):
    encryptor = Cipher(algorithms.AES(self._encryption_key),modes.ECB(),self._backend).encryptor()
    return encryptor.update(data) + encryptor.finalize()

  def encrypt(self, data):  
    if not isinstance(data, bytes):
      raise TypeError("data must be bytes.")
    nonce = os.urandom(self._nonce_size)
    print("nonce: {}".format(nonce))
    ctx = ""

    pad = b''
    numblocks = (len(data)+self._block_size_bytes)/self._block_size_bytes
    print("numblocks: {}".format(numblocks))
    nonced_counter_generator = self.get_nonced_counters(nonce, numblocks)
    print("nonced_counter_generator {}".format(nonced_counter_generator))
    
    for nonced_counter in nonced_counter_generator: 
      pad += self.encrypt_one_block(nonced_counter)
    print("pad: {}".format(pad))
    ciphertext = ''.join([unichr(ord(pad_byte) ^ ord(data_byte)) for pad_byte, data_byte in zip(pad, data)])
    print("ciphertext: {}".format(ciphertext.encode("utf-8")))
    ctx = nonce, ciphertext
    return ctx

  def decrypt(self, ctx):
    data = ""
    pad = ''
    numblocks = (len(ctx[1])+self._block_size_bytes)/self._block_size_bytes
    nonce = ctx[0] 
    ciphertext = ctx[1]
    nonced_counter_generator = self.get_nonced_counters(nonce, numblocks)

    for nonced_counter in nonced_counter_generator: 
      pad += self.encrypt_one_block(nonced_counter) 
    data  = [unichr(ord(pad_byte) ^ ord(ciphertext_byte)) for pad_byte, ciphertext_byte in zip(pad, ciphertext)]
    data=''.join(data)
    return data
