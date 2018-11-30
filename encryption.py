from Crypto.Cipher import AES
import base64
import json

DEFAULT_KEY = 'a3K8Bx%2r8Y7#xDh'

def encrypt(message, key = DEFAULT_KEY):
    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.encrypt(json.dumps(message))
    return base64.b64encode(msg.encode())

def decrypt(message, key = DEFAULT_KEY):
    decipher = AES.new(key, AES.MODE_ECB)
    msg = decipher.decrypt(message)
    return json.loads(msg)