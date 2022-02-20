
import tempfile
from xml.dom import minidom
import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from .variable import *
from .models import *

#--------------------------------------------------------
#    Make a blastdb as below: 
#        makeblastdb -in yeast_ensembl.fa \
#            -input_type fasta \
#            -parse_seqids \
#            -title "yeast_ensembl" \
#            -out "yeast_ensembl" \
#            -max_file_sz "1GB" \
#            -dbtype nucl
#
#    Example: blastdb = r"\\wsl$\Ubuntu-18.04\home\lipan\blastDB\yeast_ensembl"
#--------------------------------------------------------


class Hit:
    def __init__(self,bit_score,score,evalue,query_from,query_to,hit_acc,hit_from,hit_to,hit_strand, \
                    identity,gap,align_len,match_qseq,match_tseq,align_pat):
        self.bit_score = bit_score
        self.score = score
        self.evalue = evalue
        self.query_from = query_from
        self.query_to = query_to
        self.hit_acc = hit_acc
        self.hit_from = hit_from
        self.hit_to = hit_to
        self.hit_strand = hit_strand
        self.identity = identity
        self.gap = gap
        self.align_len = align_len
        self.match_qseq = match_qseq
        self.match_tseq = match_tseq
        self.align_pat = align_pat
    
    def __str__(self):
        str1 = "%s\t%d-%d" % (self.match_qseq, self.query_from, self.query_to)
        str2 = "%s\t%s:%d-%d" % (self.match_tseq, self.hit_acc, self.hit_from, self.hit_to)
        return "\n"+str1+"\n"+self.align_pat+"\n"+str2+"\n"
    
    def __repr__(self):
        return self.__str__()

def getChildValue(curElem, childNodeName):
    return curElem.getElementsByTagName(childNodeName)[0].firstChild.nodeValue

def read_blastn_result(blastn_xml):
    xmldoc = minidom.parse(blastn_xml)
    iteration = xmldoc.getElementsByTagName('Iteration')
    if len(iteration)>0:
        query_match = iteration[0]
        
        query_id = getChildValue(query_match, 'Iteration_query-def')
        query_len = getChildValue(query_match, 'Iteration_query-len')
        query_len = int(query_len)
        
        hits = query_match.getElementsByTagName("Hit")
        Hit_List = []
        for hit in hits:
            hit_acc = getChildValue(hit, 'Hit_def').split()[0]
            Hsps = hit.getElementsByTagName("Hsp")
            for hsp in Hsps:
                bit_score = float(getChildValue(hsp, 'Hsp_bit-score'))
                score = float(getChildValue(hsp, 'Hsp_score'))
                evalue = float(getChildValue(hsp, 'Hsp_evalue'))
                query_from = int(getChildValue(hsp, 'Hsp_query-from'))
                query_to = int(getChildValue(hsp, 'Hsp_query-to'))
                hit_from = int(getChildValue(hsp, 'Hsp_hit-from'))
                hit_to = int(getChildValue(hsp, 'Hsp_hit-to'))
                if hit_from>hit_to:
                    hit_strand = '-'
                    hit_from,hit_to = hit_to,hit_from
                else:
                    hit_strand = '+'
                identity = float(getChildValue(hsp, 'Hsp_identity'))
                gap = int(getChildValue(hsp, 'Hsp_gaps'))
                align_len = int(getChildValue(hsp, 'Hsp_align-len'))
                match_qseq = getChildValue(hsp, 'Hsp_qseq')
                match_tseq = getChildValue(hsp, 'Hsp_hseq')
                align_pat = getChildValue(hsp, 'Hsp_midline')
                new_hit = Hit(bit_score,score,evalue,query_from,query_to,hit_acc,hit_from,hit_to,hit_strand,identity,gap,align_len,match_qseq,match_tseq,align_pat)
                Hit_List.append(new_hit)
    
    return Hit_List

def blast_sequence(query_seq, blastdb, evalue=1):
    tmpdir = tempfile.TemporaryDirectory(prefix="blastn")
    tmp_query_fa = os.path.join(tmpdir.name, "query.fa")
    tmp_balstn_xml = os.path.join(tmpdir.name, "result.xml")
    
    with open(tmp_query_fa, 'w') as IN:
        print(">query-seq", file=IN)
        print(query_seq, file=IN)
    
    blastn_cmd = "blastn -query %s -strand both -task megablast -db %s -out %s -outfmt 5 -num_threads 1 -evalue %s -max_hsps 15"
    blastn_cmd = blastn_cmd % (tmp_query_fa, blastdb, tmp_balstn_xml, evalue)
    print(blastn_cmd)
    status = os.system(blastn_cmd)
    if status != 0:
        raise RuntimeError("Error: Blastn has an error")
    
    hits = read_blastn_result(tmp_balstn_xml)
    tmpdir.cleanup()
    
    return hits

