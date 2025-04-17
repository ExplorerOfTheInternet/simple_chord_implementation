import hashlib
from settings import RING_SIZE


def addrToID(ip: str) -> int:
    id = hashlib.sha1(ip.encode()).hexdigest()
    return int(id, 16) % (2**RING_SIZE)
