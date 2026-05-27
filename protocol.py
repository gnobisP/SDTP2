import json



def encode_message(message):
    return json.dumps(message).encode()



def decode_message(message):
    return json.loads(message.decode())