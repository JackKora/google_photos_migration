# How to prep your google extract for reupload

Run `extract.sh` to unzip everything

Run `find . -iname "*.json" | grep -v ".*metadata.json" | while read -r x; do rm "$x"; done` to remove unneeded json files

* Add support for two and one digit dates
