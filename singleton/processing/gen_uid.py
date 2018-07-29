import uuid

def gen_uid():
    gen_key = str(uuid.uuid1())
    key = ''
    for char in gen_key:
        if char  != '-':
            key += char
    return key
