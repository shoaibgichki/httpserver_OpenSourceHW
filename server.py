import socket
import threading
import os
import mimetypes
import json
from datetime import datetime

HOST, PORT = '0.0.0.0', 8080
STATIC_DIR = 'static'

def log(message):
    print(f"[{datetime.now()}] {message}")

def handle_client(conn, addr):
    try:
        request = conn.recv(1024).decode()
        if not request:
            conn.close()
            return
        log(f"Request from {addr}:
{request.splitlines()[0]}")
        lines = request.split('\r\n')
        request_line = lines[0]
        method, path, _ = request_line.split()

        if path == '/api/hello':
            response_body = json.dumps({"message": "Hello, world!"})
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{response_body}"
            )
        elif path.startswith("/static"):
            file_path = path.lstrip('/')
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                mime, _ = mimetypes.guess_type(file_path)
                mime = mime or 'application/octet-stream'
                header = (
                    "HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {mime}\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode()
                conn.sendall(header + content)
                conn.close()
                return
            else:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFile Not Found"
        elif method == "POST" and path == "/api/echo":
            body = lines[-1]
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{body}"
            )
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nPath Not Found"

        conn.sendall(response.encode())
    except Exception as e:
        error_msg = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nServer Error"
        conn.sendall(error_msg.encode())
        log(f"Error: {e}")
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        log(f"Serving HTTP on port {PORT}...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    start_server()
