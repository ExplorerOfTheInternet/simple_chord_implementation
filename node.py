from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from address import Address
from finger_table import FingerTable
import time
import threading
from settings import RING_SIZE, INTERVAL_TIME


def is_in_interval(
    start: int, id: int, end: int, inclusive_start=False, inclusive_end=False
):
    """Function to Check wether a value is in a given interval in a circle

    Args:
        start (int): intervals starting point
        id (int): value to check
        end (int): intervals end point
        inclusive_start (bool, optional): include or exlude starting value. Defaults to False.
        inclusive_end (bool, optional): include or exlude end value. Defaults to False.

    Returns:
        bool: Status if the value is in the interval
    """
    if start == end:
        return True

    if start < end:
        if inclusive_start and inclusive_end:
            return start <= id <= end
        elif inclusive_start:
            return start <= id < end
        elif inclusive_end:
            return start < id <= end
        else:
            return start < id < end
    else:
        # Wrap-around
        if inclusive_start and inclusive_end:
            return id >= start or id <= end
        elif inclusive_start:
            return id >= start or id < end
        elif inclusive_end:
            return id > start or id <= end
        else:
            return id > start or id < end


class Node:
    """Member of a CHORD Network"""

    def __init__(self, address: Address) -> None:
        self.address: Address = address
        self.finger: FingerTable = FingerTable(address.id)
        self.next_finger: int = 0
        self.successor: Address = self.address
        self.predecessor: Address = None

        self.finger.f_id[0] = self.successor

    def get_successor(self) -> Address:
        return self.successor

    def get_predecessor(self) -> Address:
        return self.predecessor

    def get_address(self) -> Address:
        return self.address

    def join(self, known_address: Address):
        """Method to Join the Node to a CHORD Network

        Args:
            known_address (Address): Address of an existing Node already in a Network
        """
        threading.Thread(target=self.background_tasks, daemon=True).start()
        # First Node
        if known_address == self.address:
            self.successor = self.address
            return

        # Add Node to existing Network
        known_node: Node = ServerProxy(
            f"http://{known_address.ip}:{known_address.port}"
        )

        succ = known_node.find_successor(self.address.id)
        self.successor = Address(
            id=succ["id"],
            ip=succ["ip"],
            port=succ["port"],
        )

    def find_successor(self, id) -> Address:
        """Method to find the Successor for an ID in a CHORD Network

        Args:
            id (int): ID to check

        Returns:
            Address: Found Node's Address
        """
        # Break Condition
        if is_in_interval(self.address.id, id, self.successor.id, inclusive_end=True):
            return self.successor

        # Recursive Loop trough Finger Tables
        else:
            closest_preceding_node: Address = self.closest_preceding_node(id)
            next_node: Node = ServerProxy(
                f"http://{closest_preceding_node.ip}:{closest_preceding_node.port}"
            )
            succ = next_node.find_successor(id)
            return Address(ip=succ["ip"], id=succ["id"], port=succ["port"])

    def closest_preceding_node(self, id) -> Address:
        """Method to search the finger table for the closest preceding Node

        Args:
            id (int): desired ID

        Returns:
            Address: Closest preceding Node to the desired ID
        """
        # Search trough Finger Table
        for i in reversed(range(RING_SIZE)):
            if self.finger.f_id[i] and is_in_interval(
                self.address.id, id, self.finger.key[i]
            ):
                return self.finger.f_id[i]
        return self.address

    def fix_fingers(self):
        """Method to update one finger table entry"""
        self.next_finger = (self.next_finger + 1) % RING_SIZE

        updated_successor: Address = self.find_successor(
            self.finger.key[self.next_finger]
        )

        self.finger.f_id[self.next_finger] = updated_successor

    def check_predecessor(self):
        """Method to check the availability of the Predecessor"""
        if self.predecessor is not None:
            try:
                proxy: Node = ServerProxy(
                    f"http://{self.predecessor.ip}:{self.predecessor.port}"
                )
                proxy.ping()
            except:
                self.predecessor = None

    def notify(self, n1):
        """Method to notify this Node of a potential new Predecessor

        Args:
            n1 (Node): potential new Predecessor
        """
        if self.predecessor is None or is_in_interval(
            self.predecessor.id, n1["id"], self.address.id
        ):
            self.predecessor = Address(ip=n1["ip"], port=n1["port"], id=n1["id"])

    def stabilize(self):
        """Method to check if there current successor is still correct"""
        successor: Node = ServerProxy(
            f"http://{self.successor.ip}:{self.successor.port}", allow_none=True
        )

        if self.get_predecessor() and is_in_interval(
            self.address.id,
            successor.get_predecessor()["id"],
            successor.get_address()["id"],
        ):
            self.successor = Address(
                ip=successor.get_predecessor()["ip"],
                port=successor.get_predecessor()["port"],
                id=successor.get_predecessor()["id"],
            )

        successor.notify(
            {
                "id": self.address.id,
                "ip": self.address.ip,
                "port": self.address.port,
            }
        )

    def ping(self):
        return True

    def run(self):
        """Method to run the Nodes RPC Server"""
        with SimpleXMLRPCServer(
            (self.address.ip, self.address.port), allow_none=True, logRequests=False
        ) as server:
            server.register_instance(self)
            server.serve_forever()

    def background_tasks(self):
        """Method in a seperate Thread to periodically run the background tasks"""
        while True:
            print("-" * 40)
            print("self ", self.address)
            print(f"Fingertable Node {self.address.id}:")
            for finger in range(RING_SIZE):
                print(f"{self.finger.key[finger]}:   {self.finger.f_id[finger]}")

            print("succ ", self.successor)
            print("pre ", self.predecessor)

            self.check_predecessor()
            self.stabilize()
            self.fix_fingers()

            print(self.next_finger)

            time.sleep(INTERVAL_TIME)

    def __str__(self) -> str:
        return f"{self.address}"
