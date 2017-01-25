#!/usr/bin/env python

from os import getenv
import subprocess
import sys
import argparse
from re import sub
from PandaCore.Tools.ConfigBuilding import DataSample,convert_catalog

workdir = getenv('SUBMIT_WORKDIR')
parser = argparse.ArgumentParser(description='convert configuration')
parser.add_argument('--infile',type=str,default=None)
parser.add_argument('--outfile',type=str,default=None)
parser.add_argument('--nfiles',type=int,default=None)
args = parser.parse_args()

fin = open(args.infile)
samples = convert_catalog(list(fin),as_dict=True)

fout = open(args.outfile,'w')
keys = sorted(samples)
counter=0
for k in keys:
	sample = samples[k]
	configs = sample.get_config(args.nfiles)
	for c in configs:
		fout.write(c%(counter,counter))
		counter += 1

fout.close()
