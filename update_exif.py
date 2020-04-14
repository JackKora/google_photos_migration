#!/usr/bin/python

import os, sys, datetime, json, subprocess

DEBUG = True
JSON = '.json'
EXIFTOOL = 'exiftool'

def main():
    init()
    walk_dir(sys.argv[1])

def walk_dir(root_d):
    """
    Recursively walk all directories and update EXIF DateTimeOriginal from metadata
    """

    for f in os.listdir(root_d):
        ff = os.path.join(root_d, f)

        if os.path.isfile(ff) and is_image(ff) and not is_exif_set(ff):
            timestamp = get_metadata_timestamp(ff)
            if timestamp:
                update_exif(ff, timestamp)

        if os.path.isdir(ff):
            walk_dir(ff)

def update_exif(f, timestamp):
    devnull = open(os.devnull, 'wb')
    run = '{} -overwrite_original "-DateTimeOriginal={}" "{}"'.format(EXIFTOOL, timestamp, f)
    res = subprocess.call(run, shell=True, stdout=devnull, stderr=devnull)
    if res == 0:
        info('Set EXIF DateTimeOriginal in {} to {}'.format(f, timestamp))
    else:
        error('Could not update EXIF DateTimeOriginal in {}'.format(f))

def is_exif_set(f):
    devnull = open(os.devnull, 'wb')
    run = '{} "{}" | grep "Date/Time Original"'.format(EXIFTOOL, f)
    res = subprocess.call(run, shell=True, stdout=devnull, stderr=devnull)
    return res == 0

def get_metadata_timestamp(f):
    """
    Check for <file>.json and then <file>.<ext>.json for metadata
    """
    if os.path.exists(f + JSON):
        return read_metadata(f + JSON)
    elif os.path.exists(os.path.splitext(f)[0] + JSON):
        return read_metadata(os.path.splitext(f)[0] + JSON)
    else:
        warn('No metadata exists for {}'.format(f))
        return None

def read_metadata(mf):
    with open(mf) as f:
        md = json.load(f)
        f.close()
    return datetime.datetime.fromtimestamp(float(md['photoTakenTime']['timestamp']))

def is_image(f):
    """
    Only flag JPEG and PNG. GIFs don't support EXIF and HEIC are guaranteed to have timestamps.
    """
    if os.path.splitext(f)[1].lower() in ['.jpg', '.jpeg', '.png']:
        return True
    else:
        return False

def walk_error(e):
    error(e)

def info(msg):
    log(msg, 'I')

def warn(msg):
    log(msg, 'W')

def error(msg):
    log(msg, 'E')

def log(msg, level):
    print('{} | {}'.format(level, msg))

def init():
    # do a basic sanity check that the first arg is the right dir with JPEG files
    devnull = open(os.devnull, 'wb')
    if len(sys.argv) not in [2, 3] or subprocess.call('ls ' + os.path.join(sys.argv[1], '*.jpg'), shell=True, stdout=devnull, stderr=devnull) != 0:
        print('Wrong arguments!')
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[2] == '--e':
        global DEBUG
        DEBUG = False

    if os.environ.get('EXIFTOOL'):
        global EXIFTOOL
        EXIFTOOL = os.environ.get('EXIFTOOL')

if __name__ == "__main__":
    main()
