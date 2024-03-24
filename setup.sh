#!/bin/bash

cd "$(dirname "$0")"
python -m venv venv
pip install deepdiff
