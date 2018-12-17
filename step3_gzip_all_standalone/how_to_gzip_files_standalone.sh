#!/bin/bash
# This demonstrates an efficient way to iterate over an uncompressed set of files and
# compress them individually.
find ./sample_documents/ -name "*.txt" -execdir gzip {} \;
find ./sample_documents/ -name "*.json" -execdir gzip {} \;
