from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime, timedelta

import pysam
from .variable import *
import pyBigWig
import numpy as np
import os
from . import models
# Create your views here.

def search(request):
    #mp3 = request.build_absolute_uri('/static/sounds/mp3/button-click.mp3')
    objs = {
        'animals': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in animals_list ],
        'plants': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in plants_list ],
        'bacteria_fungi': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in bacteria_fungi_list ],
        'virus': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in virus_list ]
    }
    return render(request, 'Search.html', objs);

def browser(request):
    species = request.GET.get('species', "")
    loc = request.GET.get('loc', "")
    highlight = request.GET.get('highlight', "")
    tracks = request.GET.get('tracks', "")

    if species is None:
        species = 'hg38'
    
    return render(request, 'browser.html', {
        'species': species,
        'loc': loc,
        'highlight': highlight,
        'tracks': tracks,
        'animals': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in animals_list ],
        'plants': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in plants_list ],
        'bacteria_fungi': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in bacteria_fungi_list ],
        'virus': [ {'stdname':n, 'humanname':dbName2humanName[n]} for n in virus_list ]
    });


def predstr(request):
    sequence = request.GET.get('seq', '')
    shape = request.GET.get('shape','')
    slope = request.GET.get('slope', '')
    intercept = request.GET.get('intercept', '')
    return render(request, 'predstr.html', {
        'sequence': sequence,
        'shape': shape,
        'slope': slope,
        'intercept': intercept
        })

"""
def transView(request):
    return render(request, 'transView.html')
"""


def transView(request):
    #cookie = request.COOKIES
    #print("cookie===>", cookie)

    species = request.GET.get('species', None)
    db_tid = request.GET.get('tid', None)
    if species is None or db_tid is None:
        return HttpResponse("species and tid should be specified")

    Gene_model = eval('models.'+species+'_Gene')
    Trans_model = eval('models.'+species+'_Transcript')
    Exon_model = eval('models.'+species+'_Exon')
    CDS_model = eval('models.'+species+'_CDS')

    trans_obj = Trans_model.objects.filter(ind__exact=db_tid)
    if len(trans_obj)==0:
        return HttpResponse("Transcript does not exist")
    trans_obj = trans_obj[0]
    gene_obj = Gene_model.objects.filter(ind__exact=trans_obj.gene_id)[0]

    strand = "+" if trans_obj.strand else "-"
    exon_objs = list(Exon_model.objects.filter(transcript_id__exact=db_tid))
    cds_objs = list(CDS_model.objects.filter(transcript_id__exact=db_tid))
    if len(cds_objs)==0:
        is_mRNA = False
    else:
        is_mRNA = True

    if trans_obj.strand:
        exon_objs.sort( key=lambda x: x.start )
        cds_objs.sort( key=lambda x: x.start )
    else:
        exon_objs.sort( key=lambda x: x.start, reverse=True )
        cds_objs.sort( key=lambda x: x.start, reverse=True )

    cds_range = [1, sum([e.end-e.start+1 for e in exon_objs])]
    if is_mRNA:
        cds_range = get_cds_range(exon_objs, cds_objs, strand)

    rna_seq = ""
    for exon_obj in exon_objs:
        seq = Genome[species].fetch(exon_obj.chrId, exon_obj.start-1, exon_obj.end)
        if trans_obj.strand:
            rna_seq += seq
        else:
            rna_seq += reverse_comp(seq)

    data_obj = models.BwData.objects.filter(Species__exact=species).filter(Strand__exact=strand)
    
    paper_info = {}
    for obj in data_obj:
        paper_info[obj.DOI] = obj.FirstAuthor.split()[-1]+" et al.,"+obj.Journal+","+obj.Year
    
    doi_list = list(paper_info.keys())
    paper_list = [ paper_info[doi] for doi in doi_list ]
    doi_str = paper_str = "['"
    doi_str += "','".join(doi_list) + "']"
    paper_str += "','".join(paper_list) + "']"
    
    locus = "%s:%d-%d(%c)" % (trans_obj.chrId, trans_obj.start, trans_obj.end, strand)
    locus_link = "/browser/?species="+species+"&loc="+locus[:-3]

    obj = {
        'species': species,
        'gene_symbol': gene_obj.symbol,
        'gid': gene_obj.gid,
        'tid': trans_obj.tid,
        'biotype': trans_obj.biotype,
        'exon_count': len(exon_objs),
        'sequence': rna_seq,
        'cds_start': cds_range[0],
        'cds_end': cds_range[1],

        'strand': strand,
        'db_tid': db_tid,
        'paper_list': paper_str,
        'doi_list': doi_str,

        'locus': locus,
        'locus_link': locus_link
    }

    return render(request, 'transView.html', obj)

