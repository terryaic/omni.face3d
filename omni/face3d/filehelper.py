
import omni.client
import omni.kit
import omni.usd

import asyncio
import os
from pxr import UsdGeom, Gf, Tf

import requests
import urllib.request
import sys
import json
from requests_toolbelt import MultipartEncoder
import zipfile

def get_mimetype(str1):
    name = str1.lower()
    if name.endswith("png"):
        return "image/png"
    elif name.endswith("jpg") or name.lower().endswith("jpeg"):
        return "image/jpeg"
    elif name.endswith("zip"):
        return "application/zip"
    else:
        return "application/binary"

def get_img_type(str1):
    name = str1.lower()
    if name.endswith("png"):
        return "PNG"
    elif name.endswith("jpeg") or name.endswith("jpg"):
        return "JPEG"
    elif name.endswith("bmp"):
        return "BMP"
    else:
        return None

URL = "https://live.chinaedgecomputing.com/ptt/person/face3d"

def upload_file(in_file):
    ret_url = None
    filename = os.path.basename(in_file)
    with open(in_file, 'rb') as fp:
        fs = fp.read()
    m = MultipartEncoder(
            fields={
                'photo': (filename, fs, get_mimetype(filename)),
                'userid': "omniverse"
            }
        )
    try:
        r = requests.post(URL, data=m,
        headers={'Content-Type': m.content_type})
        if r.status_code == 200:
            text = r.content.decode("utf8")
            obj = json.loads(text)
            print(obj)
            if obj['ret']:
                ret_url = obj['url']
    except Exception as e:
        print(e)
    return ret_url

def download_file(outpath, url):
    response = requests.get(url)
    if response.status_code == 200:
        filename = url[url.rfind("/")+1:]
        local_filename = os.path.join(outpath, filename)
        with open(local_filename, "wb") as f:
            f.write(response.content)
        return local_filename
    return None

def unzip_file(in_file, outpath):
    filename = os.path.basename(in_file)
    filename = filename[:filename.rfind(".")]
    filepath = os.path.join(outpath, filename)
    os.mkdir(filepath)
    zf = zipfile.ZipFile(in_file)
    zf.extractall(filepath)
    return filepath

async def convert(in_file, out_file):
    # This import causes conflicts when global?
    import omni.kit.asset_converter as assetimport

    # Folders must be created first through usd_ext of omni won't be able to create the files creted in them in the current session.
    out_folder = out_file[0 : out_file.rfind("/") + 1]

    # only call create_folder_on_omni if it's connected to an omni server
    if out_file.startswith("omniverse://"):
        await create_folder_on_omni(out_folder + "materials")

    def progress_callback(progress, total_steps):
        pass

    converter_context = omni.kit.asset_converter.AssetConverterContext()
    # setup converter and flags
    converter_context.as_shapenet = True
    converter_context.single_mesh = True
    instance = omni.kit.asset_converter.get_instance()
    task = instance.create_converter_task(in_file, out_file, progress_callback, converter_context)

    success = True
    while True:
        success = await task.wait_until_finished()
        if not success:
            await asyncio.sleep(0.1)
        else:
            break
    return success