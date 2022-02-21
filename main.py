import argparse
import os
from functools import partial

import yaml
from multiprocessing import Pool
from pprint import pprint

from PIL import Image


def resize_image(path, new_path, settings):
    pprint(settings)
    with Image.open(path) as image:
        if not validate_image(image, settings['filter']):
            return
        file_type = image.format
        filename = image.filename.split('/')[-1]
        image = image.resize(settings['convert']['resize']['resolution'], Image.ANTIALIAS)
        save_kwargs = {
            'format': file_type,
            'quality': settings['convert']['quality']
        }
        exif = image.info.get('exif')
        if exif:
            save_kwargs['exif'] = exif
        image.save(os.path.join(new_path, filename), **save_kwargs)


def validate_image(image, settings_filter):
    if image.format.upper() not in settings_filter['format']:
        print '{} not allowed'.format(image.format)
        return
    if image.size[0] < settings_filter['resolution'][0] or image.size[1] < settings_filter['resolution'][1]:
        print 'file resolution less than minimum'.format(image.format)
        return
    return True


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--path', type=str, help='path to images')
    parser.add_argument('--new_path', type=str, help='path for result')
    parser.add_argument('--settings', type=str, help='path for settings file')

    args = parser.parse_args()
    return args.path, args.new_path, args.settings


def parse_settings(settings_path):
    with open(settings_path) as settings_file:
        return yaml.load(settings_file)


def main():
    path, new_path, settings_path = parse_args()
    settings = parse_settings(settings_path)

    if os.path.isdir(path):
        pool = Pool(settings.get('threads', 1))
        f = partial(resize_image, new_path=new_path, settings=settings)
        pool.map(f, [os.path.join(path, file_image) for file_image in os.listdir(path)])
    else:
        resize_image(path, new_path, settings)


if __name__ == "__main__":
    main()
