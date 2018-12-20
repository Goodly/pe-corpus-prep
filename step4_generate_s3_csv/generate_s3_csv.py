import os, csv

customer_subdomain = "CUSTOMER"
s3_bucket_text = "s3://tagworks.thusly.co/{}/corpus/".format(customer_subdomain)

def gen_lst_files(file_name, path):
    lst_files = []
    for root, dirs, files in os.walk(path):
        if not dirs and file_name in files:
            lst_files.append(os.path.join(root, file_name))
    lst_files = sorted(lst_files)
    return lst_files

def gen_s3_csv(csv_file_name, lst_files):
    with open(csv_file_name, 'w') as out:
        writer = csv.writer(out)
        writer.writerow(["s3_bucket","s3_path"])
        for f in lst_files:
            writer.writerow([s3_bucket_text, f])

path_to_data = "sample_documents"

text = "text.txt.gz"
annotations = "annotations.json.gz"
metadata = "metadata.json.gz"
core_nlp = "core-nlp.json.gz"
hints = "hints.json.gz"

text_files = gen_lst_files(text, path_to_data)
annotations_files = gen_lst_files(annotations, path_to_data)
metadata_files = gen_lst_files(metadata, path_to_data)
core_nlp_files = gen_lst_files(core_nlp, path_to_data)
hints_files = gen_lst_files(hints, path_to_data)

s3_lists = "s3_lists"

if text_files:
    gen_s3_csv(os.path.join(s3_lists, "s3_text.csv"), text_files)

if annotations_files:
    gen_s3_csv(os.path.join(s3_lists, "s3_annotations.csv"), annotations_files)

if metadata_files:
    gen_s3_csv(os.path.join(s3_lists, "s3_metadata.csv"), metadata_files)

if core_nlp_files:
    gen_s3_csv(os.path.join(s3_lists, "s3_core_nlp.csv"), core_nlp_files)

if hints_files:
    gen_s3_csv(os.path.join(s3_lists, "s3_hints.csv"), hints_files)
