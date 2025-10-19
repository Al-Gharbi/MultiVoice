import socket
import threading
import time
import sounddevice as sd
import numpy as np
import argparse
import json
import sys
import os
import msvcrt
from datetime import datetime

class VoiceChatClient:
    def __init__(self, server_host, server_port, client_port=12346, name="User"):
        self.server_host = server_host
        self.server_port = server_port
        self.client_port = client_port
        self.name = name
        self.running = False
        self.muted = False  
        self.connected = False
        
       
        self.sock = None
        self.create_socket()
        
      
        self.samplerate = 44100
        self.blocksize = 1024
        self.channels = 1
        self.dtype = 'int16'
        
       
        self.audio_buffer = []
        self.buffer_max_size = 20  
        
        
        self.record_stream = None
        self.playback_stream = None
        
    def create_socket(self):
        
        try:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.client_port))
            self.sock.settimeout(1.0)
            return True
        except Exception as e:
            print(f"Failed to create socket: {e}")
            return False
        
    def connect(self):
        
        try:
            
            register_msg = json.dumps({
                'type': 'register',
                'name': self.name,
                'timestamp': time.time()
            })
            
            if not self.safe_sendto(('CTRL:' + register_msg).encode('utf-8'), (self.server_host, self.server_port)):
                return False
            
            
            original_timeout = self.sock.gettimeout()
            self.sock.settimeout(5.0)
            
            try:
                data, addr = self.sock.recvfrom(4096)
                
                if data.startswith(b'CTRL:'):
                    response = json.loads(data.decode('utf-8')[5:])
                    if response.get('type') == 'registered' and response.get('status') == 'ok':
                        self.connected = True
                        print("Successfully connected to server")
                        return True
                
                print("Failed to connect to server - invalid response")
                return False
                
            except socket.timeout:
                print("Connection timeout - server may be offline")
                return False
            finally:
                self.sock.settimeout(original_timeout)
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def safe_sendto(self, data, addr):
        
        if not self.sock:
            if not self.create_socket():
                return False
                
        try:
            self.sock.sendto(data, addr)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def start(self):
        try:
            if not self.connect():
                return
            
            self.running = True
            print(f"Client started. Press 'r' to mute/unmute, 'q' to quit")
            print("Commands:")
            print("  r - Mute/Unmute audio")
            print("  q - Quit")
            
            
            self.start_recording()
            
           
            receive_thread = threading.Thread(target=self.receive_audio)
            receive_thread.daemon = True
            receive_thread.start()
            
            
            heartbeat_thread = threading.Thread(target=self.send_heartbeats)
            heartbeat_thread.daemon = True
            heartbeat_thread.start()
            
            
            playback_thread = threading.Thread(target=self.playback_audio)
            playback_thread.daemon = True
            playback_thread.start()
            
            
            self.user_interface()
            
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.disconnect()
            self.stop()
    
    def receive_audio(self):
        
        while self.running:
            try:
                if not self.sock:
                    time.sleep(0.1)
                    continue
                    
                data, addr = self.sock.recvfrom(4096)
                
                if data.startswith(b'CTRL:'):
                    
                    control_data = json.loads(data.decode('utf-8')[5:])
                    if control_data.get('type') == 'heartbeat_ack':
                        continue 
                else:
                    
                    if len(self.audio_buffer) < self.buffer_max_size:
                        
                        audio_data = np.frombuffer(data, dtype=self.dtype)
                        self.audio_buffer.append(audio_data)
            
            except socket.timeout:
                continue 
            except socket.error as e:
                if e.errno == 10038:  # Operation on non-socket
                    print("Socket error, recreating socket...")
                    if not self.create_socket():
                        time.sleep(1)
                elif e.errno == 10054:  # Connection forcibly closed
                    print("Server forcibly closed the connection")
                    self.running = False
                else:
                    print(f"Socket error: {e}")
                    time.sleep(1)
            except Exception as e:
                print(f"Receive audio error: {e}")
                time.sleep(1)
    
    def playback_audio(self):
        
        while self.running:
            try:
                if self.audio_buffer:
                    
                    combined_audio = np.concatenate(self.audio_buffer)
                    
                    
                    if not self.playback_stream:
                        self.playback_stream = sd.OutputStream(
                            samplerate=self.samplerate,
                            channels=self.channels,
                            dtype=self.dtype
                        )
                        self.playback_stream.start()
                    
                    
                    self.playback_stream.write(combined_audio)
                    
                    
                    self.audio_buffer.clear()
                
                time.sleep(0.1)  
                
            except Exception as e:
                print(f"Playback error: {e}")
                if self.playback_stream:
                    try:
                        self.playback_stream.stop()
                        self.playback_stream.close()
                    except:
                        pass
                    self.playback_stream = None
                time.sleep(1)
    
    def send_heartbeats(self):
        
        while self.running and self.connected:
            try:
                heartbeat_msg = json.dumps({
                    'type': 'heartbeat',
                    'timestamp': time.time()
                })
                self.safe_sendto(('CTRL:' + heartbeat_msg).encode('utf-8'), 
                                (self.server_host, self.server_port))
            except Exception as e:
                print(f"Heartbeat error: {e}")
            
            time.sleep(10)  
    
    def start_recording(self):
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio callback status: {status}")
            if not self.muted and self.connected:  
                try:
                    audio_bytes = indata.tobytes() # convert audio data to bytes
                    self.safe_sendto(audio_bytes, (self.server_host, self.server_port))
                except Exception as e:
                    print(f"Send audio error: {e}")
        
        try:
            self.record_stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                channels=self.channels,
                dtype=self.dtype,
                callback=audio_callback
            )
            self.record_stream.start()
            print("Recording started automatically")
        except Exception as e:
            print(f"Recording error: {e}")
    
    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            print("Audio muted")
        else:
            print("Audio unmuted")
    
    def stop_recording(self):
        if self.record_stream:
            try:
                self.record_stream.stop()
                self.record_stream.close()
            except:
                pass
            self.record_stream = None
    
    def user_interface(self):
        while self.running:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    
                    if key == 'r':
                        self.toggle_mute()
                    elif key == 'q':
                        print("Quitting...")
                        self.running = False
                
                time.sleep(0.1)  
                
            except Exception as e:
                print(f"Interface error: {e}")
                time.sleep(1)
    
    def disconnect(self):
        if self.connected:
            try:
                disconnect_msg = json.dumps({
                    'type': 'disconnect',
                    'timestamp': time.time()
                })
                self.safe_sendto(('CTRL:' + disconnect_msg).encode('utf-8'), 
                                (self.server_host, self.server_port))
            except Exception as e:
                print(f"Disconnect error: {e}")
            
            self.connected = False
    
    def stop(self):
        self.running = False
        self.stop_recording()
        
        if self.playback_stream:
            try:
                self.playback_stream.stop()
                self.playback_stream.close()
            except:
                pass
            self.playback_stream = None
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
            
        print("Client stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Voice Chat Client')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=12345, help='Server port')
    parser.add_argument('--client-port', type=int, default=12346, help='Client port')
    parser.add_argument('--name', default='User', help='Your display name')
    
    args = parser.parse_args()
    
    client = VoiceChatClient(args.host, args.port, args.client_port, args.name)
    try:
        client.start()
    except KeyboardInterrupt:
        print("\nShutting down client...")
        client.stop()