#!/usr/bin/env python3
"""utility to move/delete duplicate files of the same size and context in specified folder.

command string parameters:
first parameter:    full_path_to_folder - folder where duplicates are searched.
second parameter:   optional - folder for storage duplicate files """

import argparse
import logging
import pathlib
import sys

# my module
from remove_dublicates import my_utils


def recursive_process_folder(start_folder, trash_folder):
    """
    :param start_folder: Search for duplicate files starts from this folder.
    :param trash_folder: found copies of files are transferred to this folder
    :return:
    """
    ret_val = my_utils.delete_duplicate_file(start_folder, trash_folder)
    logging.info(f"Folder {start_folder} processed.")
    # enumerating
    pth = pathlib.Path(start_folder)
    for child in pth.iterdir():
        try:
            if child.is_dir():
                ret_val += recursive_process_folder(str(child.absolute()), trash_folder)
        except PermissionError:
            folder_name = str(child.absolute())
            logging.warning(f"Access is denied! Folder: {folder_name}")
    # return value
    return ret_val


def main():
    str_storage_folder = None  # default value
    log_file_name = None
    str_search_folder = my_utils.get_folder_name_from_path(sys.argv[0])  # default value

    parser = argparse.ArgumentParser(description="""Utility to recursive search and move/delete duplicate files 
                                                of the same size and context in specified folder.""",
                                     epilog="""If the storage folder is not specified, 
                                                then duplicate files will be deleted!
                                                If the number of command line parameters is zero, 
                                                then the search folder = current folder.""")

    parser.add_argument("--start_folder", type=str, help="The folder with which the recursive search begins")
    parser.add_argument("--recycle_bin", type=str, help="Folder for storing duplicate files.")
    parser.add_argument("--log_file", type=str, help="Log file.")

    args = parser.parse_args()

    if args.log_file:
        log_file_name = args.log_file
    # setup logger start
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if log_file_name:
        handler = logging.FileHandler(log_file_name, "w", "utf-8")
    else:  # ???????????????????????? ???? ?????????? ?????? ??????????-??????????????, ?????????????? ???????????????? ???????????????????? sys.stdout
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
    handler.setFormatter(formatter)  # Pass handler as a parameter, not assign
    root_logger.addHandler(handler)
    # setup logger end

    if args.start_folder:
        str_search_folder = args.start_folder
        if not my_utils.is_folder_exist(str_search_folder):
            logging.critical(f"Invalid path to search folder: {str_search_folder}. Exit!")
            sys.exit(my_utils.INVALID_VALUE)

    if args.recycle_bin:
        if not my_utils.is_folder_exist(args.recycle_bin):
            logging.critical(f"Invalid path to storage folder: {args.recycle_bin}. Exit!")
            sys.exit(my_utils.INVALID_VALUE)
        else:
            str_storage_folder = args.recycle_bin

    # START
    logging.info(f"Search for duplicate files in the folder: {str_search_folder}")
    if log_file_name:
        logging.info(f"Log file name: {log_file_name}")
    if str_storage_folder:
        logging.info(f"Storage folder: {str_storage_folder}")

    ret_val = 0
    ret_val += recursive_process_folder(str_search_folder, str_storage_folder)
    if args.recycle_bin:
        movordel = "moved"
    else:
        movordel = "deleted"
    logging.info(f"Found {ret_val} copies of files. They have been {movordel}.")
    sys.exit(ret_val)


if __name__ == "__main__":
    main()
