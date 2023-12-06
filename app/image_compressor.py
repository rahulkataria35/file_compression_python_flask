import os
import random
import traceback
from flask import Blueprint, jsonify,request
import datetime
import shutil
# from utils.compressor import compress_image, convert_size
import math
import traceback, os, shutil
from random import randint
import json
import PyPDF2
from PIL import Image
from pdf2image import convert_from_path
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



def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1000)))
   p = math.pow(1000, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def compress_image(input_path, output_path, quality):
    try:
        
        # Open the image
        image = Image.open(input_path)
        # Save the image with reduced quality
        image.save(output_path, optimize=True, quality=int(quality))
        # Get the new file size
        compressed_size = os.path.getsize(output_path) / (1000 * 1000)  # in MB
        print("\nFile compressed successfully. New size: {:.2f} MB".format(compressed_size))

        # get the compressed size in bytes
        compressed_size_in_bytes = os.path.getsize(output_path)
        
        return compressed_size_in_bytes, output_path

    except Exception as e:
        print("Error compressing the image file:", str(e))

def get_random_dir_file_name(prefix, suffix):
    """
    generates random file/ directory name
    """
    time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    random_no = ''.join(random.sample('0123456789', 4))
    return prefix + time_stamp + random_no + suffix

img_compressor_app = Blueprint("img_compressor_app", __name__, url_prefix="/compression_api")

@img_compressor_app.route("/img", methods=['POST', 'GET'])
def img():
    try:
        payload = request.get_json()
        target_compression_size = payload['target_compression_size']
        image_url = payload['image_url']
    except:
        return jsonify({"response":"key missing"})
    
    try:  
        temp_folder_name = get_random_dir_file_name("../temp/", '_image_compressor/')

        isExist = os.path.exists(temp_folder_name)
        if not isExist:
            os.makedirs(temp_folder_name)
        

        final_file_path = temp_folder_name+ "input." + image_url.split(".")[-1]

        download_file(image_url, final_file_path)

    except Exception as ex:

        meta = {
            'exc_type': type(ex).__name__,
            'exc_message': traceback.format_exc().split('\n')
        }
        return jsonify(
            {"RESPONSE_TYPE": "E", "RESPONSE_MESSAGE": "Error while downloading file", "meta": meta})
        
        
    
    try:
        # Convert the target size to bytes
        if target_compression_size.endswith('KB'):
            target_size_bytes = int(target_compression_size[:-2]) * 1000
        elif target_compression_size.endswith('MB'):
            target_size_bytes = int(target_compression_size[:-2]) * 1000 * 1000
        
    except Exception as ex:
        meta = {
            'exc_type': type(ex).__name__,
            'exc_message': traceback.format_exc().split('\n')
        }
        return jsonify(
            {"STATUS": "E", "RESPONSE_MESSAGE": "Invalid target size format! Please use format 'X KB' or 'Y MB'", "meta": meta})

    try:
        if '.jpg' in final_file_path:
            # Check if the source file is already smaller than the target size
            original_size = os.path.getsize(final_file_path)

            if original_size <= target_size_bytes:
                try:
                    shutil.rmtree(temp_folder_name)
                except:
                    pass
                return jsonify({"RESPONSE_TYPE": "I", 
                                "RESPONSE_MESSAGE": f"The original file({convert_size(original_size)}) is already smaller than the Target Size {convert_size(target_size_bytes)}.",
                                "MESSAGE": "This API is only used for Compression"})


            final_path = temp_folder_name + "output.jpg"

            ###_________________start__________________
            image_quality = 100
            compressed_size_in_bytes , output_path = compress_image(final_file_path, final_path, image_quality)
            print("\noriginal size==", convert_size(compressed_size_in_bytes))

            while compressed_size_in_bytes > target_size_bytes:
                print("\nimage_quality________", image_quality)
                compressed_size_in_bytes , output_path = compress_image(output_path, final_path, image_quality)
                image_quality -= 5
                if image_quality == 10:
                    break
            
        
            response = {}
            try:
                encoded_graph = image_to_base64(final_path)
                image_base64 = encoded_graph.decode("utf-8")

                response['final_img'] = image_base64
                response["doc_size_after"] = convert_size(compressed_size_in_bytes)
                response["doc_size_before"] = convert_size(os.path.getsize(final_file_path))
                response["msg"]= 'Success'
            except Exception as ex:

                meta = {
                    'exc_type': type(ex).__name__,
                    'exc_message': traceback.format_exc().split('\n')
                }
                return jsonify(
                    {"RESPONSE_TYPE": "E", "RESPONSE_MESSAGE": "Error while encrypting file", "meta": meta})

            
            try:
                shutil.rmtree(temp_folder_name)
            except:
                pass
            return jsonify({"RESPONSE_TYPE": "I", "RESPONSE_MESSAGE": "SUCCESS", "DATA": response})
    except Exception as ex:

        meta = {
            'exc_type': type(ex).__name__,
            'exc_message': traceback.format_exc().split('\n')
        }
        return jsonify(
            {"RESPONSE_TYPE": "E", "RESPONSE_MESSAGE": "Error while downloading file", "meta": meta})

    
