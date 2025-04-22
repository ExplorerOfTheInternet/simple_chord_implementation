import sys
from node import Node
from address import Address
from addrToID import addrToID

address = Address(
    ip=sys.argv[1].split(":")[0],
    port=int(sys.argv[1].split(":")[1]),
    id=addrToID(sys.argv[1]),
)

known_address = (
    Address(
        ip=sys.argv[2].split(":")[0],
        port=int(sys.argv[2].split(":")[1]),
        id=addrToID(sys.argv[2]),
    )
    if len(sys.argv) > 2
    else address
)


node = Node(address)
node.join(known_address)
node.run()
