
from .models import *
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .variable import *

def match_score(query, match):
    #print(query, match)
    query_l = query.lower()
    match_l = match.lower()
    i = match_l.find(query_l)
    assert i>=0
    score = 0
    while i<len(query_l):
        if query_l[i]==match_l[i]:
            score += 1
        i += 1
    score -= len(match_l)-len(query_l)
    return score

def search_gene(request):
	query_str = request.GET.get('gene_symbol', None)
	species = request.GET.getlist('species1')
	#print(query_str, species)
	if query_str is None or len(species)==0:
		return HttpResponse("Species and gene_symbol should not be empty")
	results = []
	for raw_species in species:
		if raw_species in list(humanName2dbName.values()):
			std_species_name = raw_species
			gene_db = eval(std_species_name+"_Gene")
			trans_db = eval(std_species_name+"_Transcript")
			symbol_results = gene_db.objects.filter(symbol__istartswith=query_str)[:100]
			gid_results = gene_db.objects.filter(gid__istartswith=query_str)[:100]
			tid_results = trans_db.objects.filter(tid__istartswith=query_str)[:100]
			
			for f_symbol in symbol_results:
				score = match_score(query_str, f_symbol.symbol)
				results.append([ raw_species, score, 'symbol', f_symbol ])
			for f_gid in gid_results:
				score = match_score(query_str, f_gid.gid)
				results.append([ raw_species, score, 'gid', f_gid ])
			for f_tid in tid_results:
				score = match_score(query_str, f_tid.tid)
				results.append([ raw_species, score, 'tid', f_tid ])
	results.sort(key=lambda x: x[1], reverse=True)
	
	link_root = "/browser/?species=%s&loc=%s:%d-%d"
	
	obj = { 'query_str':query_str, 'species':",".join(species) }
	matches = []
	for raw_species,score,f_type,search_obj in results[:100]:
		std_species_name = raw_species
		gene_db = eval(std_species_name+"_Gene")
		trans_db = eval(std_species_name+"_Transcript")
		region = "%s:%d-%d" % (search_obj.chrId, search_obj.start, search_obj.end)
		trans_list = []
		if f_type == "symbol" or f_type == "gid":
			# search_obj is a gene obj
			if f_type == "symbol":
				target="symbol:"+search_obj.symbol
				gene_symbol = search_obj.symbol
			else:
				target="gene_id:"+search_obj.gid
				gene_symbol = search_obj.symbol
			trans_obj_list = trans_db.objects.filter( gene_id__exact=search_obj.ind )
			for trans_obj in trans_obj_list:
				t_obj = {
					"tid": trans_obj.tid, 
					"link": "/transView/?species="+std_species_name+"&tid="+str(trans_obj.ind),
					"biotype": trans_obj.biotype
				}
				trans_list.append(t_obj)
		else:
			# search_obj is a trans obj
			target="trans_id:"+search_obj.tid
			gene_obj = gene_db.objects.filter( ind__exact=search_obj.gene_id)[0]
			gene_symbol = gene_obj.symbol
			t_obj = {
				"tid": search_obj.tid, 
				"link": "/transView/?species="+std_species_name+"&tid="+str(search_obj.ind),
				"biotype": search_obj.biotype
			}
			trans_list.append(t_obj)
		#print(trans_list)
		#anno_track = species_anno_track[raw_species]
		#seq_track = species_seq_track[raw_species]
		link = link_root % (std_species_name, search_obj.chrId, 
				search_obj.start, search_obj.end)
		matches.append({ 'species':dbName2humanName[raw_species], 'region':region, 'target':target, 'gene_symbol':gene_symbol, 'link':link, 'trans_matches': trans_list })
	obj['matches'] = matches
	if len(matches)>0:
		obj['findmatch'] = True
	#print(obj)
	return render(request, 'search_gene_result.html', obj)



