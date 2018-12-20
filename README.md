**What is the format for a TagWorks document repo?**

A TagWorks document repository can have an arbitrary number of directory levels. In other words, the user can decide how many levels are needed to be able to organize the documents in the most logical way possible. For example, the `sample_documents` directory of this repository (which is one example of a TagWorks document repository) has the files stored under two subdirectories (e.g., `Seattle` ---> `26239-Seattle-SeattleTimes`).

Once the user decides how to organize the directories, the leaf directories should be named as the document filenames (e.g., `26239-Seattle-SeattleTimes`) and have the `text.txt.gz`, `metadata.json.gz`, and `annotations.json.gz` files (or their unzipped versions to be zipped as described in Step 3 below). The files `core-nlp.json.gz` and `hints.json.gz` are subsequently created through the steps described below.

The `metadata.json.gz` file is required and must have the following fields in a single JSON object at a minimum: `filename` and `file_sha246`.

An example:

```
{
  "filename": "26239Seattle-SeattleTimes-02-999.txt",
  "file_sha256": "3b3f5dbe18afe9a79ec8b25722221c6658387da13c28824653f9a278725d7999"
}
```

Since TagWorks stores all annotations separately as character offsets, Tagworks matches all annotations and metadata with their source documents by looking up documents using their SHA-256 fingerprint. SHA-256 is a standardized algorithm that provides a unique document fingerprint, so any single character change, addition, or removal will change the SHA-256 of that document.

Thus it is very important that once annotations are generated externally, such as by the processes outlined below for adding hints, that each source text document remain identical and not mutate.

The `annotations.json.gz` format is only relevant if you already have annotations from a prior process that you wish to load into Tagworks for further processing.

**What do the various steps in the TagWorks-prep repo accomplish?**

*Step 1: Run CoreNLP*

- Step 1a. Run `export PYTHONPATH="."` in the terminal.
	- The current directory has to be on the path because the modules `file_utilities` and `ner_to_hints` are imported later in the pipeline. 
- Step 1b. Start the Stanford CoreNLP server. This can be achieved by doing the following:
	- If you have Docker already installed, you may find it simpler to run an [existing container](https://stanfordnlp.github.io/CoreNLP/other-languages.html): `$ docker run -it -p 9000:9000 vzhong/corenlp-server bash`
		- Note at the time of this writing, this container runs an older version of CoreNLP and has not been updated. The source for this container is at [vzhong/corenlp-docker](https://github.com/vzhong/corenlp-docker).
	- Then run this inside the container, or directly at your command line if you have installed Java and CoreNLP on the machine you are using: `$ java -Xmx16g -cp "./src/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 150000`
		- See also the documentation for the [Stanford CoreNLP webserver](https://stanfordnlp.github.io/CoreNLP/corenlp-server.html) parameters.
	- If you get error 500, you probably ran out of memory. In particular, if you have less than 4GB of free memory, you don't need all the parsers, you can leave off `parse`, `depparse`, `dccoref` in the `params` object included in the script described in Step 1c.
- Step 1c. Run `compute_core_nlp_annotations.py` from the terminal: `$ python3 step1_run_corenlp/compute_core_nlp_annotations.py`
	- This script runs a program that processes all of the documents in the `sample_documents` folder using the inputted CoreNLP annotators and produces a `core-nlp.json.gz` file in the same subfolder where `text.txt.gz` resides, or returns an error message if the annotation process for a given article fails. 
	- The script allows the user to specify a custom documents folder (other than the one hardcoded in the script) using the `-d` or `--dirname` flags when running the script. 

*Step 2: Make hints*

- Run `make_hints_from_corenlp.py` from the terminal: `$ python3 step2_make_hints/make_hints_from_corenlp.py`
	- This script runs a program that processes all of the documents in the `sample_documents` folder and produces a `hints.json.gz` file in the same subfolder where `text.txt.gz`, `core-nlp.json.gz`, and `metadata.json.gz` reside. The hints are generated using named entity recognition (NER) with Location, Person, Organization, and Time as tags. 
		- When run, the script imports functions defined in `file_utilities/__init__.py` and `ner_to_hints/__init__.py`.
		- The script returns an error message if the SHA-256 stored in `metadata.json.gz` does not match the SHA-256 the script creates on the fly. 
		- The script allows the user to specify a custom documents folder (other than the one hardcoded in the script) using the `-d` or `--dirname` flags when running the script. 

*Step 3: Gzip all standalone (Optional)*

- Run `how_to_gzip_files_standalone.sh` from the terminal: `$ ./step3_gzip_all_standalone/how_to_gzip_files_standalone.sh`
	- Steps 1 and 2 above already gzip the files they produce, so this Step 3 is not a necessary part of the pipeline. However, we are including it here to demonstrate an efficient way to iterate over an uncompressed set of files and compress them individually on the fly. 

*Step 4: Generate s3 csv*

- Run `generate_s3_csv.py` from the terminal: `$ python3 step4_generate_s3_csv/generate_s3_csv.py`
	- This script runs a program that goes through all of the documents in the `sample_documents` folder and generates five csv files inside the s3_lists folder: `s3_text.csv`, `s3_annotations.csv`, `s3_metadata.csv`, `s3_core_nlp.csv`, and `s3_hints.csv`. 
	- Each of these csv files have two columns, `s3_bucket` and `s3_path`. `s3_bucket` is based on the customer subdomain and `s3_path` lists the paths to the corresponding gzipped text, annotations, metadata, core_nlp, or hints files. 

*Step 5: Upload to s3*

- Step 5a. Add an AWS key with appropriate S3 permissions to `~/.aws/config` labeled `"corpus-writer"`
- Step 5b. Set the following variable in the shell as advised by Thusly: `$ export TAGWORKS_REPO="CUSTOMER_SUBDOMAIN"`
- Step 5c. Run `sync_to_s3.sh` from the terminal: `$ ./step5_upload_to_s3/sync_to_s3.sh`
	- This script runs a program that syncs a TagWorks corpus to an S3 bucket, excluding any `core-nlp.json.gz` files. 

This workflow is summarized in the script `run_all.sh`. For further information on the content of each of the scripts, refer to the relevant sections of the repository. 

Finally, an important warning related to encoding/decoding in Python: 

One potential gotcha is that editing documents on Windows may introduce a byte-order-mark, and other platforms may remove this byte-order-mark.

Microsoft tools sometimes add a byte-order-mark (BOM) signature as the first character of utf-8 encoded files. The Python decode/encode routines have a `'-sig'` version that strips/adds this BOM from the file. Stripping the BOM is a good idea when initially preparing/writing a corpus. However, if we are just reading the text, leave the sig alone so the SHA-256 computation will match any prior SHA-256 that was calculated with the BOM. Please refer to the `bom_sig` folder for more information on this issue.
