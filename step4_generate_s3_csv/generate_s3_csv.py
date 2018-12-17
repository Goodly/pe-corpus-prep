import os, csv

customer_subdomain = "CUSTOMER"
s3_bucket_text = "s3://tagworks.thusly.co/{}/corpus/".format(customer_subdomain)

def gen_lst_files(file_name, path):
    lst_files = []
    for f in sorted(os.listdir(path)):
        if f != ".DS_Store":
            for sf in sorted(os.listdir(os.path.join(path, f))):
                if sf != ".DS_Store":
                    lst_files += [os.path.join(f, sf, file_name)]        
    return lst_files

def gen_s3_csv(csv_file_name, lst_files):
    with open(csv_file_name, 'w') as out:
        writer = csv.writer(out)
        writer.writerow(["s3_bucket","s3_path"])
        for f in lst_files:
            writer.writerow([s3_bucket_text, f])

path_to_data = "sample_documents/"

text = "text.txt.gz"
annotations = "annotations.json.gz"
metadata = "metadata.json.gz"
core_nlp = "core-nlp.json.gz"
hints = "hints.json.gz"

s3_lists = "s3_lists"

gen_s3_csv(os.path.join(s3_lists, "s3_text.csv"), gen_lst_files(text, path_to_data))

gen_s3_csv(os.path.join(s3_lists, "s3_annotations.csv"), gen_lst_files(annotations, path_to_data))

gen_s3_csv(os.path.join(s3_lists, "s3_metadata.csv"), gen_lst_files(metadata, path_to_data))

gen_s3_csv(os.path.join(s3_lists, "s3_core_nlp.csv"), gen_lst_files(core_nlp, path_to_data))

gen_s3_csv(os.path.join(s3_lists, "s3_hints.csv"), gen_lst_files(hints, path_to_data))
