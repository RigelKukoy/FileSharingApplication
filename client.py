import socket
import os
from tkinter import Tk, Listbox, Button, messagebox

# Configure client
SERVER_HOST = '172.20.10.14'  # Server's IP address
SERVER_PORT = 5001
BUFFER_SIZE = 1024

# GUI setup
def refresh_file_list():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        # Receive the file list
        files_list = client_socket.recv(BUFFER_SIZE).decode()
        file_listbox.delete(0, 'end')  # Clear the listbox
        for file in files_list.split('\n'):
            file_listbox.insert('end', file)
        client_socket.close()
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")

def download_file():
    try:
        # Get the selected file
        selected_file = file_listbox.get(file_listbox.curselection()).strip()  # Strip whitespace
        print(f"Selected file: '{selected_file}'")
        
        if not selected_file:
            messagebox.showerror("Error", "No file selected.")
            return

        # Connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        # Receive the file list (not used here but part of protocol)
        client_socket.recv(BUFFER_SIZE).decode()

        # Send the sanitized file name
        client_socket.send(selected_file.encode())

        # Receive server response
        response = client_socket.recv(BUFFER_SIZE).decode()
        print(f"Server response: {response}")

        if response == "FILE_FOUND":
            # Save the file to the "downloads" directory
            filepath = os.path.join("downloads", selected_file)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    if data == b"EOF":  # End-of-file marker
                        break
                    f.write(data)

            messagebox.showinfo("Success", f"File '{selected_file}' downloaded successfully.")
        elif response == "FILE_NOT_FOUND":
            messagebox.showerror("Error", f"File '{selected_file}' was not found on the server.")
        else:
            messagebox.showerror("Error", "Invalid server response.")
        
        client_socket.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Initialize GUI
root = Tk()
root.title("File Downloader")

file_listbox = Listbox(root, width=50, height=15)
file_listbox.pack(pady=10)

refresh_button = Button(root, text="Refresh File List", command=refresh_file_list)
refresh_button.pack(pady=5)

download_button = Button(root, text="Download File", command=download_file)
download_button.pack(pady=5)

root.mainloop()
