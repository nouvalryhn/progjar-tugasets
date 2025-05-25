import socket
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

BUFFER_SIZE = 8192  # 8 KiB

class ClientHandler:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.protocol = FileProtocol()

    def handle(self):
        buffer = ''
        while True:
            chunk = self.conn.recv(BUFFER_SIZE)
            if not chunk:
                break
            buffer += chunk.decode()
            if '\r\n\r\n' in buffer:
                request = buffer.split('\r\n\r\n')[0].strip()
                logging.warning(f"[Client {self.addr}] Request received, processing...")
                response = self.protocol.proses_string(request)
                response += '\r\n\r\n'
                self.conn.sendall(response.encode())
                logging.warning(f"[Client {self.addr}] Response sent.")
                break
        self.conn.close()
        logging.warning(f"[Client {self.addr}] Connection closed.")

class ThreadPoolFileServer:
    def __init__(self, host='0.0.0.0', port=7777, workers=5):
        self.address = (host, port)
        self.workers = workers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ThreadPoolExecutor(max_workers=self.workers)

    def serve(self):
        self.sock.bind(self.address)
        self.sock.listen(10)
        logging.warning(f"[Server] ThreadPool server running at {self.address} with {self.workers} workers.")
        try:
            while True:
                conn, addr = self.sock.accept()
                logging.warning(f"[Server] Connection from {addr}")
                handler = ClientHandler(conn, addr)
                self.executor.submit(handler.handle)
        except KeyboardInterrupt:
            logging.warning("[Server] Shutting down.")
        finally:
            self.sock.close()
            self.executor.shutdown(wait=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    server = ThreadPoolFileServer(port=7777, workers=workers)
    server.serve() 