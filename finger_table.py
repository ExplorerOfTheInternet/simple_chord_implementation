from address import Address
from settings import RING_SIZE


class FingerTable:
    def __init__(self, node_id: int) -> None:
        self.key = [(node_id + (2**i)) % (2**RING_SIZE) for i in range(RING_SIZE)]

        self.f_id: list[Address] = [None] * RING_SIZE
