#!/bin/bash

# requires gcloud auth
mkdir -p data/raw
mkdir -p data/reference
gsutil cat gs://motherbrain-external-test/interview-test-funding.json.gz | gunzip > data/reference/interview-test-funding.ndjson
gsutil cat gs://motherbrain-external-test/interview-test-org.json.gz | gunzip > data/reference/interview-test-org.ndjson
