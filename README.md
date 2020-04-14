# About

This is a collection of scripts that helps to do massive migrations from one Google Photo account to another.

# Prerequisites

1. This was written for Python 2 and tested on 2.7. Should probably work in 3 as well.
1. You will need to have [the exiftool](https://exiftool.org/) installed. If it's not somewhere on system path, you can set `EXIFTOOL` environment variable to let the script know where it is.

# How it works

1. Do Google Takeout for all your Photos. It exports files in a weird directory and filename structure. For each album and image file there is `metadata.json` that has a bunch of info.
1. Run `extract.sh` to unzip everything
1. Extract everything.
1. Set EXIF `DateTimeOriginal` timestamps so Google Photos can properly sort them. This step is needed if you previously set timestamps in Google Photos, which does not change the EXIF on the image and only stores the timestamp in metadata.
1.

# Open items

1. * Add support for two and one digit dates
1. Video timestamp support is not implemented yet.
1. `-edited` support
