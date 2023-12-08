import os
import random
import traceback
from flask import Blueprint, jsonify,request
import datetime
import shutil
from utils.compressor import compress_image, convert_size
from common.common import get_random_dir_file_name, download_file, image_to_base64


img_compressor_app = Blueprint("img_compressor_app", __name__, url_prefix="/compression_api")

@img_compressor_app.route("/img", methods=['POST'])
def img():
    try:
        payload = request.get_json()
        target_compression_size = payload['target_compression_size']
        image_url = payload['image_url']
    except:
        return jsonify({"response":"key missing"})
    
    try:  
        temp_folder_name = get_random_dir_file_name("./temp/", '_image_compressor/')

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
                shutil.rmtree("./temp/")
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

    
