#!/bin/bash

# This shows you would run all the steps, after you have set appropriate
# credentials, installed Stanford CoreNLP, etc.

export PYTHONPATH="."
# For step 1, you need to start the Stanford CoreNLP server.
# Something like:

# docker run -it -p 9000:9000 vzhong/corenlp-server bash
#   java -Xmx16g -cp "./src/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
#     -port 9000 -timeout 150000

# If you get error 500, you probably ran out of memory. See the code for which
# parsers you can turn off.
python3 step1_run_corenlp/compute_core_nlp_annotations.py

python3 step2_make_hints/make_hints_from_corenlp.py

# The above tools gzip on the fly, so you may not need this.
./step3_gzip_all_standalone/how_to_gzip_files_standalone.sh

python3 step4_generate_s3_csv/generate_s3_csv.py

./step5_upload_to_s3/sync_to_s3.sh
