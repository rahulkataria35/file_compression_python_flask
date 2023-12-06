"""COMMON file"""
import random
import datetime


def get_random_dir_file_name(prefix, suffix):
    """
    generates random file/ directory name
    """
    time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    random_no = ''.join(random.sample('0123456789', 4))
    return prefix + time_stamp + random_no + suffix
