#!/usr/bin/python

import os, sys, subprocess, re, json, traceback

DEBUG = True
E_DIR = '_everything'

def main():
    # do a basic sanity check that the first arg is the right dir with JPEG files
    devnull = open(os.devnull, 'wb')
    if len(sys.argv) not in [2, 3] or subprocess.call('ls ' + os.path.join(sys.argv[1], '*.jpg'), shell=True, stdout=devnull, stderr=devnull) != 0:
        print('Wrong arguments!')
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[2] == '--e':
        global DEBUG
        DEBUG = False

    # create E_DIR if it's not there
    if not os.path.isdir(os.path.join(sys.argv[1], E_DIR)):
        os.mkdir(os.path.join(sys.argv[1], E_DIR))

    walk_dir(sys.argv[1])

def walk_dir(root_d):
    # first go over all files and move them to right dirs
    print('* Running with DEBUG={}'.format(DEBUG))
    print('------ PROCESS FILES')
    for f in os.listdir(root_d):
        ff = os.path.join(root_d, f)

        if os.path.isfile(ff):
            if re.match('^\d{4}-\d{2}-\d{2}\.[A-Za-z]+$', f):
                date_file_move(root_d, f)
            else:
                album_file_move(root_d, f)

    # now go over all dirs and rename/move them
    print('------ PROCESS DIRECTORIES')
    for f in os.listdir(root_d):
        if f == E_DIR:
            continue
        ff = os.path.join(root_d, f) 
        
        if os.path.isdir(ff):
            if re.match('^\d{4}-\d{2}-\d{2}.*$', f):
                date_dir_process(root_d, f)
            else:
                album_dir_process(root_d, f)

def album_dir_process(root_d, d):
    this_d = os.path.join(root_d, d)
    print('--- Process album dir {}'.format(this_d))

    try:
        # see if it's empty
        path, dirs, files = next(os.walk(this_d))
        files.remove('metadata.json')
        if len(files) == 0:
            log('Removing empty directory {}'.format(this_d))
            return

        # Rename directory based on metadata.json
        with open(os.path.join(root_d, d, 'metadata.json')) as f:
            md = json.load(f)
            name = md['albumData']['title'].encode('utf-8')
            f.close()
    
        old_d = os.path.join(root_d, d)
        new_d = os.path.join(root_d, name)
        if d != name:
            if not DEBUG:
                os.rename(old_d, new_d)
            else:
                new_d = old_d # hack
            log('Renaming _Album dir_ {} to {}'.format(old_d, new_d))

        # Delete metadata.json
        mf = os.path.join(new_d, 'metadata.json')
        if not DEBUG:
            os.remove(mf)
        log('Removing album metadata file {}'.format(mf))

        # Remove parens from all files just in case
        for f in os.listdir(new_d):
            old_f = os.path.join(new_d, f)
            new_f = os.path.join(new_d, filename_filter(f))
            if old_f != new_f:
                if not DEBUG:
                    os.rename(old_f, new_f)
                log('Cleaning file name {} to {}'.format(old_f, new_f))
    except OSError as e:
        log('Something went wrong...', e, sys.exc_info())

def date_dir_process(root_d, d):
    try:
        old_dir = os.path.join(root_d, d)
        new_dir = os.path.join(root_d, E_DIR)
        
        print('--- Process date dir {}'.format(old_dir))

        # delete metadata.json
        m_f = os.path.join(old_dir, 'metadata.json')
        if not DEBUG and os.path.exists(m_f):
            os.remove(m_f)
        log('Deleted "{}"'.format(m_f))

        # move all files to E_DIR
        for f in os.listdir(old_dir):
            try:
                old_f = os.path.join(old_dir, f)
                new_f = os.path.join(new_dir, d + '-' + filename_filter(f))
                if not DEBUG:
                    os.rename(old_f, new_f)
                log('Moved _Date dir file_ "{}" to "{}"'.format(old_f, new_f))
            except OSError as e:
                log('Could not move file {} to {}'.format(old_f, new_f), e, sys.exc_info())

        # now remove dir itself
        if not DEBUG:
            os.rmdir(old_dir)
        log('Deleted _Date dir_ {}'.format(old_dir))
    except OSError as e:
        log('Something went wrong...', e, sys.exc_info())

def filename_filter(fn):
    return ''.join((filter(lambda x: x not in ['(', ')'], fn)))

def album_file_move(root_d, f):
    try:
        old_f = os.path.join(root_d, f)
        # assume that the directory name is same as file name without extension
        new_f = os.path.join(root_d, f.split('.')[0], f)
        if not DEBUG:
            os.rename(old_f, new_f)
        log('Moved _Album file_ "{}" to "{}"'.format(old_f, new_f))
    except OSError as e:
        log('Something went wrong...', e, sys.exc_info()) 

def date_file_move(root_d, f):
    try:
        old_f = os.path.join(root_d, f)
        new_f = os.path.join(root_d, E_DIR, f)
        if not DEBUG:
            os.rename(old_f, new_f)
        log('Moved _Date file_ "{}" to "{}"'.format(old_f, new_f))
    except OSError as e:
        log('Something went wrong...', e, sys.exc_info())

def log(l, e=None, ei=None):
    if not e:
        print('I | {}'.format(l))
    else:
        print('E | {}'.format(l))
        print(traceback.format_exc(ei))

if __name__ == "__main__":
    main()
