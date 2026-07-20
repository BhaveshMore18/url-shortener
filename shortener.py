import string

BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase

def encode(num: int) -> str:
    if num == 0:
        return BASE62[0]
    encoded = ""
    base = len(BASE62)
    while num:
        num, rem = divmod(num, base)
        encoded = BASE62[rem] + encoded
    return encoded