#hits = blast_sequence("ACCCAGAAATTTTGATATTTTCAGTGTCAAAAAATGAGGGTCTCTAA", blastdb)

def search_sequence(request):
    sequence = request.POST.get('sequence', "")
    sequence = sequence.strip()
    evalue = float(request.POST.get('evalue'))
    species = request.POST.getlist('species2')
    #print(sequence)
    #print(species)
    if sequence=="" or len(species)==0:
        return HttpResponse("sequence and gene_symbol should not be empty")
    
    seq_lines = sequence.split('\n')
    if seq_lines[0][0] == '>':
        title = seq_lines[0][1:].strip()
        del seq_lines[0]
    else:
        title = "unknown"
    query_seq = ""
    for line in seq_lines:
        if line[0] == '>':
            break
        query_seq += line.strip().upper().replace('U','T')
    
    if len(query_seq)<15:
        return HttpResponse("The seuqnce you provide is too short")

    all_hits = []
    for raw_species in species:
        if raw_species in list(humanName2dbName.values()):
            spname = raw_species
            blastdb = blastdb_root+spname
            hits = blast_sequence(query_seq, blastdb, evalue=evalue)
            for hit in hits:
                hit.species = raw_species
                all_hits.append(hit)

    link_root = "/browser/?species=%s&loc=%s:%d-%d&highlight=%s:%d-%d"
    
    all_hits = sorted(all_hits, key=lambda x: x.evalue)[:100]
    results = []
    species_str = ",".join(species)
    from .coordinate import genomeRegion2transRegion
    for hit in all_hits:
        raw_species = hit.species
        spname = raw_species
        Gene, Transcript, Exon, CDS = eval(spname+"_Gene"),eval(spname+"_Transcript"),eval(spname+"_Exon"),eval(spname+"_CDS")
        model_list = [ Gene, Transcript, Exon, CDS, spname+"_" ]
        trans_dict = genomeRegion2transRegion(model_list, hit.hit_acc, hit.hit_from, hit.hit_to, hit.hit_strand)
        #h = hit.__dict__
        #h['trans'] = list(trans_dict.items())
        hit.trans = list(trans_dict.items())
        #extend_hits.append(h)
        
        gene_db = eval(spname+"_Gene")
        overlapped_genes = gene_db.RM.get_samples_overlap(hit.hit_acc, hit.hit_from, hit.hit_to, True if hit.hit_strand=="+" else False)
        if len(overlapped_genes)>0:
            gene_symbol = overlapped_genes[0].symbol
        else:
            gene_symbol = "None"

        overlapped_trans_obj_list = Transcript.RM.get_samples_overlap(hit.hit_acc,hit.hit_from,hit.hit_to,True if hit.hit_strand=="+" else False)
        trans_list = []
        for trans_obj in overlapped_trans_obj_list:
            t_obj = {
                "tid": trans_obj.tid, 
                "link": "/transView/?species="+spname+"&tid="+str(trans_obj.ind),
                "biotype": trans_obj.biotype
            }
            trans_list.append(t_obj)

        anno_track = species_anno_track[raw_species]
        seq_track = species_seq_track[raw_species]
        show_range = (hit.hit_to-hit.hit_from)//2
        show_start = max(hit.hit_from-show_range, 1)
        show_end = hit.hit_to+show_range
        link = link_root%(raw_species,hit.hit_acc,show_start,show_end,hit.hit_acc,hit.hit_from,hit.hit_to)
        results.append({
            'species_region':"%s %s:%d-%d"%(dbName2humanName[raw_species],hit.hit_acc, hit.hit_from, hit.hit_to),
            'match':hit.match_qseq+"&nbsp;query:"+str(hit.query_from)+"-"+str(hit.query_to)+"<br>"+
                hit.align_pat+"<br>"+
                hit.match_tseq+"&nbsp;%s:%d-%d"%(hit.hit_acc, hit.hit_from, hit.hit_to),
            'gene_symbol': gene_symbol,
            'evalue': round(hit.evalue,3),
            'link': link,
            'trans_matches': trans_list
            })
    
    obj = { 'query_name':title, 'query_seq':query_seq, 'species':species_str, 'evalue':evalue, 'hits':results }
    if len(results)>0:
        obj['findmatch'] = True
    return render(request, 'search_sequence_result.html', obj)