def query_dataset(request):
    species = request.GET.get('species', None)
    doi = request.GET.get('doi', None)
    strand = request.GET.get('strand', None)
    datatype = request.GET.get('datatype', None)
    if species is None and doi is None or strand is None:
        return HttpResponse("species, doi and strand should be specified")
    if strand == "pos":
        strand = "+"
    elif strand == 'neg':
        strand = '-'
    else:
        return HttpResponse("strand should be pos or neg")
    bw_objs = models.BwData.objects.filter(Species__exact=species).filter(DOI__exact=doi).filter(Strand__exact=strand)
    if datatype:
        bw_objs = bw_objs.filter(DataType__exact=datatype)
    if len(bw_objs)==0:
        return HttpResponse("No BigWig found")

    datasets = []
    for bw in bw_objs:
        datasets.append({'condition':bw.CellLine+"_"+bw.Condition ,'filePath':bw.FilePath})
    return JsonResponse({'datasets': datasets})


def get_cds_range(exon_objs, cds_objs, strand):
    cds = [0, 0]
    assert strand in ('+','-')
    if strand=="+":
        cds_start_global = cds_objs[0].start
        for exon in exon_objs:
            if exon.start<=cds_start_global<=exon.end:
                cds[0] += cds_start_global-exon.start+1
                break
            else:
                cds[0] += exon.end-exon.start+1
        cds_end_global = cds_objs[-1].end
        for exon in exon_objs:
            if exon.start<=cds_end_global<=exon.end:
                cds[1] += cds_end_global-exon.start+1
                break
            else:
                cds[1] += exon.end-exon.start+1
    else:
        cds_start_global = cds_objs[0].end
        for exon in exon_objs:
            if exon.start<=cds_start_global<=exon.end:
                cds[0] += exon.end-cds_start_global+1
                break
            else:
                cds[0] += exon.end-exon.start+1
        cds_end_global = cds_objs[-1].start
        for exon in exon_objs:
            if exon.start<=cds_end_global<=exon.end:
                cds[1] += exon.end-cds_end_global+1
                break
            else:
                cds[1] += exon.end-exon.start+1
    return cds


def reverse_comp(sequence):
    """
    sequence                -- Raw input sequence
    
    Return the reverse complimentary sequence
    """
    RC_Map = {'A':'T', 'C':'G', 'T':'A', 'G':'C', 'N':'N',
               'a':'t', 'c':'g', 't':'a', 'g':'c', '-':'-'}
    
    return ''.join(map(lambda x: RC_Map[x], list(sequence[::-1])))

def fetch_score(request):
    species = request.GET.get('species', None)
    db_tid = request.GET.get('db_tid', None)
    bw_fn = request.GET.get('bw', None)

    if species is None or db_tid is None or bw_fn is None:
        return HttpResponse("species, db_tid and bw should be specified")

    if not os.path.exists(bw_fn):
        raise RuntimeError(bw_fn + " bigwig file does not exists")
    bw_handle = pyBigWig.open(bw_fn)

    Trans_model = eval('models.'+species+'_Transcript')
    Exon_model = eval('models.'+species+'_Exon')

    trans_obj = Trans_model.objects.filter(ind__exact=db_tid)
    if len(trans_obj)==0:
        return HttpResponse("Transcript does not exist")
    trans_obj = trans_obj[0]

    exon_objs = list(Exon_model.objects.filter(transcript_id__exact=db_tid))
    if trans_obj.strand:
        exon_objs.sort( key=lambda x: x.start )
    else:
        exon_objs.sort( key=lambda x: x.start, reverse=True )
    scores = []
    for exon_obj in exon_objs:
        if exon_obj.chrId in bw_handle.chroms():
            values = bw_handle.values(exon_obj.chrId, exon_obj.start-1, exon_obj.end)
        else:
            values = [np.nan]*(exon_obj.end-exon_obj.start+1)
        if not trans_obj.strand:
            values.reverse();
        scores += values
    for i in range(len(scores)):
        if np.isnan(scores[i]):
            scores[i] = "NULL"
        else:
            scores[i] = str(round(scores[i], 3))
    from .prediction import energy_color_list, get_color
    color_list = energy_color_list()
    colors, lower_bound, upper_bound = get_color(scores, color_list)

    return JsonResponse({'score': scores, 'colors': colors, 'color_list':color_list, 'lower':lower_bound, 'upper':upper_bound})

def fetch_paperinfo(request):
    species = request.GET.get('species', None)
    doi = request.GET.get('doi', None)
    if species is None and doi is None:
        return HttpResponse("species, doi should be specified")
    bw_objs = models.BwData.objects.filter(Species__exact=species).filter(DOI__exact=doi)
    if len(bw_objs)==0:
        return HttpResponse("No BigWig found")
    obj = bw_objs[0]
    return JsonResponse({
        'journal': obj.Journal,
        'year': obj.Year,
        'authors': obj.FirstAuthor+",...,"+obj.CorrespondingAuthor,
        'doi': obj.DOI
    })

