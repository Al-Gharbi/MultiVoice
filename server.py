import socket
import threading
import time
import json
from collections import defaultdict
from datetime import datetime

class VoiceChatServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.clients = defaultdict(dict)
        self.running = False
        self.sock = None
        
        
        self.log_file = "server_log.txt"
        self.setup_logging()
        
    def setup_logging(self):
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n=== Server started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    def log_event(self, event, addr=None):
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if addr:
            message = f"[{timestamp}] {event} - Client: {addr}\n"
        else:
            message = f"[{timestamp}] {event}\n"
        
        print(message.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message)
    
    def setup_socket(self):
       
        try:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            return True
        except Exception as e:
            self.log_event(f"Failed to setup socket: {e}")
            return False
    
    def start(self):
        if not self.setup_socket():
            return
        
        try:
            self.running = True
            self.log_event(f"Server started on {self.host}:{self.port}")
            
            
            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.log_event("Press Ctrl+C to stop the server")
            
            
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            self.log_event(f"Server error: {e}")
        finally:
            self.stop()
    
    def receive_data(self):
        while self.running and self.sock:
            try:
                data, addr = self.sock.recvfrom(4096)
                
                
                if data.startswith(b'CTRL:'):
                    self.handle_control_message(data, addr)
                else:
                    
                    self.handle_voice_data(data, addr)
                
            except socket.error as e:
                if e.errno == 10054:  # Windows error for forcibly closed connection
                    self.log_event("Client forcibly closed connection", addr)
                    if addr in self.clients:
                        del self.clients[addr]
                elif self.running:
                    self.log_event(f"Socket error: {e}")
                    time.sleep(1)
            except Exception as e:
                if self.running:
                    self.log_event(f"Receive error: {e}")
                    time.sleep(1)
    
    def handle_control_message(self, data, addr):
        
        try:
            message = data.decode('utf-8')[5:]  
            control_data = json.loads(message)
            
            if control_data.get('type') == 'register':
               
                if addr not in self.clients:
                    self.clients[addr] = {
                        'last_seen': time.time(),
                        'status': 'connected',
                        'name': control_data.get('name', 'Unknown')
                    }
                    self.log_event(f"Client registered: {control_data.get('name', 'Unknown')}", addr)
                
                
                response = json.dumps({'type': 'registered', 'status': 'ok'})
                self.safe_sendto(('CTRL:' + response).encode('utf-8'), addr)
                
            elif control_data.get('type') == 'heartbeat':
                
                if addr in self.clients:
                    self.clients[addr]['last_seen'] = time.time()
                    response = json.dumps({'type': 'heartbeat_ack'})
                    self.safe_sendto(('CTRL:' + response).encode('utf-8'), addr)
            
            elif control_data.get('type') == 'disconnect':
                
                if addr in self.clients:
                    client_name = self.clients[addr].get('name', 'Unknown')
                    del self.clients[addr]
                    self.log_event(f"Client disconnected: {client_name}", addr)
        
        except Exception as e:
            self.log_event(f"Error processing control message: {e}", addr)
    
    def handle_voice_data(self, data, addr):
        
        if addr in self.clients:
            
            self.clients[addr]['last_seen'] = time.time()
            
            
            self.broadcast(data, addr)
        else:
            
            response = json.dumps({'type': 'error', 'message': 'Please register first'})
            self.safe_sendto(('CTRL:' + response).encode('utf-8'), addr)
    
    def safe_sendto(self, data, addr):
        
        if not self.sock:
            return False
            
        try:
            self.sock.sendto(data, addr)
            return True
        except Exception as e:
            self.log_event(f"Send error to {addr}: {e}")
            return False
    
    def broadcast(self, data, exclude_addr):
        
        for client_addr in list(self.clients.keys()):
            if client_addr != exclude_addr:
                if not self.safe_sendto(data, client_addr):
                    
                    if client_addr in self.clients:
                        del self.clients[client_addr]
    
    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.log_event("Server stopped")

if __name__ == "__main__":
    server = VoiceChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()