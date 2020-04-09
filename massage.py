#!/usr/bin/python

import os, sys, subprocess, re, json

DEBUG = True
E_DIR = '_everything'

def main():
    # do a basic sanity check that the first arg is the right dir with JPEG files
    devnull = open(os.devnull, 'wb')
    if len(sys.argv) not in [2, 3] or subprocess.call('ls ' + os.path.join(sys.argv[1], '*.jpg'), shell=True, stdout=devnull, stderr=devnull) != 0:
        print('Wrong arguments!')
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[2] == '--e':
        DEBUG = False

    # create E_DIR if it's not there
    if not os.path.isdir(os.path.join(sys.argv[1], E_DIR)):
        os.mkdir(os.path.join(sys.argv[1], E_DIR))

    walk_dir(sys.argv[1])

def walk_dir(root_d):
    # first go over all files and move them to right dirs  
    for f in os.listdir(root_d):
        ff = os.path.join(root_d, f)

        if os.path.isfile(ff):
            if re.match('^\d{4}-\d{2}-\d{2}\.[A-Za-z]+$', f):
                date_file_move(root_d, f)
            else:
                album_file_move(root_d, f)

    # now go over all dirs and rename/move them
    for f in os.listdir(root_d):
        if f == E_DIR:
            continue
        ff = os.path.join(root_d, f) 
        
        if os.path.isdir(ff):
            if re.match('^\d{4}-\d{2}-\d{2}$', f):
                date_dir_process(root_d, f)
            else:
                album_dir_process(root_d, f)

def album_dir_process(root_d, d):
    # Rename directory based on metadata.json
    with open(os.path.join(root_d, d, 'metadata.json')) as f:
        md = json.load(f)
    name = md['albumData']['title']
    log('Renaming to {}'.format(name))

    # Delete metadata.json


def date_dir_process(root_d, d):
    old_dir = os.path.join(root_d, d)
    new_dir = os.path.join(root_d, E_DIR)
    
    # delete metadata.json
    m_f = os.path.join(old_dir, 'metadata1.json')
    if not DEBUG:
        os.remove(m_f)
    log('Deleted "{}"'.format(m_f))

    # move all files to E_DIR
    for f in os.listdir(old_dir):
        old_f = os.path.join(old_dir, f)
        new_f = os.path.join(new_dir, old_dir + '-' + ''.join((filter(lambda x: x not in ['(', ')'], f))))
        if not DEBUG:
            os.rename(old_f, new_f)
        log('Moved _Album dir file_ "{}" to "{}"'.format(old_f, new_f))
    
    # now remove dir itself
    if not DEBUG:
        os.rmdir(old_dir)
    log('Deleted _Album dir_ {}'.format(old_dir))

def album_file_move(root_d, f):
    old_f = os.path.join(root_d, f)
    # assume that the directory name is same as file name without extension
    new_f = os.path.join(root_d, f.split('.')[0], f)
    if not DEBUG:
        os.rename(old_f, new_f)
    log('Moved _Album file_ "{}" to "{}"'.format(old_f, new_f))

def date_file_move(root_d, f):
    old_f = os.path.join(root_d, f)
    new_f = os.path.join(root_d, E_DIR, f)
    if not DEBUG:
        os.rename(old_f, new_f)
    log('Moved _Date file_ "{}" to "{}"'.format(old_f, new_f))

def log(l):
    print('S | {}'.format(l))

if __name__ == "__main__":
    main()
