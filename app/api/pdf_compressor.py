import os
import traceback
from flask import Blueprint, jsonify,request
import shutil
from utils.compressor import convert_size, get_pdf_page_count, convert_pdf_to_images, merge_images_to_pdf
from common.common import get_random_dir_file_name, download_file


pdf_compressor_app = Blueprint("pdf_compressor_app", __name__, url_prefix="/compression_api")

@pdf_compressor_app.route("/pdf", methods=['POST'])
def pdf():
    try:
        payload = request.get_json()
        target_compression_size = payload['target_compression_size']
        pdf_url = payload['pdf_url']

    except Exception as ex:

        meta = {
            'exc_type': type(ex).__name__,
            'exc_message': traceback.format_exc().split('\n')
        }
        return jsonify(
            {"RESPONSE_TYPE": "E", "RESPONSE_MESSAGE": "Key Missing", "meta": meta})
    
    # download the file
    try:  
        temp_folder_name = get_random_dir_file_name("../temp/", '_pdf_compressor/')

        isExist = os.path.exists(temp_folder_name)
        if not isExist:
            os.makedirs(temp_folder_name)
        
        downloaded_pdf_file = temp_folder_name + "input_file.pdf"

        download_file(pdf_url, downloaded_pdf_file)

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

    # recheck
    original_size = os.path.getsize(downloaded_pdf_file)

    if original_size <= target_size_bytes:
        try:
            shutil.rmtree("../temp/")
        except:
            pass
        
        return jsonify({"RESPONSE_TYPE": "I", 
                        "RESPONSE_MESSAGE": f"The original file({convert_size(original_size)}) is already smaller than the Target Size {convert_size(target_size_bytes)}.",
                        "MESSAGE": "This API is only used for Compression"})


    # check the no. of pages in pdf
    pages_in_pdf = get_pdf_page_count(downloaded_pdf_file)
    
    # set limit according to requirement
    if pages_in_pdf > 70:
        try:
            shutil.rmtree('../temp/')
        except:
            pass
        
        return jsonify({"RESPONSE_TYPE": "E", 
                        "RESPONSE_MESSAGE": f"The maximum number of pages in a PDF for this API is 70. but you have {pages_in_pdf} pages PDF.",
                        "MESSAGE": " Please try the new pdf, which includes fewer than 70 pages, again"})


    
    # create pdf to image directory
    pdf_to_images_folder = get_random_dir_file_name("../temp/", '_pdf_to_images/')
    isExist = os.path.exists(pdf_to_images_folder)
    if not isExist:
        os.makedirs(pdf_to_images_folder)
    
    # create a directory where we'll merge these images and then create a pdf 
    merged_pdf_folder = get_random_dir_file_name("../temp/", '_final_pdf/')
    isExist = os.path.exists(merged_pdf_folder)
    if not isExist:
        os.makedirs(merged_pdf_folder)

    # start
    if float(convert_size(original_size)[:-3]) > 100:   # checking if pdf size is more than 100 MB 
        dpi = 200
    else:
        dpi = 100
    
    # convert original pdf into images and then merge it
    convert_pdf_to_images(downloaded_pdf_file, pdf_to_images_folder, dpi,  50)
    pdf_size, pdf_path = merge_images_to_pdf(pdf_to_images_folder, merged_pdf_folder)
    
    print("firstly_compreesed_pdf_size___", convert_size(pdf_size))
    
    # checking, this is already compreesed or not
    if pdf_size >= original_size:
            try:
                shutil.rmtree("../temp/")
            except:
                pass

            return jsonify({"RESPONSE_TYPE": "E", 
                            "RESPONSE_MESSAGE": f"The original file({convert_size(original_size)}) is already a compressed file.",
                            })
    dpi = 100
    image_quality = 40
    prev_size = original_size

    response_msg = {"msg": "Success"}

    while pdf_size > target_size_bytes: 
        convert_pdf_to_images(pdf_path, pdf_to_images_folder, dpi, image_quality)
        pdf_size, pdf_path = merge_images_to_pdf(pdf_to_images_folder, merged_pdf_folder)
        
        #checking, if after compression size will not decreasing, that means already compressed.
        print("prev_size-----------------", convert_size(prev_size))
        print("now_pdf_size is_______ ", convert_size(pdf_size))

        if pdf_size > prev_size:
            response_msg["msg"] = "Further compression is not possible."
            break

        prev_size = pdf_size
        image_quality-= 5
        
        if image_quality < 10:
            response_msg["msg"] = "Further compression is not possible."
            break
    
    response = {}
    response["doc_size_after"] = convert_size(pdf_size)
    response["doc_size_before"] = convert_size(os.path.getsize(downloaded_pdf_file))
    response["compressed_msg"]= response_msg["msg"]

    
    try:
        shutil.rmtree("../temp/")
        
    except:
        pass    
    
    return jsonify({"RESPONSE_TYPE": "I", "RESPONSE_MESSAGE": "SUCCESS", "DATA": response})

    
