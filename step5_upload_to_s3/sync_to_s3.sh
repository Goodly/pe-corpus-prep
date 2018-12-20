#!/bin/bash
# This demonstrates how to sync a TagWorks corpus to an S3 bucket.
# You will need to add an AWS key with appropriate S3 permissions to
# ~/.aws/config labeled "corpus-writer"

# Set this variable in your shell
#export TAGWORKS_REPO="CUSTOMER_SUBDOMAIN"
TAGWORKS_WRITER="corpus-writer"
aws s3 sync --profile ${TAGWORKS_WRITER} data/ s3://tagworks.thusly.co/${TAGWORKS_REPO}/corpus/ --exclude "core-nlp.json.gz"
