#!/bin/bash

set -e

for f in *.zip; do
  echo "Unzip $f file.."
  unzip $f
  echo "Deleting $f file..."
  rm -f $f
done
