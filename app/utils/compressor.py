import os
from PIL import Image
import math
import traceback, os, shutil
from random import randint
import json
import PyPDF2
from PyPDF2 import PdfReader
from PIL import Image
from pdf2image import convert_from_path


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


def get_pdf_page_count(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        page_count = pdf_reader.numPages
        return page_count

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1000)))
   p = math.pow(1000, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


def convert_pdf_to_images(pdf_path, output_directory, dpi, image_quality=50):
    print("dpi=", dpi)
    print("image_quality==",image_quality)
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Convert PDF pages to images
    images = convert_from_path(pdf_path, dpi=int(dpi), grayscale=False)

    # Save each image with low quality
    for i, image in enumerate(images):
        image_path = os.path.join(output_directory, f"page_{i + 1}.jpg")
        image.save(image_path, format="JPEG", quality=int(image_quality))

    print("\nPDF pages converted to images successfully.")
    return output_directory

    

def merge_images_to_pdf(image_directory, output_pdf):
    # Verify if the provided image directory exists
    if not os.path.exists(image_directory):
        return "Invalid image directory!"

    # Get image files from the directory
    image_files = [file for file in os.listdir(image_directory) if ((file.endswith('.png') or (file.endswith('.jpg'))))]
    
    # Sort the image files based on page number
    image_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    # Merge images into a PDF
    for image_file in image_files:
        image_path = os.path.join(image_directory, image_file)
        img = Image.open(image_path)
        pdf_path = os.path.join(image_directory, image_file[:-4] + '.pdf')
        img.save(pdf_path, 'PDF', resolution = 100.0)

    pdf_merger = PyPDF2.PdfFileMerger()

    all_pdfs = [file for file in os.listdir(image_directory) if (file.endswith('.pdf'))]
    all_pdfs.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    for filename in all_pdfs:
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(image_directory, filename)
            pdf_merger.append(pdf_path)
    final_pdf_path = os.path.join(output_pdf, 'final_output.pdf')
    pdf_merger.write(final_pdf_path)
    pdf_merger.close()

    pdf_size = os.path.getsize(final_pdf_path)

    return pdf_size, final_pdf_path


def calculate_dpi(image_path):
    image = Image.open(image_path)
    print("\n____Image_information________",image.info)
    width, height = image.size 
    print(f"width= {width}, height= {height}")

    try:
        # Get the size of the image in inches
        width_inch = width / image.info['dpi'][0]
        height_inch = height / image.info['dpi'][1]

        dpi = max(width_inch, height_inch)
    except:
        print("not able to read its dpi")
        return None 

    return round(dpi)



