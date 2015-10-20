import socket, re

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8080               # Arbitrary non-privileged port

CRLF = '\r\n'
HTTPVer = 'HTTP/1.1'


def serve():
    # Create TCP socket
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow socket to be reused so we don't have to wait for OS to relase it
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind to given port and start listening for connections
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

    method, uri, version = re.match(r'^(\S+)\s(\S+)\s(\S+)', requestLine).groups()

    # We only support GET requests
    if method != 'GET':
        sendResponse(conn, 501)                 # 501: not implemented
        return
    # We only support HTTP version 1.1
    if version != 'HTTP/1.1':
        sendResponse(conn, 505)                 # 501: not implemented
        return

def sendResponse(conn, statusCode):
    statusMessages = {
        501: 'Not Implemented',
        505: 'HTTP Version not supported'
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
