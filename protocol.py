import pickle

CMD_FIELD_LENGTH = 10  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol

def build_message(cmd, msg):
    # Build a message according to the protocol.

    if len(cmd) > CMD_FIELD_LENGTH or len(cmd) == 0 or len(msg) > MAX_DATA_LENGTH:
        return None
    data = pickle.dumps(msg)
    s = (cmd.ljust(CMD_FIELD_LENGTH) + str(len(data)).zfill(LENGTH_FIELD_LENGTH)).encode()
    return b''.join((s, data))

def receive_data(socket):
    # Receive and decode data from a socket according to the protocol.

    cmd = socket.recv(CMD_FIELD_LENGTH).decode().strip()
    length = socket.recv(LENGTH_FIELD_LENGTH).decode()

    try:
        length = int(length)
    except ValueError:
        return "", ""

    data = socket.recv(length)
    return cmd, pickle.loads(data)