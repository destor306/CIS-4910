from ftplib import FTP
import os
import subprocess
import time

# Define the configurations for both FTP servers
ftp_config_1 = {
    "network_name": 'eduroam',
    "ftp_server": '10.226.120.41',
    "username": 'ftp-villageA',
    "password": '1234',
    "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
}

ftp_config_2 = {
    "network_name": 'eduroam',
    "ftp_server": '10.226.121.80',
    "username": 'ftp-user2',
    "password": '1234',
    "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
}

def is_connected_to_wifi_network(network_name):
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        return network_name in output
    except subprocess.CalledProcessError:
        return False

def download_files(ftp, local_directory):
    downloaded_files = []
    file_list = ftp.nlst()

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # Download each file from the FTP server
    for remote_filename in file_list:
        if remote_filename not in downloaded_files:
            local_filepath = os.path.join(local_directory, remote_filename)
            with open(local_filepath, 'wb') as local_file:
                ftp.retrbinary(f'RETR {remote_filename}', local_file.write)
            print(f'Downloaded {remote_filename} to {local_filepath}')
            downloaded_files.append(remote_filename)

def upload_files(ftp, local_directory):
    local_files = os.listdir(local_directory)

    for local_filename in local_files:
        local_filepath = os.path.join(local_directory, local_filename)
        with open(local_filepath, 'rb') as local_file:
            ftp.storbinary(f'STOR {local_filename}', local_file)
            print(f'Uploaded {local_filename} to the FTP server')

while True:
    if is_connected_to_wifi_network(ftp_config_1["network_name"]):
        print(f'Connected to {ftp_config_1["network_name"]} as {ftp_config_1["username"]}. Downloading files.')
        
        # Connect to the first FTP server
        ftp1 = FTP()
        ftp1.connect(ftp_config_1["ftp_server"])
        ftp1.login(ftp_config_1["username"], ftp_config_1["password"])
        
        # Download files from the first FTP server
        download_files(ftp1, ftp_config_1["local_directory"])
        
        # Close the connection to the first FTP server
        ftp1.quit()

    if is_connected_to_wifi_network(ftp_config_2["network_name"]):
        print(f'Connected to {ftp_config_2["network_name"]} as {ftp_config_2["username"]}. Uploading files.')
        
        while True:
            try:
                # Connect to the second FTP server
                ftp2 = FTP()
                ftp2.connect(ftp_config_2["ftp_server"])
                ftp2.login(ftp_config_2["username"], ftp_config_2["password"])
                break  # Break the loop if the connection is successful
            except TimeoutError:
                # Handle the timeout error (server not available)
                print("Server not available. Retrying...")
                time.sleep(5)

        # Upload files to the second FTP server
        upload_files(ftp2, ftp_config_2["local_directory"])    
        # Close the connection to the second FTP server
        ftp2.quit()
        
    time.sleep(5)
