import socket, re, time, os.path as osp

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
    decodedData = data.decode()
    print('Request:', decodedData)
    dataArray = decodedData.split(CRLF)
    requestLine = dataArray[0]
    headerLines = dataArray[1:]

    # TODO: check for trailing CRLF
    method, uri, version = re.match(r'^(\S+)\s(\S+)\s(\S+)', requestLine).groups()

    # We only support GET requests
    if method != 'GET':
        sendResponse(conn, 501)                 # 501: not implemented
        return
    # We only support HTTP version 1.1
    if version != 'HTTP/1.1':
        sendResponse(conn, 505)                 # 501: not implemented
        return

    try:
        with open(uri[1:], 'rb') as f:
            content = f.read()
            contentType = {
                'txt': 'text/plain',
                'jpg': 'image/JPEG',
                'jpeg': 'image/JPEG',
                'html': 'text/html',
                'htm': 'text/html'
            }.get(f.name.split('.')[1], 'text/plain')
            headers = {
                'Content-Type': contentType,
                'Content-Length': len(content),
                'Last-Modified': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(osp.getmtime(f.name)))
            }
            sendResponse(conn, 200, content, headers)
    except IOError:
        sendResponse(conn, 404)

def sendResponse(conn, statusCode, messageBody='', messageHeaders={}):
    # Prepare status line
    statusMessages = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
        505: 'HTTP Version not supported'
    }
    statusString = '{} {}'.format(statusCode, statusMessages.get(statusCode,''))
    statusLine = '{} {}{}'.format(HTTPVer, statusString, CRLF)

    # Prepare response headers
    messageHeaders.update({
        'Server': 'ServerMcAwesome/0.1',
        'Date': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
        'Connection': 'close'
    })
    headers = ''.join(['{}: {}{}'.format(k,v,CRLF) for (k,v) in messageHeaders.items()])

    # Prepare response
    response = bytearray('{}{}{}'.format(statusLine, headers, CRLF), 'utf-8')
    response.extend(messageBody)
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
