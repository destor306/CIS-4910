from ftplib import FTP
import os
import subprocess
import time
import logging
from playsound import playsound


beep1 = './assets/beep-01a.wav'
beep2 = './assets/beep-05.wav'

# Function to play a sound
def play_notification_sound(sound_path):
    playsound(sound_path)

# Define the base directory for log files
log_base_directory = r'C:\Users\hyunj\OneDrive\Desktop\MVP'

# Initialize logging for the client
client_log_file = r'C:\Users\hyunj\OneDrive\Desktop\MVP\client.log'
logging.basicConfig(filename=client_log_file, level=logging.INFO, format='%(asctime)s - %(message)s')



# Define the configurations for both FTP servers
ftp_config_1 = {
    "network_name": 'Yoo',
    "ftp_server": '192.168.1.218',
    "username": 'ftp-user',
    "password": '1234',
    "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
}

ftp_config_2 = {
    "network_name": 'Yoo',
    "ftp_server": '192.168.1.54',
    "username": 'ftp-villageA',
    "password": '1234',
    "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
}

def delete_files(ftp, file_list):
    for remote_filename in file_list:
        ftp.delete(remote_filename)
        print(f'Deleted {remote_filename} from the {ftp.host}')

def delete_local_files(local_directory):
    try:
        local_files = os.listdir(local_directory)
        for local_filename in local_files:
            local_filepath = os.path.join(local_directory, local_filename)
            file_extension = os.path.splitext(local_filename)[1]

            # Check if the file extension is not ".log" before deleting
            if file_extension != ".log":
                os.remove(local_filepath)
                print(f'Deleted local file: {local_filename}')
    except Exception as e:
        print(f"Error deleting local files: {str(e)}")

def is_connected_to_wifi_network(network_name):
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        return network_name in output
    except subprocess.CalledProcessError:
        return False

def download_files(ftp, username, local_directory, downloaded_files, log_file):
    file_list = ftp.nlst()

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    for remote_filename in file_list:
        if remote_filename not in downloaded_files:
            # Check the file extension and skip downloading log files
            if not remote_filename.endswith('.log'):
                local_filepath = os.path.join(local_directory, remote_filename)
                with open(local_filepath, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {remote_filename}', local_file.write)

                # Modify the log message to include source and filename
                log_message = f'From {username} {ftp.host} download {remote_filename} to {local_filepath}'
                logging.info(log_message)

                print(f'Downloaded {remote_filename} to {local_filepath}')
                downloaded_files.append(remote_filename)  # Append to the list

    logging.shutdown()


def upload_files(ftp, local_directory, uploading_files):
    local_files = os.listdir(local_directory)

    for local_filename in local_files:
        if local_filename not in uploading_files:
            if not local_filename.endswith(".log"):
                local_filepath = os.path.join(local_directory, local_filename)
                with open(local_filepath, 'rb') as local_file:
                    ftp.storbinary(f'STOR {local_filename}', local_file)

                # Log the action on the client
                log_message = f'From User {local_directory} upload {local_filename} to {ftp.host}'
                logging.info(log_message)

                print(f'Uploaded {local_filename} to the FTP server')
                uploading_files.append(local_filename)
    logging.shutdown()

def upload_log_files(ftp, local_directory):
    local_files = os.listdir(local_directory)

    for local_filename in local_files:
        if local_filename.endswith(".log"):
            local_filepath = os.path.join(local_directory, local_filename)
            with open(local_filepath, 'rb') as local_file:
                ftp.storbinary(f'STOR {local_filename}', local_file)

            # Log the action on the client
            log_message = f'From User {local_directory} upload {local_filename} to {ftp.host}'
            logging.info(log_message)

            print(f'Uploaded {local_filename} to the FTP server')
    logging.shutdown()


while True:
    # Check if connected to server_1
    if is_connected_to_wifi_network(ftp_config_1["network_name"]):
        try:
            # Connect to server_1
            while True:
                try:
                    ftp1 = FTP()
                    ftp1.connect(ftp_config_1["ftp_server"])
                    ftp1.login(ftp_config_1["username"], ftp_config_1["password"])
                    break  # Break the loop if the connection is successful
                except TimeoutError:
                    # Handle the timeout error (server not available)
                    print("Server not available. Retrying...")
                    time.sleep(5)

            downloaded_files = []  # Initialize the list for downloaded files
            print(f'Connected to {ftp_config_1["network_name"]} as {ftp_config_1["username"]}. Downloading files.')

            # Download files from server_1
            download_files(ftp1, ftp_config_1["username"], ftp_config_1["local_directory"], downloaded_files, client_log_file)
            

            # upload_files(ftp1, ftp_config_1["local_directory"])
            # # Remove uploaded files from the local directory
            # delete_local_files(ftp_config_1["local_directory"])

            # Play a sound to indicate successful transfer
            if downloaded_files:
                play_notification_sound(beep1)
                # Upload files to server_1
                upload_log_files(ftp1, ftp_config_1["local_directory"])

            delete_files(ftp1, downloaded_files)

            # Close the connection to server_1
            ftp1.quit()
        except Exception as e:
            print(f"Error downloading from FTP server 1: {str(e)}")

    # Check if connected to server_2
    if is_connected_to_wifi_network(ftp_config_2["network_name"]):
        try:
            local_files = os.listdir(ftp_config_2["local_directory"])  # Initialize the list for local files

            # Connect to server_2
            while True:
                try:
                    ftp2 = FTP()
                    ftp2.connect(ftp_config_2["ftp_server"])
                    ftp2.login(ftp_config_2["username"], ftp_config_2["password"])
                    break  # Break the loop if the connection is successful
                except TimeoutError:
                    # Handle the timeout error (server not available)
                    print("Server not available. Retrying...")
                    time.sleep(5)

            uploading_files = []  # Initialize the list for downloaded files
            print(f'Connected to {ftp_config_2["network_name"]} as {ftp_config_2["username"]}. Uploading files.')

            # Upload files to server_2
            upload_files(ftp2, ftp_config_2["local_directory"],uploading_files)
            
            
            # Play a sound to indicate successful transfer
            if uploading_files:
                play_notification_sound(beep1)
                upload_log_files(ftp2, ftp_config_2["local_directory"])
            
            # Remove uploaded files from the local directory
            for local_filename in local_files:
                if not local_filename.endswith(".log"):
                    local_filepath = os.path.join(ftp_config_2["local_directory"], local_filename)
                    os.remove(local_filepath)

            # Close the connection to server_2
            ftp2.quit()

            

            
        except Exception as e:
            print(f"Error downloading from FTP server 1: {str(e)}")
    # Sleep before checking again
    time.sleep(5)