from socket import *
import pickle
import const
import threading

def handle_client(conn, addr):
    print("Chat Server: client is connected from address " + str(addr))
    marshaled_msg_pack = conn.recv(1024)  # receive data from client
    msg_pack = pickle.loads(marshaled_msg_pack)
    msg = msg_pack[0]
    dest = msg_pack[1]
    src = msg_pack[2]
    print("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest)  # just print the message and destination

    # Check that the destination exists
    try:
        dest_addr = const.registry[dest]  # get address of destination in the registry
    except:
        conn.send(pickle.dumps("NACK"))  # to do: send a proper error code
        conn.close()
        return
    else:
        conn.send(pickle.dumps("ACK"))  # send ACK to client
        conn.close()

    # Forward the message to the recipient client
    client_sock = socket(AF_INET, SOCK_STREAM)  # socket to connect to clients
    dest_ip = dest_addr[0]
    dest_port = dest_addr[1]
    try:
        client_sock.connect((dest_ip, dest_port))
    except:
        print("Error: Destination client is down")
        client_sock.close()
        return
    msg_pack = (msg, src)
    marshaled_msg_pack = pickle.dumps(msg_pack)
    client_sock.send(marshaled_msg_pack)
    marshaled_reply = client_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
        print("Error: Destination client did not receive message properly")
    else:
        pass
    client_sock.close()

def main():
    server_sock = socket(AF_INET, SOCK_STREAM)  # socket for clients to connect to this server
    server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
    server_sock.listen(5)  # may change if too many clients

    print("Chat Server is ready...")

    while True:
        conn, addr = server_sock.accept()

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == '__main__':
    main()
