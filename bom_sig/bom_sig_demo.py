#!/usr/bin/python3
import gzip

from file_utilities import compute_sha256

# Microsoft tools sometimes add a byte-order-mark (BOM) signature as the first
# character of utf-8 encoded files.
# The Python decode/encode routines have a '-sig' version that strips/adds this BOM
# from the file. Stripping the BOM is a good idea when initially preparing/writing a corpus.
# However, if we are just reading the text, leave the sig alone so the SHA256 computation
# will match any prior SHA256 that was calculated with the BOM.

def get_document(text_filename, strip_sig=True):
    raw_bytes = gzip.GzipFile(text_filename, mode='rb').read()
    if strip_sig:
        raw_text = raw_bytes.decode('utf-8-sig', errors='strict')
    else:
        raw_text = raw_bytes.decode('utf-8', errors='strict')
    return raw_text


if __name__ == "__main__":
    file_with_bom_sig = "text.txt.gz"

    # Demonstrate different SHA256 computations depending on whether BOM signature is stripped.

    without_sig = get_document(file_with_bom_sig, strip_sig=True)
    print("without sig {} chars, '{}'".format(len(without_sig), without_sig[:20].encode('unicode-escape')))
    print(compute_sha256(without_sig))

    with_sig = get_document(file_with_bom_sig, strip_sig=False)
    print("with sig {} chars, '{}'".format(len(with_sig), with_sig[:20].encode('unicode-escape')))
    print(compute_sha256(with_sig))

    # Encode with utf-8-sig adds a BOM sig, then the decode leaves it there.
    with_sig2 = without_sig.encode('utf-8-sig').decode('utf-8')
    print("with sig {} chars, '{}'".format(len(with_sig2), with_sig2[:20].encode('unicode-escape')))
    print(compute_sha256(with_sig2))
