import zlib


def encode(message):
    return zlib.compress(message.encode())


def decode(message):
    return zlib.decompress(message).decode()