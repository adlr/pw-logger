#!/bin/bash

cd "$(dirname "$0")"
python -m venv venv
. ./venv/bin/activate
python log.py
