from ftplib import FTP
import os
import subprocess
import time
import logging
from playsound import playsound

sound_file_path = './assets/beep-01a.wav'

# Function to play a sound
def play_notification_sound():
    playsound(sound_file_path)

# Define log file names for each village
log_file_1 = 'ftp_server_1.log'
log_file_2 = 'ftp_server_2.log'



# Initialize logging
logging.basicConfig(filename=log_file_1, level=logging.INFO, format='%(asctime)s - %(message)s')


# Define the configurations for both FTP servers
ftp_config_1 = {
    "network_name": 'Yoo',
    "ftp_server": '192.168.1.218',
    "username": 'ftp-user',
    "password": '1234',
    "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
    # "network_name": 'eduroam',
    # "ftp_server": '10.226.120.41',
    # "username": 'ftp-villageA',
    # "password": '1234',
    # "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
}

ftp_config_2 = {
    "network_name": 'eduroam',
    "ftp_server": '10.226.121.80',
    "username": 'ftp-user2',
    "password": '1234',
    "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
}

def delete_files(ftp, file_list):
    for remote_filename in file_list:
        ftp.delete(remote_filename)
        print(f'Deleted {remote_filename} from the FTP server')

def is_connected_to_wifi_network(network_name):
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        return network_name in output
    except subprocess.CalledProcessError:
        return False

def download_files(ftp, local_directory, downloaded_files):
    file_list = ftp.nlst()

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    for remote_filename in file_list:
        if remote_filename not in downloaded_files:
            local_filepath = os.path.join(local_directory, remote_filename)
            with open(local_filepath, 'wb') as local_file:
                ftp.retrbinary(f'RETR {remote_filename}', local_file.write)
            print(f'Downloaded {remote_filename} to {local_filepath}')
            downloaded_files.append(remote_filename)  # Append to the list

            # Log the file transfer
            logging.info(f'Downloaded {remote_filename} to {local_filepath}')


def upload_files(ftp, local_directory):
    local_files = os.listdir(local_directory)

    for local_filename in local_files:
        local_filepath = os.path.join(local_directory, local_filename)
        with open(local_filepath, 'rb') as local_file:
            ftp.storbinary(f'STOR {local_filename}', local_file)
            print(f'Uploaded {local_filename} to the FTP server')
            # Log the file transfer
            logging.info(f'Uploaded {local_filename} to the FTP server')

while True:
    print("Waiting for connection....")
    downloaded_files = []  # Initialize the list for downloaded files

    if is_connected_to_wifi_network(ftp_config_1["network_name"]):
        print(f'Connected to {ftp_config_1["network_name"]} as {ftp_config_1["username"]}. Downloading files.')

        try:
            # Connect to the first FTP server
            ftp1 = FTP()
            ftp1.connect(ftp_config_1["ftp_server"])
            ftp1.login(ftp_config_1["username"], ftp_config_1["password"])

            # Download files from the first FTP server
            download_files(ftp1, ftp_config_1["local_directory"], downloaded_files)

            # Remove downloaded files from the first FTP server
            delete_files(ftp1, downloaded_files)

            # Close the connection to the first FTP server
            ftp1.quit()

            # Play a sound to indicate successful transfer
            play_notification_sound()
        except Exception as e:
            print(f"Error downloading from FTP server 1: {str(e)}")

    if is_connected_to_wifi_network(ftp_config_2["network_name"]):
        print(f'Connected to {ftp_config_2["network_name"]} as {ftp_config_2["username"]}. Uploading files.')

        local_files = os.listdir(ftp_config_2["local_directory"])  # Initialize the list for local files

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

        # Remove uploaded files from the local directory
        for local_filename in local_files:
            local_filepath = os.path.join(ftp_config_2["local_directory"], local_filename)
            os.remove(local_filepath)

        # Close the connection to the second FTP server
        ftp2.quit()

        # Play a sound to indicate successful transfer
        play_notification_sound()

    # Sleep before checking again
    time.sleep(5)