def fetch_paperinfo_dataset(request):
    filePath = request.GET.get('filePath', None)
    if filePath is None:
        return HttpResponse("filePath should be specified")
    bw_objs = models.BwData.objects.filter(FilePath__exact=filePath)
    if len(bw_objs)==0:
        return HttpResponse("No BigWig found")
    obj = bw_objs[0]
    return JsonResponse({
        'reagent': obj.Reagent,
        'techname': obj.Technology,
        'cellline': obj.CellLine,
        'condition': obj.Condition,
        'datasource': obj.DataSource
    })


def alignment(request):
    return render(request, 'alignment.html')

def download(request):
    filter_objs = models.BwData.objects.all()
    species_list = list(set([dbName2humanName[obj.Species] for obj in filter_objs]))
    #raw_title_list = list(set([obj.title for obj in filter_objs]))
    #title_list = []
    #for title in raw_title_list:
    #   if len(title)>50:
    #       title_list.append( [title[:50]+"...", title] )
    #   else:
    #       title_list.append( [title, title] )
    #print(title_list)
    return render(request, 'download.html', {'species_list': species_list})


localfulltime = lambda x: datetime.combine(x.date, x.time)


def feedback(request):
    objs = models.Topic.objects.order_by('date', 'time').reverse()
    obj_list = []
    for obj in objs:
        obj.time = localfulltime(obj)
        if u"【置顶】" in obj.title:
            obj_list.insert(0, obj)
        else:
            obj_list.append(obj)
    return render(request, 'feedback.html', {'topic_list': obj_list})

def topic(request):
    topic_id = request.GET.get('topic', None)

    if topic_id is None:
        return HttpResponse("topic ID should be provided")

    topic_id = int(topic_id)
    topic_objs = models.Topic.objects.filter(topicID__exact=topic_id)
    if len(topic_objs)==0:
        return HttpResponse("No topic")

    topic_obj = topic_objs[0]
    #comments = models.Discussion.objects.filter(topic_id__exact=topic_id).order_by('time').reverse()
    comments = models.Discussion.objects.filter(topic_id__exact=topic_id).order_by('date', 'time').reverse()

    return_obj = { 
        'error_code': 0,
        'topicID': topic_id,
        'title': topic_obj.title,
        'nickName': topic_obj.nickName,
        'time': localfulltime(topic_obj),
        'content': topic_obj.content,
        'comments': []
    }

    if len(topic_obj.image_links)>0:
        images = topic_obj.image_links.split(';')
        return_obj['image_list'] = images
    else:
        return_obj['image_list'] = False

    for comment in comments:
        comm_obj = {
            'nickName': comment.nickName,
            'time': localfulltime(comment),
            'content': comment.content
        }
        if len(comment.image_links)>0:
            images = comment.image_links.split(';')
            comm_obj['image_list'] = images
        else:
            comm_obj['image_list'] = False
        return_obj['comments'].append(comm_obj)
    return render(request, 'topic.html', return_obj)


def news(request):
    objs = models.News.objects.all().order_by('date').reverse()
    return render(request, 'news.html', {'news': objs})

def statistics(request):
    filter_objs = models.BwData.objects.filter(DataType__exact="score")
    Reagent_list = sorted(list(set([obj.Reagent.strip() for obj in filter_objs])))
    Principle_list = sorted(list(set([obj.Principle.strip() for obj in filter_objs])))
    return render(request, 'statistics.html', {'reagent_list':Reagent_list,'principle_list':Principle_list})

def help(request):
    return render(request, 'help.html')

def links(request):
    return render(request, 'links.html')

def contact(request):
    return render(request, 'contact.html')

def test(request):
    return render(request, 'test.html')

def special_SARS2(request):
    return render(request, 'SARS2.html')

def upload(request):
    return render(request, 'upload.html')

# def special_SARS2_forreviewer(request):
#   return render(request, 'SARS2-wh27hsvak.html')

def data_request(request):
    title = request.POST.get('title', None)
    url = request.POST.get('url', None)
    description = request.POST.get('description', None)
    name = request.POST.get('name', None)
    email = request.POST.get('email', None)

    html = "<html><body>Please fill the blanks</body></html>"
    if title is None or title.strip()=="":
        return HttpResponse(html)
    if url is None or url.strip()=="":
        return HttpResponse(html)
    if name is None or name.strip()=="":
        return HttpResponse(html)
    if email is None or email.strip()=="":
        return HttpResponse(html)

    try:
        models.DataRequest(title=title, url=url, description=description, name=name, email=email).save()

        from django.core.mail import send_mail
        send_mail(
            f'RASP: New data request from {name}',
            f'Title: {title} \n url: {url} \n email: {email} \n description: {description}',
            'lip16@mails.tsinghua.edu.cn',
            ['hnsfyfyzlp@126.com'],
            fail_silently=False,
        )
    except:
        return HttpResponse(html)
    
    html = "<html><body>Success, we have received your request!</body></html>"
    return HttpResponse(html)


