import os
import argparse
from fnmatch import fnmatch
import json
import gzip
from io import BytesIO
from collections import defaultdict

import logging
from logging import StreamHandler
logger = logging.getLogger(__name__)

from file_utilities import compute_sha256, read_gzipped_metadata, read_gzipped_document

def ner_to_hints(core_filename, hints_filename, full_text, sha256, metadata):
    raw_bytes = open(core_filename, 'rb').read()
    basename = os.path.basename(core_filename)
    if fnmatch(basename, "*.gz"):
        basename, ext = os.path.splitext(basename)
        raw_bytes = gzip.GzipFile(fileobj=BytesIO(raw_bytes), mode='rb').read()
    if fnmatch(basename, "*.json"):
        basename, ext = os.path.splitext(basename)
        raw_text = raw_bytes.decode('utf-8-sig', errors='strict')
        annotations = json.loads(raw_text)
        hints = collect_hints(annotations, full_text, hints_filename)
        annotations = {
            'hints': hints,
            'file_sha256': sha256,
            'filename': metadata['filename']
        }
        with gzip.GzipFile(hints_filename, mode='wb') as f_out:
            raw_bytes = json.dumps(annotations).encode("utf-8")
            f_out.write(raw_bytes)
    else:
        logger.warn("Expected a .json or .json.gz file.")

def collect_hints(annotations, full_text, hints_filename):
    entities = defaultdict(list)
    for sentence in annotations.get('sentences', []):
        # Reset prior_token for each sentence - never merge across sentences.
        prior_token = defaultdict(lambda:-99)
        for token in sentence.get('tokens', []):
            ner = token.get('ner', '')
            token_index = token.get('index', -50)
            if ner in ['LOCATION', 'PERSON', 'ORGANIZATION', 'TIME']:
                anno = {
                    'text': token['originalText'],
                    'start': token['characterOffsetBegin'],
                    'end': token['characterOffsetEnd']
                }
                if prior_token[ner] + 1 == token_index:
                    last_entry = entities[ner][-1]
                    last_entry['text'] += token['before'] + token['originalText']
                    last_entry['end'] = token['characterOffsetEnd']
                else:
                    entities[ner].append(anno)
                prior_token[ner] = token_index
                last_entry = entities[ner][-1]
                # Verify that the offsets produce the claimed text exactly.
                expected_text = full_text[last_entry['start']:last_entry['end']]
                if expected_text != last_entry['text']:
                    print(u"Offsets don't produce expected text in '{}', forcing fix:\n{}\n{}"
                    .format(hints_filename, expected_text, last_entry['text']))
                    last_entry['text'] = expected_text
    return entities

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--dirname',
        help='dir with standard text.txt.gz and core-nlp.json.gz')
    args = parser.parse_args()
    if args.dirname:
        dirname = args.dirname
        text_filename = os.path.join(dirname, "text.txt.gz")
        core_filename = os.path.join(dirname, "core-nlp.json.gz")
        meta_filename = os.path.join(dirname, "metadata.json.gz")
        hints_filename = os.path.join(dirname, "hints.json.gz")
        full_text = read_gzipped_document(text_filename)
        metadata = read_gzipped_metadata(meta_filename)
        sha256 = compute_sha256(full_text)
        assert(sha256 == metadata['file_sha256'])
        ner_to_hints(core_filename, hints_filename, full_text, sha256, metadata)
