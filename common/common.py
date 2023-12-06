"""COMMON file"""
import random
import datetime
import base64
import requests


def image_to_base64(f):
    with open(f, 'rb') as image:
        encoded_string = base64.b64encode(image.read())
    return encoded_string



def download_file(url, file_path):
    try:
        # Send a HTTP GET request to the URL
        response = requests.get(url)
        
        # Check if the response was successful (status code 200)
        if response.status_code == 200:
            # Open the file in binary mode and write the response content
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print("File downloaded successfully.")
            
        else:
            print(f"Download failed. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        
    except IOError as e:
        print(f"An error occurred while saving the file: {e}")
        
    except Exception as e:
        print(f"An unknown error occurred: {e}")




def get_random_dir_file_name(prefix, suffix):
    """
    generates random file/ directory name
    """
    time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    random_no = ''.join(random.sample('0123456789', 4))
    return prefix + time_stamp + random_no + suffix
