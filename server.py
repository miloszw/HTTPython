import socket, re, time, sys, os.path as osp

HOST = ''                           # Symbolic name meaning all available interfaces
try:
    PORT = int(sys.argv[1])         # Use first command line argument as port number
except (ValueError, IndexError):
    PORT = 8080                     # Fallback to preset value

CRLF = '\r\n'
HTTP_ver = 'HTTP/1.1'


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
        handle_request(conn, data)              # Handle request
        conn.close()                            # Close connection
        print('Closed connection')

def handle_request(conn, data):
    decoded_data = data.decode()
    print('Request:', decoded_data)
    data_array = decoded_data.split(CRLF)
    request_line = data_array[0]
    header_lines = data_array[1:] #TODO

    # TODO: check for trailing CRLF
    try:
        method, uri, version = re.match(r'^(\S+)\s(\S+)\s(\S+)', request_line).groups()
    except AttributeError: # match failed
        send_response(conn, 400)                 # 400: bad request
        return

    # We only support GET requests
    if method != 'GET':
        send_response(conn, 501)                 # 501: not implemented
        return
    # We only support HTTP version 1.1
    if version != 'HTTP/1.1':
        send_response(conn, 505)                 # 505: version not supported
        return

    try:
        with open(uri[1:], 'rb') as f:
            content = f.read()
            content_type = {
                'txt': 'text/plain',
                'jpg': 'image/JPEG',
                'jpeg': 'image/JPEG',
                'html': 'text/html',
                'htm': 'text/html'
            }.get(f.name.split('.')[1], 'text/plain')
            headers = {
                'Content-Type': content_type,
                'Content-Length': len(content),
                'Last-Modified': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(osp.getmtime(f.name)))
            }
            send_response(conn, 200, content, headers)
    except FileNotFoundError:
        send_response(conn, 404)

def send_response(conn, status_code, message_body='', message_headers={}):
    # Prepare status line
    status_messages = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
        501: 'Not Implemented',
        505: 'HTTP Version Not Supported'
    }
    status_string = '{} {}'.format(status_code, status_messages.get(status_code,''))
    status_line = '{} {}{}'.format(HTTP_ver, status_string, CRLF)

    # Prepare response headers
    message_headers.update({
        'Server': 'ServerMcAwesome/0.1',
        'Date': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
        'Connection': 'close'
    })
    headers = ''.join(['{}: {}{}'.format(k,v,CRLF) for (k,v) in message_headers.items()])

    # Prepare response
    response = bytearray('{}{}{}'.format(status_line, headers, CRLF), 'utf-8')
    response.extend(message_body or bytearray(status_string, 'utf-8'))
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
