import socket
import os
import threading
import tkinter.messagebox as messagebox
import queue
import time

class FileDownloadClient:
    def __init__(self, server_host='192.168.1.6', server_port=5001, buffer_size=1024):
        """
        Initialize the File Download Client
        
        :param server_host: IP address of the server
        :param server_port: Port number of the server
        :param buffer_size: Size of the buffer for network communication
        """
        self.SERVER_HOST = server_host
        self.SERVER_PORT = server_port
        self.BUFFER_SIZE = buffer_size
        self.download_status = {
            'status': None,
            'message': '',
            'timestamp': 0
        }
        self.download_lock = threading.Lock()
        self.is_downloading = False
    
    def get_file_list(self):
        """
        Retrieve the list of files from the server
        
        :return: List of files or None if connection fails
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
                files_list = client_socket.recv(self.BUFFER_SIZE).decode()
                return files_list.split('\n')
        except Exception as e:
            print(f"Error retrieving file list: {e}")
            return None
    
    def _download_worker(self, selected_file):
        """
        Background worker for file download
        
        :param selected_file: Name of the file to download
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
                
                # Receive the file list (part of protocol)
                client_socket.recv(self.BUFFER_SIZE).decode()
                
                # Send the file name
                client_socket.send(selected_file.encode())
                
                # Receive server response
                response = client_socket.recv(self.BUFFER_SIZE).decode()
                
                if response == "FILE_FOUND":
                    # Ensure downloads directory exists
                    filepath = os.path.join("downloads", selected_file)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Download file
                    with open(filepath, 'wb') as f:
                        while True:
                            data = client_socket.recv(self.BUFFER_SIZE)
                            if data == b"EOF":  # End-of-file marker
                                break
                            f.write(data)
                    
                    # Update download status
                    with self.download_lock:
                        self.download_status = {
                            'status': True,
                            'message': f"File '{selected_file}' downloaded successfully.",
                            'timestamp': time.time()
                        }
                elif response == "FILE_NOT_FOUND":
                    # Update download status
                    with self.download_lock:
                        self.download_status = {
                            'status': False,
                            'message': f"File '{selected_file}' was not found on the server.",
                            'timestamp': time.time()
                        }
                else:
                    # Update download status
                    with self.download_lock:
                        self.download_status = {
                            'status': False,
                            'message': "Invalid server response.",
                            'timestamp': time.time()
                        }
        
        except Exception as e:
            # Update download status
            with self.download_lock:
                self.download_status = {
                    'status': False,
                    'message': f"An error occurred: {e}",
                    'timestamp': time.time()
                }
        finally:
            self.is_downloading = False
    
    def download_file(self, selected_file):
        """
        Initiate file download in a background thread
        
        :param selected_file: Name of the file to download
        :return: Tuple (success, message)
        """
        if not selected_file:
            return False, "No file selected."
        
        if self.is_downloading:
            return False, "A download is already in progress."
        
        # Reset download status
        with self.download_lock:
            self.download_status = {
                'status': None,
                'message': '',
                'timestamp': 0
            }
        
        self.is_downloading = True
        
        # Start download in a separate thread
        download_thread = threading.Thread(
            target=self._download_worker, 
            args=(selected_file,)
        )
        download_thread.start()
        
        return True, "Download started."
    
    def check_download_status(self):
        """
        Check the current download status
        
        :return: Download status dictionary
        """
        with self.download_lock:
            # Return a copy of the status to prevent race conditions
            return dict(self.download_status)