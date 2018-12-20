import os
import argparse

from file_utilities import compute_sha256, read_gzipped_metadata, read_gzipped_document
from ner_to_hints import ner_to_hints

def read_gzipped_folders(path):
    folders = []
    for f in sorted(os.listdir(path)):
        if f != ".DS_Store":
            for sf in sorted(os.listdir(os.path.join(path, f))):
                if sf != ".DS_Store":
                    folders += [os.path.join(path, f, sf)]
    return folders

def add_hints_files(folders):
    for f in folders:
        text_filename = os.path.join(f, "text.txt.gz")
        core_filename = os.path.join(f, "core-nlp.json.gz")
        meta_filename = os.path.join(f, "metadata.json.gz")
        hints_filename = os.path.join(f, "hints.json.gz")
        full_text = read_gzipped_document(text_filename)
        metadata = read_gzipped_metadata(meta_filename)
        sha256 = compute_sha256(full_text)
        if (sha256 != metadata['file_sha256']):
            print("SHA256 for '{}' does not match metadata SHA256!".format(f))
        ner_to_hints(core_filename, hints_filename, full_text, sha256, metadata)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--dirname',
        help='dir with corpus with text.txt.gz, core-nlp.json.gz, and metadata.json.gz')
    args = parser.parse_args()

    path_to_documents = "sample_documents/"
    if args.dirname:
        path_to_documents = "sample_documents/"

    folders = read_gzipped_folders(path_to_documents)
    add_hints_files(folders)
