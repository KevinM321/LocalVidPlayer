import re
import ctypes
import subprocess
from config.config_utils import *

def rename_vid(name, ext):
    changed = False

    if ext != "mp4":
        ext = "mp4"
        changed = True

    if not bool(re.match(r'^[A-Za-z0-9._\-\[\]\(\)]+$', name)):
        name = re.sub(r'[^A-Za-z0-9._\-\[\]\(\)]', '_', name)
        changed = True

    return (name, ext, changed)


def get_vid_ctime(path : str, title : str, platform : str):
    if platform == "Windows":
        return os.path.getctime(path + "\\" + title)
    else:
        return os.path.getctime(path + title)
    

def preprocess_vids(path : str, modify: bool, platform : str, hide: bool) -> list:
    titles = os.listdir(path)
    if not modify:
        return titles

    vids = []
    for title in titles:
        parts = title.split('.')
        name = '.'.join(parts[:-1])
        ext = parts[-1]

        name, ext, changed = rename_vid(name, ext)
        new_title = ".".join((name, ext))

        if changed:
            if os.path.isfile(path + new_title):
                name += "_D"
                new_title = ".".join((name, ext))

        if hide:
            if platform == "Windows" and not bool(ctypes.windll.kernel32.GetFileAttributesW(path +
                                                                                            new_title) & 0x2):
                os.rename(path + title, path + new_title)
                subprocess.call(['attrib', '+h', path + new_title])
            elif platform == "MacOS" or "Linux":
                new_title = "." + new_title if parts[0] != "" else new_title
                os.rename(path + title, path + new_title)

        if platform == "Windows":
            vids.append((new_title, get_vid_ctime(path, new_title, platform)))
        else:
            vids.append((new_title, get_vid_ctime(path, new_title, platform)))

    return vids


# conf = BackEndConfig()
# print(preprocess_vids(conf.get('vids_path'), conf.get('preprocess', 'modify'),
#                       conf.get('preprocess', 'platform'), conf.get('preprocess', 'hide'))[:10])
