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

1. Do Google Takeout to download your photos.
1. Unzip them all. Use `extract.sh` as a convenience script.

## Update EXIF date/time

Google Photos is designed to work around photos having EXIF date (`DateTimeOriginal` tag) set. Without it you get a pile of photos that's not quite manageable. If you ever set date/time on photos within Google Photos, beware that the EXIF was not updated. Instead your export contains metadata in _.json_ files.

Follow this section to set proper EXIF dates on your photos. Only _jpeg/jpg_ and _png_ are supported. Note that video formats aren't supported at all.

1. Run `update_exif.py`. Sometimes an occasional update fails, likely due to corrupted EXIF headers.
1. Save these _<image>.json_ metadata files for the failed image updates if you need that info for later. Otherwise it will be deleted in the next step.

## Prepare folders for upload

Another strange thing Google Photos do is a weird folder structure. You can see it for yourself. This step will do a few things:

- Move all files into their proper album directories.
- Rename album directories to their proper names based on _metadata.json_ info. And filter out an occasional non-ASCII character.
- Move all files that aren't in albums into one directory called *\_NO_ALBUM\_*.
- Remove parenthesis from filenames (why would you ever do that?!).

The directory structure Google gives you keeps giving more and more surprises. Every time I run it on a new account, there's something new. So it is highly advised to examine the output for errors and see if there are any. Frequently you'll have a few weirdly named directories that you can manually rename (or delete, many of them are empty).

Here's how:
1. Run `prepare_folders.py` and redirect output.
1. Look for `E ` in the output to double check for potential errors.

## Upload to Google Photos

Use your favorite uploader. There are a few out there:
- I tried [gpphotos_uploader-cli](https://github.com/gphotosuploader/gphotos-uploader-cli) and it was good but had a few problems. It kept creating duplicate folders and I kept running into Google API rate limit, which is only 10,000 a day. It's not nearly enough to upload a large library.
- [PickBackMan](https://www.picbackman.com/) is a commercial solution and not cheap either. But it works well (Mac and Windows only).

# Contributions & bugs

You are welcome to contribute! If you see a bug, you can open an issue and I hope to get to it soon. Or create a pull request yourself :)

# License

Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
