#!/bin/bash
python3 -m cProfile snak.py -q dubs.snak 3 > profile.txt & pid="$!"
echo "$pid"
sleep 10
kill -1 "$pid"