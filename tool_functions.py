import os
import tkinter as tk
import random
import time
import datetime
from PIL import Image


def batch_rename(dir):
    """批量重命名dir目录下的gif后缀文件，将其改为png后缀"""
    for file in os.listdir(dir):
        if file.endswith('.gif'):
            os.renames(os.path.join(dir, file), os.path.join(dir, file[0:-3]+'png'))
    print("rename finished!")


def batch_crop(dir):
    """批量裁剪dir下面的图片,并保存在cropped文件夹下"""
    for img in os.listdir(dir):
        image = Image.open(os.path.join(dir, img))
        cropped = image.crop((40, 50, 150, 197))
        cropped.save('cropped/'+img)
    print("Batch Crop Finished!")
