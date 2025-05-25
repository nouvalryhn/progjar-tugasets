import socket
import logging
import sys
from multiprocessing import Pool
from file_protocol import FileProtocol

BUFFER_SIZE = 8192  # 8 KiB

def client_worker(conn_addr):
    conn, addr = conn_addr
    protocol = FileProtocol()
    buffer = ''
    while True:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        buffer += chunk.decode()
        if '\r\n\r\n' in buffer:
            request = buffer.split('\r\n\r\n')[0].strip()
            logging.warning(f"[Process {addr}] Request received, processing...")
            response = protocol.proses_string(request)
            response += '\r\n\r\n'
            conn.sendall(response.encode())
            logging.warning(f"[Process {addr}] Response sent.")
            break
    conn.close()
    logging.warning(f"[Process {addr}] Connection closed.")
    return True

class ProcessPoolFileServer:
    def __init__(self, host='0.0.0.0', port=7777, workers=5):
        self.address = (host, port)
        self.workers = workers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pool = Pool(processes=self.workers)

    def serve(self):
        self.sock.bind(self.address)
        self.sock.listen(10)
        logging.warning(f"[Server] ProcessPool server running at {self.address} with {self.workers} workers.")
        try:
            while True:
                conn, addr = self.sock.accept()
                logging.warning(f"[Server] Connection from {addr}")
                self.pool.apply_async(client_worker, args=((conn, addr),))
        except KeyboardInterrupt:
            logging.warning("[Server] Shutting down.")
        finally:
            self.sock.close()
            self.pool.close()
            self.pool.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    server = ProcessPoolFileServer(port=7777, workers=workers)
    server.serve() 