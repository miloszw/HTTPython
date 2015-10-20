import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8080               # Arbitrary non-privileged port


def serve():
    # Create TCP socket, bind it to given port and start listening for connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(0)
    print('Listening on port {}'.format(PORT))

    # Keep serving
    while True:
        conn, addr = s.accept()                 # Accept incoming connection
        print('Connection from', addr)
        while True:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)
            print('Sent data')
        conn.close()                            # Close connection
        print('Closed connection')

def shutdown():
    print('Exiting...')
    return

if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        shutdown()
