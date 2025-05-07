#!/bin/sh
if [[ -z "${VIRTUAL_ENV+x}" ]] ; then
    python -m venv .venv
    source .venv/bin/activate
    pip install -r third_party/requirements.txt
fi

if [[ $# -eq 0 ]] ; then
    python wsgi.py 
else
    python wsgi.py $@
fi