import socket
import os
import tkinter as tk
from tkinter import messagebox, filedialog

# Configure client
SERVER_HOST = '127.0.0.1'  # Change to the server's IP address if needed
SERVER_PORT = 5001
BUFFER_SIZE = 1024

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

def connect_to_server():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        return client_socket
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
        return None

def fetch_file_list():
    client_socket = connect_to_server()
    if client_socket:
        try:
            files_list = client_socket.recv(BUFFER_SIZE).decode()
            file_listbox.delete(0, tk.END)
            for file in files_list.split("\n"):
                if file.strip():
                    file_listbox.insert(tk.END, file)
            client_socket.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch file list: {e}")


def download_file():
    selected_file = file_listbox.get(tk.ACTIVE)
    if not selected_file:
        messagebox.showwarning("Selection Error", "Please select a file to download.")
        return

    client_socket = connect_to_server()
    if client_socket:
        try:
            # Send the filename request
            client_socket.send(selected_file.encode())

            # Check server response
            response = client_socket.recv(BUFFER_SIZE).decode()
            if response == "FILE_FOUND":
                filepath = f"downloads/{selected_file}"
                with open(filepath, 'wb') as f:
                    while True:
                        data = client_socket.recv(BUFFER_SIZE)
                        if not data:
                            break
                        f.write(data)
                messagebox.showinfo("Success", f"File '{selected_file}' downloaded successfully to '{filepath}'.")
            else:
                messagebox.showerror("Error", f"File '{selected_file}' not found on the server.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file: {e}")
        finally:
            client_socket.close()

# GUI Setup
app = tk.Tk()
app.title("File Downloader")
app.geometry("400x300")

# File list section
file_list_label = tk.Label(app, text="Available Files:")
file_list_label.pack(pady=5)

file_listbox = tk.Listbox(app, height=10, width=50)
file_listbox.pack(pady=5)

# Buttons
refresh_button = tk.Button(app, text="Refresh File List", command=fetch_file_list)
refresh_button.pack(pady=5)

download_button = tk.Button(app, text="Download File", command=download_file)
download_button.pack(pady=5)

# Start application
fetch_file_list()
app.mainloop()