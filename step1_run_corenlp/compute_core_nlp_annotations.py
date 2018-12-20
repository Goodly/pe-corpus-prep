# coding: utf-8

"""

Start the CoreNLP server, for example:

docker run -it -p 9000:9000 vzhong/corenlp-server bash

# If you have less than 4GB of free memory, you don't need all the parsers, you can leave off
    parse, depparse, dccoref
in the params below.
java -Xmx16g -cp "./src/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
-port 9000 -timeout 150000

"""

import os, argparse, gzip, json
import requests

params = (
    ('properties',
     '{"annotators":"tokenize,ssplit,pos,lemma,ner","outputFormat":"json"}'),
)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--dirname',
        help='dir with corpus with text.txt.gz, core-nlp.json.gz, and metadata.json.gz')
    args = parser.parse_args()

    path_to_documents = "sample_documents/"
    if args.dirname:
        path_to_documents = args.dirname

    for f in sorted(os.listdir(path_to_documents)):
        if f != ".DS_Store":
            for sf in sorted(os.listdir(os.path.join(path_to_documents, f))):
                if sf != ".DS_Store":
                    zipped = os.path.join(path_to_documents, f, sf, "text.txt.gz")
                    with gzip.open(zipped, mode='rt', encoding='utf8') as unzipped:
                        data = unzipped.read().encode('utf-8')
                    response = requests.post('http://localhost:9000/', params = params, data = data)
                    if response.status_code == 200:
                        with gzip.open(os.path.join(path_to_documents, f, sf, "core-nlp.json.gz"),
                                       mode='wt',
                                       encoding="utf-8") as f_out:
                            json.dump(response.json(), f_out)
                    else:
                        print("Uh oh, got code {} when annotating {}".format(response.status_code, zipped))
