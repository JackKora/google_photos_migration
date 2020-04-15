#!/usr/bin/python

import os, sys, subprocess, re, json, traceback

DRYRUN = True
NO_ALBUM_DIR = '_NO_ALBUMS'
DATE_NAME_REGEX = '^(\d{1,4}-)+\d{1,4}( #2)?(\.[A-Za-z]{3,4})?$'
METADATA = 'metadata.json'

def main():
    init()

    delete_media_metadata(sys.argv[1])
    move_files(sys.argv[1])
    massage_folders(sys.argv[1])

def delete_media_metadata(parent_d):
    """
    Clean up all media metadata .json files except album metadata.json ones
    """
    info('------ CLEAN UP MEDIA METADATA')
    for root, dirs, files in os.walk(parent_d):
        for f in files:
            if os.path.splitext(f)[1].lower() == '.json':
                delete(f, 'useless metadata')

def move_files(parent_d):
    """
    Go over all top level files and move them to right dirs
    and delete all non metadata.json files (photo metadata)
    """
    info('------ PROCESS FILES')
    for f in os.listdir(parent_d):
        ff = os.path.join(parent_d, f)

        if os.path.isfile(ff):
            if re.match(DATE_NAME_REGEX, f):
                file_move(parent_d, f, 'date')
            else:
                file_move(parent_d, f, 'album')

def massage_folders(parent_d):
    # now go over all dirs and rename/move them
    info('------ PROCESS DIRECTORIES')
    for d in os.listdir(parent_d):
        if d == NO_ALBUM_DIR:
            continue # skip this one
        dd = os.path.join(parent_d, d)

        if os.path.isdir(dd):
            remove_empty_dir(dd)

            if re.match(DATE_NAME_REGEX, d):
                process_date_dir(parent_d, d)
            else:
                process_album_dir(parent_d, d)

def process_album_dir(parent_d, d):
    this_d = os.path.join(parent_d, d)
    info('--- Process album dir {}'.format(this_d))

    new_d = rename_album_dir(parent_d, d)

    # Delete metadata.json that's no longer needed
    delete(os.path.join(new_d, METADATA), 'no longer needed')

    # Remove parens from all files just in case
    clean_filenames(new_d)

def clean_filenames(parent_d):
    """
    Rename all files in the dir to remove parenthesis, etc
    """
    for f in os.listdir(parent_d):
        old_f = os.path.join(parent_d, f)
        new_f = os.path.join(parent_d, filename_filter(f))
        if old_f != new_f:
            if DRYRUN:
                info('Dry run: Would rename filename {} to {}'.format(old_f, new_f))
            else:
                rename(old_f, new_f, 'cleaned file')

def process_date_dir(parent_d, d):
    old_dir = os.path.join(parent_d, d)
    new_dir = os.path.join(parent_d, NO_ALBUM_DIR)
    info('--- Process date dir {}'.format(old_dir))

    delete(os.path.join(old_dir, METADATA), 'useless') # delete metadata.json

    # move all files to NO_ALBUM_DIR
    for f in os.listdir(old_dir):
        old_f = os.path.join(old_dir, f)
        new_f = os.path.join(new_dir, d + '-' + filename_filter(f))
        rename(old_f, new_f, 'date file')

    delete(old_dir, 'date dir') # now remove dir itself

def rename_album_dir(parent_d, d):
    """
    Read metadata.json, rename the dir, and return the new name
    """
    mf = os.path.join(parent_d, d, METADATA)
    try:
        with open(mf) as f:
            md = json.load(f)
            name = md['albumData']['title'].encode('utf-8')
            # TODO: filter out unicode, ascii only
            f.close()
    except OSError as e:
        error('Could not read from {}, skipping _album_ dir rename'.format(mf), e, sys.exc_info())
        return os.path.join(parent_d, d)

    return rename(os.path.join(parent_d, d), os.path.join(parent_d, name), 'album dir')

def filename_filter(fn):
    return ''.join((filter(lambda x: x not in ['(', ')'], fn)))

def file_move(parent_d, f, type):
    old_f = os.path.join(parent_d, f)
    if type == 'album':
        new_f = os.path.join(parent_d, f.split('.')[0], f) # assume dir name is same as file name w/o extension
    elif type == 'date':
        new_f = os.path.join(parent_d, NO_ALBUM_DIR, f)
    else:
        error('Unknown file type {}'.format(type))
        return

    rename(old_f, new_f, type + ' file')

def remove_empty_dir(d):
    path, dirs, files = next(os.walk(d))
    files.remove(METADATA) # if this is the only file, remove dir still
    if len(files) == 0:
        delete(d, 'empty dir')

def rename(old_f, new_f, msg):
    if old_f == new_f:
        return old_f
    elif DRYRUN:
        info('Dry run: would rename [{}] {} to {}'.format(msg, old_f, new_f))
    else:
        try:
            os.rename(old_f, new_f)
            log('Renamed [{}] {} to {}'.format(msg, old_f, new_f))
            return new_f # it actually got renamed

        except OSError as e:
            error('Could not rename [{}] {} to {}'.format(msg, old_f, new_f), e, sys.exc_info())
    return old_f # it never got renamed

def delete(f, msg):
    if DRYRUN:
        info('Dry run: would be deleting [{}] {}'.format(msg, f))
    else:
        try:
            if os.path.isdir():
                os.rmdir(f)
            else:
                os.remove(f)
            info('Deleted [{}] {}'.format(msg, f))
        except OSError as e:
            error('Could not delete [{}] {}'.format(msg, f), e, sys.exc_info())

def init():
    # do a basic sanity check that the first arg is the right dir with JPEG files
    devnull = open(os.devnull, 'wb')
    if len(sys.argv) not in [2, 3] or subprocess.call('ls ' + os.path.join(sys.argv[1], '*.jpg'), shell=True, stdout=devnull, stderr=devnull) != 0:
        print('Wrong arguments!')
        print('- first arg: directory with images')
        print('- second arg: optional -e to execute the changes (the default is a dry run)')
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[2] == '-e':
        global DRYRUN
        DRYRUN = False

    # create NO_ALBUM_DIR if it's not there
    if not os.path.isdir(os.path.join(sys.argv[1], NO_ALBUM_DIR)):
        os.mkdir(os.path.join(sys.argv[1], NO_ALBUM_DIR))

def info(msg):
    log(msg, 'I')

def warn(msg):
    log(msg, 'W')

def error(msg, exc=None, exc_info=None):
    log(msg, 'E', exc, exc_info)

def log(msg, level, exc=None, exc_info=None):
    if not exc:
        print('{} | {}'.format(level, msg))
    else:
        print('{} [{}] | {}'.format(level, msg, exc))
        print(traceback.format_exc(exc_info))

if __name__ == "__main__":
    main()
