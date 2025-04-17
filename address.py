class Address:
    def __init__(self, ip, port, id) -> None:
        self.ip = ip
        self.port = port
        self.id = id

    def get_id(self):
        return self.id

    def __str__(self) -> str:
        return f"id: {self.id} / {self.ip}:{self.port}"
