# About

This is a collection of scripts that helps to do massive migrations from one Google Photo account to another.

All the tools out there that use Google Photos API to migrate one account to another (rcloud, Multcloud, etc) **only migrate compressed versions** of your photos! This is a limitation of Google Photos API so the only way to do this properly is to export from the old account and then re-upload to the new.

# Prerequisites

1. This was written for Python 2 and tested on 2.7. Should probably work in 3 as well.
1. You will need to have [the exiftool](https://exiftool.org/) installed. If it's not somewhere on system path, you can set `EXIFTOOL` environment variable to let the script know where it is.

# General notes

Everything here takes a long time to run if you're dealing with gigabytes of photos. Highly recommend a few things as you work:

- Use `tmux` or a virtual UI session to make sure your scripts keep running when your laptop drops the connection in the middle of processing.
- When you run scripts redirect all output `> output.log` so you can later look at what may have failed.
- Every output line starts with either `I | ` or `W | ` or `E | ` (for info, warning, error respectively) so you can tell exactly what happened.
- Both Python scripts run in _dry run_ mode by default where they don't do any permanent operations. Use `-e` as the second/last argument to execute your changes.
- All files that aren't in any album are moved to the `_NO_ALBUM_` directory.

# How it works

## Download your photos

1. Use google Takeout
1. Run `extract.sh`

## Update EXIF date/time

1. Copy the <image>.json metadata files for the failed images to save for later. Otherwise it will be deleted in the next step.

1. Do Google Takeout for all your Photos. It exports files in a weird directory and filename structure. For each album and image file there is `metadata.json` that has a bunch of info.
1. Run `extract.sh` to unzip everything
1. Extract everything.
1. Set EXIF `DateTimeOriginal` timestamps so Google Photos can properly sort them. This step is needed if you previously set timestamps in Google Photos, which does not change the EXIF on the image and only stores the timestamp in metadata.
1.

## Upload to Google Photos

Use your favorite uploader. There are a few out there. I tried gp_photo_uploader - it sucked. PickBackMan is a commercial solution but it works better.

# Open items

1. Filter unicode out of album names
1. Video timestamp support is not implemented yet.
