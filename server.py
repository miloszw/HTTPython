import socket, re

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8080               # Arbitrary non-privileged port

CRLF = '\r\n'
HTTPVer = 'HTTP/1.1'


def serve():
    # Create TCP socket, bind it to given port and start listening for connections
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(0)
    print('Listening on port {}'.format(PORT))

    # Keep serving
    while True:
        conn, addr = sock.accept()              # Accept incoming connection
        print('Connection from', addr)
        data = conn.recv(1024)                  # Receive request
        handleRequest(conn, data)               # Handle request
        conn.close()                            # Close connection
        print('Closed connection')

def handleRequest(conn, data):
    dataArray = data.decode().split(CRLF)
    requestLine = dataArray[0]
    headerLines = dataArray[1:]

    if not re.match(r'^GET', requestLine):
        # We only support GET requests
        # Send status code 501: not implemented
        sendResponse(conn, 501)

def sendResponse(conn, statusCode):
    statusMessages = {
        501: 'Not Implemented'
    }
    responseString = '{}: {}'.format(statusCode, statusMessages.get(statusCode,''))
    response = bytearray('{} {} {}'.format(HTTPVer, responseString, CRLF), 'UTF-8')
    conn.sendall(response)

def shutdown():
    print('Exiting...')
    sock.close()
    return

if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        shutdown()
