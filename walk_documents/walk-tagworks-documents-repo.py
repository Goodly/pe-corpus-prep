#!/usr/bin/python3
import os

def walk_doc_repo(path_to_doc_repo):
    folders = []
    for root, dirs, files in os.walk(path_to_doc_repo):
        if not dirs:
            folders.append(root)
    folders = sorted(folders)
    return folders

if __name__ == "__main__":
    path_to_doc_repo = "test-documents"
    
    for f in walk_doc_repo(path_to_doc_repo):
        print(f + '\n')
