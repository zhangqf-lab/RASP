from .models import *
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .variable import *

def multi_alignment(seq_list, clean=True, verbose=False):
	"""
	seq_list                -- A list of sequences
	clean                   -- Clean the tmp files
	verbose                 -- Print the command
	
	Global align multiple sequences
	
	Return [ aligned_seq1, aligned_seq2, aligned_seq3,... ]
	
	Require: muscle
	"""
	import random, os, sys
	import shutil
	import tempfile
	import General

	tmpdir = tempfile.TemporaryDirectory(prefix="muscle")
	tmp_input_fa = os.path.join(tmpdir.name, "input.fa")
	tmp_output_fa = os.path.join(tmpdir.name, "output.afa")

	MUSCLE_CMD = "muscle -in %s -out %s -quiet" % (tmp_input_fa, tmp_output_fa)

	OUT = open(tmp_input_fa, 'w')
	for i, sequence in enumerate(seq_list):
		OUT.writelines(">seq_%s\n%s\n" % (i+1, sequence))
	OUT.close()
	
	os.system(MUSCLE_CMD)

	aligned_list = []
	afa = General.load_fasta(tmp_output_fa)
	for i in range(1, len(seq_list)+1):
		aligned_list.append( afa["seq_"+str(i)] )
	
	if verbose: 
		print(MUSCLE_CMD)

	if clean:
		tmpdir.cleanup()
	
	return aligned_list

def read_fasta_from_str(seq_str, default_name='unknown'):
	Fasta = {}
	cur_tid = default_name
	for line in seq_str.strip().split('\n'):
		line = line.strip()
		if line=="": continue
		if line[0]=='>':
			cur_tid = line[1:].split()[0]
		else:
			try:
				Fasta[cur_tid] += line
			except KeyError:
				Fasta[cur_tid] = line
	return Fasta

def read_score_from_str(score_str, default_name='unknown'):
	Shape = {}
	cur_tid = default_name
	for line in score_str.strip().split('\n'):
		line = line.strip()
		if line=="": continue
		if line[0]=='>':
			cur_tid = line[1:].split()[0]
		else:
			try:
				Shape[cur_tid] += line.split()
			except KeyError:
				Shape[cur_tid] = line.split()
	for tid in Shape:
		Shape[tid] = [ float(it) if it!='NULL' else 'NULL' for it in Shape[tid] ]
	return Shape


def normalize_score(score_list):
	"""
	Normalize raw score to 0-1
	"""
	import numpy as np
	valid_scores = np.array([i for i in score_list if i!='NULL'])
	if len(valid_scores)==0:
		return score_list
	elif len(valid_scores)==1:
		lb = 0
		ub = valid_scores[0]
	else:
		valid_scores.sort()
		lb = np.quantile(valid_scores, 0.05)
		ub = np.quantile(valid_scores, 0.95)
	
	new_score = []
	for score in score_list:
		if score!='NULL':
			score = max(min(score, ub), lb)
			new_score.append( round((score-lb)/(ub-lb+0.00001),4) )
		else:
			new_score.append( 'NULL' )
	return new_score

def proc_alignment(request):
	sequence = request.POST.get('sequence', None)
	score = request.POST.get('score', None)

	if sequence is None or score is None:
		return JsonResponse({'error_code':1, 'error_text': 'sequence and score should be provided'})

	fasta = read_fasta_from_str(sequence)
	score = read_score_from_str(score)

	seq_keys = sorted(list(fasta.keys()))
	score_keys = sorted(list(score.keys()))

	if seq_keys!=score_keys:
		return JsonResponse({'error_code':2, 'error_text': 'Sequence keys is not the same as score keys'})
	
	for k in score_keys:
		if len(fasta[k])!=len(score[k]):
			return JsonResponse({'error_code':3, 'error_text': 'Input '+k+' has different length for sequence and score'})

	seq_list = [ fasta[k] for k in seq_keys ]

	aligned_seq_list = multi_alignment(seq_list)

	aligned_seq = {}
	normed_score = {}
	for i,k in enumerate(seq_keys):
		aligned_seq[k] = aligned_seq_list[i]
		normed_score[k] = normalize_score(score[k])

	return_obj = { 'error_code':0, 'data':{} }
	for k in seq_keys:
		aligned_norm_score = []
		raw_score = []
		i = 0
		for b in aligned_seq[k]:
			if b=='-':
				aligned_norm_score.append('-')
				raw_score.append('-')
			else:
				aligned_norm_score.append(normed_score[k][i])
				raw_score.append(score[k][i])
				i += 1
		return_obj['data'][k] = { 'seq': aligned_seq[k], 'normed_score': aligned_norm_score, 'raw_score': raw_score }
	
	return JsonResponse(return_obj)

