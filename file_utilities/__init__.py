import hashlib
import gzip
import json

def compute_sha256(unicode_text):
    m = hashlib.sha256()
    m.update(unicode_text.encode('utf-8'))
    return m.hexdigest()

def read_gzipped_metadata(meta_filename):
    raw_bytes = gzip.GzipFile(meta_filename, mode='rb').read()
    raw_text = raw_bytes.decode('utf-8-sig', errors='strict')
    return json.loads(raw_text)

def read_gzipped_document(text_filename):
    raw_bytes = gzip.GzipFile(text_filename, mode='rb').read()
    raw_text = raw_bytes.decode('utf-8', errors='strict')
    return raw_text
