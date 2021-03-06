import pathlib
import shutil
from operator import itemgetter
import hashlib
import os

INVALID_VALUE = -1
NO_ERROR_VALUE = 0

__name__ = "my_utils"
__version__ = 1.0


def get_file_name_from_path(fullpathtofile: str):
    """ return filename from full path file name """
    path = pathlib.Path(fullpathtofile)
    return str(path.name)


def get_folder_name_from_path(strfullpathtofile: str):
    """ return folder name from full path file name """
    mypath = pathlib.Path(strfullpathtofile).absolute()
    return str(mypath)


def get_folder_files_info(str_full_folder_path_name: str):
    """Return list of files in folder str_full_folder_path_name.
    Each list item contains a tuple of two elements (filename_without_path, file_size_in_bytes).
    Returned tuple sorted by file_size ascending """
    # flist = None

    lpath = pathlib.Path(str_full_folder_path_name)
    if not lpath.is_dir():
        return None  # return None if str_full_folder_path_name not folder

    flist = list()
    # enumerating files ONLY!!!
    for child in lpath.iterdir():
        if child.is_file():
            file = pathlib.Path(child.absolute())
            flist.append((child.name, file.stat().st_size))

    return tuple(sorted(flist, key=itemgetter(1)))


def get_hash_file(path: str, algorithm="md5", bufsize=4096) -> bytes:
    """return hash of file"""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(bufsize), b""):
            h.update(chunk)

    return h.digest()


def is_folder_exist(full_folder_path: str):
    """check folder for exist and is folder
    return value is Boolean!"""
    folder = pathlib.Path(full_folder_path)
    return folder.is_dir() and folder.exists()


def get_full_file_name(str_folder_owner: str, str_file_name: str):
    """returns the full file name adding the folder name and file name"""
    return str_folder_owner + os.path.sep + str_file_name


def delete_duplicate_file(folder_full_path: str, storage_folder: str = None):
    """move/delete duplicate files of the same size and context in specified folder (folder_full_path).

    folder_full_path - folder where duplicates are searched.
    storage_folder - optional - folder for storage duplicate files
    If the storage_folder is not specified, then duplicate files will be deleted!

    in case of error returns a negative value.
    if successful, returns the number of found duplicate files subjected to move / delete
    """
    ret_val = INVALID_VALUE

    if not is_folder_exist(folder_full_path):
        return ret_val

    # START
    if storage_folder and not is_folder_exist(storage_folder):
        return ret_val

    file_list = get_folder_files_info(folder_full_path)

    if not file_list:  # zero files for compare. exit
        return NO_ERROR_VALUE

    tpl_first = None

    index_file_name, index_file_size = range(2)

    ret_val = NO_ERROR_VALUE

    for item in file_list:
        if tpl_first is None:
            tpl_first = item
            continue
        if item[index_file_size] == tpl_first[index_file_size]:
            fname0 = get_full_file_name(folder_full_path, item[index_file_name])
            fname1 = get_full_file_name(folder_full_path, tpl_first[index_file_name])
            h0 = get_hash_file(fname0)
            h1 = get_hash_file(fname1)
            if h0 == h1:
                if not storage_folder:
                    f = pathlib.Path(fname0)
                    f.unlink()  # delete file
                    ret_val += 1
                else:
                    dst = get_full_file_name(storage_folder, item[index_file_name])  # make full file name
                    # move duplicate file to storage folder
                    shutil.move(fname0, dst, copy_function=shutil.copy)
                    ret_val += 1
        else:  # file size not equals
            tpl_first = item
            continue

    return ret_val
