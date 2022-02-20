
from django.http import HttpResponse
from django.http import JsonResponse
from . import models
from datetime import datetime, timedelta
import os

def query_datasets(request):
    q_species = request.GET.get('species', None);
    q_reagent = request.GET.get('reagent', None);
    q_technology = request.GET.get('technology', None);
    q_journal = request.GET.get('journal', None);
    q_year = request.GET.get('year', None);
    q_firstauthor = request.GET.get('firstauthor', None);
    q_corresauthor = request.GET.get('corresauthor', None);
    q_title = request.GET.get('title', None);
    q_datatype = request.GET.get('datatype', None);
    q_condition = request.GET.get('condition', None);
    q_source = request.GET.get('source', None);
    q_cellline = request.GET.get('cellline', None);
    q_strand = request.GET.get('strand', None);
    q_principle = request.GET.get('principle', None);
    
    if q_species is None:
        filter_objs = models.BwData.objects.all()
        species_list = list(set([obj.species for obj in filter_objs]))
        return JsonResponse({'error_code': 0, 'species_list': species_list})
    
    filter_objs = models.BwData.objects.filter(Species__exact=q_species)
    if len(filter_objs)==0:
        return JsonResponse({'error_code': 2, 'error_text': 'Query species not found'})
    if q_reagent is not None:
        filter_objs = filter_objs.filter(Reagent__exact=q_reagent)
    if q_technology is not None:
        filter_objs = filter_objs.filter(Technology__exact=q_technology)
    if q_journal is not None:
        filter_objs = filter_objs.filter(Journal__exact=q_journal)
    if q_year is not None:
        filter_objs = filter_objs.filter(Year__exact=q_year)
    if q_firstauthor is not None:
        filter_objs = filter_objs.filter(FirstAuthor__exact=q_firstauthor)
    if q_corresauthor is not None:
        filter_objs = filter_objs.filter(CorrespondingAuthor__exact=q_corresauthor)
    if q_title is not None:
        filter_objs = filter_objs.filter(Title__exact=q_title)
    if q_datatype is not None:
        filter_objs = filter_objs.filter(DataType__exact=q_datatype)
    if q_condition is not None:
        filter_objs = filter_objs.filter(Condition__exact=q_condition)
    if q_source is not None:
        filter_objs = filter_objs.filter(DataSource__exact=q_source)
    if q_cellline is not None:
        filter_objs = filter_objs.filter(CellLine__exact=q_cellline)
    if q_strand is not None:
        filter_objs = filter_objs.filter(Strand__exact=q_strand)
    if q_principle is not None:
       filter_objs = filter_objs.filter(Principle__exact=q_principle)
    
    reagent = set()
    technology = set()
    journal = set()
    year = set()
    firstauthor = set()
    corresauthor = set()
    title = set()
    datatype = set()
    condition = set()
    source = set()
    cellline = set()
    strand = set()
    principle = set()
    track_labels = []
    for obj in list(filter_objs):
        reagent.add( obj.Reagent )
        technology.add( obj.Technology )
        journal.add( obj.Journal )
        year.add( obj.Year )
        firstauthor.add( obj.FirstAuthor )
        corresauthor.add( obj.CorrespondingAuthor )
        title.add( obj.Title )
        datatype.add( obj.DataType )
        condition.add( obj.Condition )
        source.add( obj.DataSource )
        cellline.add( obj.CellLine )
        strand.add( obj.Strand )
        principle.add( obj.Principle )
        track_labels.append( obj.label )
    
    return JsonResponse({
        'error_code': 0,
        'reagent': list(reagent),
        'technology': list(technology),
        'journal': list(journal),
        'year': list(year),
        'firstauthor': list(firstauthor),
        'corresauthor': list(corresauthor),
        'title': list(title),
        'datatype': list(datatype),
        'condition': list(condition),
        'source': list(source),
        'cellline': list(cellline),
        'strand': list(strand),
        'num_datasets': len(filter_objs),
        'track_labels': track_labels,
        'principle': list(principle),
    })

def query_bwfiles(request):
    q_species = request.GET.get('species', None);
    q_reagent = request.GET.get('reagent', None);
    q_technology = request.GET.get('technology', None);
    q_journal = request.GET.get('journal', None);
    q_year = request.GET.get('year', None);
    q_firstauthor = request.GET.get('firstauthor', None);
    q_corresauthor = request.GET.get('corresauthor', None);
    q_title = request.GET.get('title', None);
    q_datatype = request.GET.get('datatype', None);
    q_condition = request.GET.get('condition', None);
    q_source = request.GET.get('source', None);
    q_cellline = request.GET.get('cellline', None);
    q_strand = request.GET.get('strand', None);
    q_principle = request.GET.get('principle', None);
    q_region = request.GET.get('region', None);
    
    if q_species is None:
        return JsonResponse({'error_code': 1, 'error_text': 'species should be provided'})

    filter_objs = models.BwData.objects.filter(Species__exact=q_species)
    if len(filter_objs)==0:
        return JsonResponse({'error_code': 2, 'error_text': 'Query species not found'})
    if q_reagent is not None:
        filter_objs = filter_objs.filter(Reagent__exact=q_reagent)
    if q_technology is not None:
        filter_objs = filter_objs.filter(Technology__exact=q_technology)
    if q_journal is not None:
        filter_objs = filter_objs.filter(Journal__exact=q_journal)
    if q_year is not None:
        filter_objs = filter_objs.filter(Year__exact=q_year)
    if q_firstauthor is not None:
        filter_objs = filter_objs.filter(FirstAuthor__exact=q_firstauthor)
    if q_corresauthor is not None:
        filter_objs = filter_objs.filter(CorrespondingAuthor__exact=q_corresauthor)
    if q_title is not None:
        filter_objs = filter_objs.filter(Title__exact=q_title)
    if q_datatype is not None:
        filter_objs = filter_objs.filter(DataType__exact=q_datatype)
    if q_condition is not None:
        filter_objs = filter_objs.filter(Condition__exact=q_condition)
    if q_source is not None:
        filter_objs = filter_objs.filter(DataSource__exact=q_source)
    if q_cellline is not None:
        filter_objs = filter_objs.filter(CellLine__exact=q_cellline)
    if q_strand is not None:
        filter_objs = filter_objs.filter(Strand__exact=q_strand)
    if q_principle is not None:
       filter_objs = filter_objs.filter(Principle__exact=q_principle)
    
    return_obj = []
    for obj in list(filter_objs):
        return_obj.append({
            'species': obj.Species,
            'reagent': obj.Reagent,
            'technology': obj.Technology,
            'journal': obj.Journal,
            'year': obj.Year,
            'doi': obj.DOI,
            'label': obj.label,
            'firstauthor': obj.FirstAuthor,
            'correspondauthor': obj.CorrespondingAuthor,
            'title': obj.Title,
            'datatype': obj.DataType,
            'condition': obj.Condition,
            'cellline': obj.CellLine,
            'strand': obj.Strand,
            'principle': obj.Principle,
            'file_path': obj.FilePath,
            'bed_file_path': obj.BedFilePath,
            'file_size': sizeof_fmt(os.path.getsize(obj.FilePath)) })
    
    if q_region is not None:
        chrID, start_end = q_region.split(':')
        start, end = start_end.split('-')
        start, end = int(start), int(end)
        return_obj = only_overed_objs(return_obj, chrID, start, end)

    return JsonResponse({ 'error_code': 0, 'bw_files': return_obj })

def only_overed_objs(obj_list, chrID, start, end, min_num=10):
    """
    只留下bigWig在那个区域有值的那些项，其他的过滤掉
    """
    import numpy as np
    import pyBigWig
    overed_objs = []
    for obj in obj_list:
        bw = pyBigWig.open(obj['file_path'])
        try:
            values = bw.values(chrID, start, end)
        except RuntimeError:
            continue
        if (~np.isnan(values)).sum() >= min_num:
            overed_objs.append(obj)
    return overed_objs

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def query_symbol_match(request):
    q_species = request.GET.get('species', None); # Species
    q_symbol = request.GET.get('symbol', None); # Symbol prefix
    q_topNum = request.GET.get('topNum', '10'); # Symbol prefix
    
    if q_species is None:
        return JsonResponse({'error_code': 1, 'error_text': 'species should be provided'})

    q_topNum = int(q_topNum)

    try:
        gene_db = eval("models."+q_species+"_Gene")
    except NameError:
        return JsonResponse({'error_code': 2, 'error_text': 'Query species not found'})

    if q_symbol is None:
        t_objects = gene_db.objects.all()[:q_topNum]
    else:
        t_objects = gene_db.objects.filter(symbol__istartswith=q_symbol)[:q_topNum]
    top_symbols = list(set([ o.symbol for o in t_objects ]))

    return JsonResponse({
        'error_code': 0,
        'symbols': top_symbols
    })

def get_geneObj_by_symbol(request):
    q_species = request.GET.get('species', None); # Species
    q_symbol = request.GET.get('symbol', None); # Symbol prefix
    
    if q_species is None or q_symbol is None:
        return JsonResponse({'error_code': 1, 'error_text': 'Species and symbol should be provided'})

    try:
        gene_db = eval("models."+q_species+"_Gene")
    except NameError:
        return JsonResponse({'error_code': 2, 'error_text': 'Query species not found'})

    t_objects = gene_db.objects.filter(symbol__exact=q_symbol)
    if( len(t_objects)==0 ):
        return JsonResponse({'error_code': 3, 'error_text': 'Gene symbol not found'})
    
    return JsonResponse({
        'error_code': 0,
        'ind': t_objects[0].ind,
        'gid': t_objects[0].gid,
        'symbol': t_objects[0].symbol,
        'chrId': t_objects[0].chrId,
        'start': t_objects[0].start,
        'end': t_objects[0].end,
        'strand': "+" if t_objects[0].strand else "-"
    })

def update_align_seq(request):
    cook_id = request.COOKIES.get('userid')
    name = request.POST.get('name', None)
    seq = request.POST.get('seq', None)
    score_str = request.POST.get('score', None)

    if name is None or seq is None or score_str is None:
        return JsonResponse({'error_code': 1, 'error_text': 'name, seq and score should be provided'})
    
    cookie_objs = models.CookieData.objects.filter(cookieID__exact=cook_id)
    if len(cookie_objs) == 0:
        #cookie_obj = models.CookieData()
        #cookie_obj.cookieID = cook_id
        #cookie_obj.save()
        #cookie_obj = create_cookie_obj(cook_id, nick_name)
        return JsonResponse({'error_code': 3, 'error_text': 'Cookie Obj not create'})
    else:
        cookie_obj = cookie_objs[0]

    #print(cookie_obj.align_seq1)
    if cookie_obj.align_seq1 is None:
        cookie_obj.align_name1 = name
        cookie_obj.align_seq1 = seq
        cookie_obj.align_score1 = score_str
        cookie_obj.save()
    elif cookie_obj.align_seq2 is None:
        cookie_obj.align_name2 = name
        cookie_obj.align_seq2 = seq
        cookie_obj.align_score2 = score_str
        cookie_obj.save()
    elif cookie_obj.align_seq3 is None:
        cookie_obj.align_name3 = name
        cookie_obj.align_seq3 = seq
        cookie_obj.align_score3 = score_str
        cookie_obj.save()
    else:
        return JsonResponse({'error_code': 2, 'error_text': 'Maximun number of sequence to align have reached, Please delete at first'})

    return JsonResponse({'error_code': 0})

def get_align_seq(request):
    cook_id = request.COOKIES.get('userid')
    
    cookie_objs = models.CookieData.objects.filter(cookieID__exact=cook_id)
    if len(cookie_objs) == 0:
        #cookie_obj = models.CookieData()
        #cookie_obj.cookieID = cook_id
        #cookie_obj.save()
        return JsonResponse({'error_code': 3, 'error_text': 'Cookie Obj not create'})
    else:
        cookie_obj = cookie_objs[0]

    data = []
    if cookie_obj.align_seq1 is not None:
        data.append([cookie_obj.align_name1, cookie_obj.align_seq1, cookie_obj.align_score1])
    if cookie_obj.align_seq2 is not None:
        data.append([cookie_obj.align_name2, cookie_obj.align_seq2, cookie_obj.align_score2])
    if cookie_obj.align_seq3 is not None:
        data.append([cookie_obj.align_name3, cookie_obj.align_seq3, cookie_obj.align_score3])

    return JsonResponse({'error_code':0, 'data':data })

def get_align_seq_count(request):
    cook_id = request.COOKIES.get('userid')
    cookie_objs = models.CookieData.objects.filter(cookieID__exact=cook_id)
    if len(cookie_objs) == 0:
        #cookie_obj = models.CookieData()
        #cookie_obj.cookieID = cook_id
        #cookie_obj.save()
        return JsonResponse({'error_code': 3, 'error_text': 'Cookie Obj not create'})
    else:
        cookie_obj = cookie_objs[0]

    count = 0
    if cookie_obj.align_seq1 is not None:
        count += 1
    if cookie_obj.align_seq2 is not None:
        count += 1
    if cookie_obj.align_seq3 is not None:
        count += 1

    return JsonResponse({'error_code':0, 'count':count })


def delete_align_seq(request):
    cook_id = request.COOKIES.get('userid')
    name = request.GET.get('name', None)

    if name is None:
        return JsonResponse({'error_code': 1, 'error_text': 'name should be provided'})

    cookie_objs = models.CookieData.objects.filter(cookieID__exact=cook_id)
    if len(cookie_objs) == 0:
        return JsonResponse({'error_code': 2, 'error_text': 'Cookie not exists'})
    else:
        cookie_obj = cookie_objs[0]

    if cookie_obj.align_name1 == name:
        cookie_obj.align_name1 = None
        cookie_obj.align_seq1 = None
        cookie_obj.align_score1 = None
        cookie_obj.save()
    elif cookie_obj.align_name2 == name:
        cookie_obj.align_name2 = None
        cookie_obj.align_seq2 = None
        cookie_obj.align_score2 = None
        cookie_obj.save()
    elif cookie_obj.align_name3 == name:
        cookie_obj.align_name3 = None
        cookie_obj.align_seq3 = None
        cookie_obj.align_score3 = None
        cookie_obj.save()
    else:
        return JsonResponse({'error_code': 3, 'error_text': 'This align seq with this name does not exists'})
    
    return JsonResponse({'error_code': 0})

def create_cookie_obj_local(request):
    import random
    import string
    from datetime import date
    from django.http import HttpResponse
    cook_id = "".join(random.sample(string.ascii_letters+string.digits,20))
    nickName = str(date.today())+"_user"
    cookie_obj = models.CookieData()
    cookie_obj.cookieID = cook_id
    cookie_obj.nickName = nickName
    cookie_obj.save()
    http = HttpResponse()
    http.set_cookie("userid", value=cook_id, max_age=360000000, expires=None, path='/', domain=None, secure=False, httponly=False, samesite=None)
    return http

def create_cookie_obj(request):
    import random
    import string
    #cook_id = request.COOKIES.get('_ga')
    cook_id = "".join(random.sample(string.ascii_letters+string.digits,20))
    nickName = request.POST.get('nickName', None)
    #print(request.COOKIES)

    if nickName is None:
        return JsonResponse({'error_code': 1, 'error_text': 'Nick Name should be provided'})
    #if cook_id is None:
    #    return JsonResponse({'error_code': 2, 'error_text': 'Cookie _ga not found'})

    cookie_obj = models.CookieData()
    cookie_obj.cookieID = cook_id
    cookie_obj.nickName = nickName
    cookie_obj.save()
    
    from django.http import HttpResponse
    http = HttpResponse()
    http.set_cookie("userid", value=cook_id, max_age=360000000, expires=None, path='/', domain=None, secure=False, httponly=False, samesite=None)

    return http

def upload_file(request):
    #import datetime
    #suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    import os
    from django.conf import settings
    from django_file_md5 import calculate_md5
    f = request.FILES.get('file',None)
    suffix = calculate_md5(f)
    if f is None:
        return JsonResponse({'error_code': 1, 'error_text': 'You should provide a file'})
    filename, file_extension = os.path.splitext(f.name)
    tmpFn = suffix+file_extension
    saveFn = os.path.join(settings.MEDIA_ROOT, tmpFn)
    with open(saveFn, 'wb') as fp:
        for chunk in f.chunks(): #这里表示把文件切成小块
            fp.write(chunk)
    return JsonResponse({'error_code': 0, 'name': tmpFn})

def new_topic(request):
    title = request.POST.get('title', None)
    content = request.POST.get('content', None)
    cook_id = request.COOKIES.get('userid')
    imagefiles = request.POST.get('imagefiles', "")

    if title is None or content is None:
        return JsonResponse({'error_code': 1, 'error_text': 'title and content should be provided'})

    cookie_obj = models.CookieData.objects.filter(cookieID__exact=cook_id)[0]
    nickName = cookie_obj.nickName
    #time = datetime.now()

    topic = models.Topic()
    topic.title = title
    topic.content = content
    topic.image_links = imagefiles
    topic.nickName = nickName
    #topic.time = time

    topic.save()

    return JsonResponse({'error_code': 0})

def new_comment(request):
    topicID = request.POST.get('topicID', None)
    content = request.POST.get('content', None)
    cook_id = request.COOKIES.get('userid')
    imagefiles = request.POST.get('imagefiles', "")

    if content is None or topicID is None:
        return JsonResponse({'error_code': 1, 'error_text': 'content and topicID should be provided'})

    cookie_obj = models.CookieData.objects.filter(cookieID__exact=cook_id)[0]
    nickName = cookie_obj.nickName
    #time = datetime.now()

    comment = models.Discussion()
    comment.topic_id = int(topicID)
    comment.content = content
    comment.image_links = imagefiles
    comment.nickName = nickName
    #comment.time = time

    print(datetime.now())
    comment.save()

    return JsonResponse({'error_code': 0})


def paper_species_classification(request):
    q_reagent = request.GET.get('reagent', None);
    q_principle = request.GET.get('principle', None);

    filter_objs = models.BwData.objects.filter(DataType__exact="score")
    if q_reagent is not None:
        filter_objs = filter_objs.filter(Reagent__exact=q_reagent)
    if q_principle is not None:
        filter_objs = filter_objs.filter(Principle__exact=q_principle)

    paper_list = [ (o.Species, o.DOI, o.Journal, o.Year, o.FirstAuthor, o.CorrespondingAuthor, o.DataSource, o.Technology) for o in filter_objs.all() ]
    paper_list = list( set(paper_list) )

    species_dict = {}
    for species,doi,journal,year,fAuthor,cAuthor,dataProduction,technology in paper_list:
        obj = {'doi': doi,'journal': journal,'year': year,'author': fAuthor+",...,"+cAuthor,'dataProduction': dataProduction, 'technology': technology}
        try:
            species_dict[species].append(obj)
        except KeyError:
            species_dict[species] = [obj]

    for species in species_dict:
        species_dict[species].sort(key=lambda x: x['year']);

    paper = {
        'Animals': {
            'Human': species_dict.get('hg38',[]),
            'Mouse': species_dict.get('mm10',[]),
            'Zebrafish': species_dict.get('GRCZ11',[])
        },
        'Plants': {
            'Rice': species_dict.get('rice',[]),
            'Ara.tha': species_dict.get('TAIR10',[])
        },
        'Bacterial and Fugins': {
            'E.coli': species_dict.get('ecoli',[]),
            'Yeast': species_dict.get('yeast',[]),
            'P.putida': species_dict.get('Pputida',[]),
            'Synechococcus': species_dict.get('Synechococcus',[]),
            'Y_pseudotuberculosis': species_dict.get('Y_pseudotuberculosis',[])
        },
        'Virus': {
            'HIV': species_dict.get('HIV',[]),
            'Dengue': species_dict.get('Dengue',[]),
            'Zika': species_dict.get('Zika',[]),
            'HCV': species_dict.get('HCV',[]),
            'STMV': species_dict.get('STMV',[]),
            'CMV': species_dict.get('CMV',[]),
            'IAV': species_dict.get('IAV',[]),
            'SARS-CoV-2': species_dict.get('SARS2',[])
        }
    }

    return JsonResponse(paper)

class ReadTempFile():
    def __init__(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        self.file = file
        self.obj = open(file, mode=mode, buffering=buffering, encoding=encoding, 
            errors=errors, newline=newline, closefd=closefd, opener=opener)
        ReadTempFile.method_spread(self)
    def __del__(self):
        import os
        if os.path.exists(self.file):
            os.remove(self.file)
    def close(self):
        import os
        if os.path.exists(self.file):
            os.remove(self.file)
        self.obj.close()
    @staticmethod
    def method_spread(readTempObj):
        for method in dir(readTempObj.obj):
            if not method.startswith('_') and method!='close':
                setattr(readTempObj, method, eval("readTempObj.obj."+method))

def downloadfile(request):
    from django.http import FileResponse
    from . import variable
    import tarfile
    from django.core.files.temp import NamedTemporaryFile
    import tempfile
    from wsgiref.util import FileWrapper
    import zipfile
    
    def enc(raw_string):
        return raw_string.replace("&", "_").replace(" ", "_").replace("/", "_")

    filetype = request.GET.get('filetype', None)
    filelist = request.GET.getlist('filelist')
    
    if filetype is None:
        return JsonResponse({'error_code': 1, 'error_text': 'filetype should be provided'})
    if filelist == []:
        return JsonResponse({'error_code': 2, 'error_text': 'filelist should be provided'})
    
    if filetype == 'gff':
        fileToDownload = os.path.join(variable.gff_root, filelist[0])
        return FileResponse( open(fileToDownload ,'rb') )
    elif filetype == 'fasta':
        fileToDownload = os.path.join(variable.genome_root, filelist[0])
        return FileResponse( open(fileToDownload ,'rb') )
    elif filetype in ('bw', 'bed'):
        fileToDownload = tempfile.mktemp(suffix='.tar', dir="/data2/lipan/tmp")
        tar = tarfile.open(fileToDownload, mode='w')
        filelist = list(set(filelist))
        for fullname in filelist:
            if filetype == 'bw':
                obj = models.BwData.objects.filter(FilePath__exact=fullname)
            else:
                obj = models.BwData.objects.filter(BedFilePath__exact=fullname)
            if len(obj)==0:
                return JsonResponse({'error_code': 4, 'error_text': fullname+' does not exists'})
            obj = obj[0]
            #reagent = enc(obj.Reagent)
            #condition = obj.Condition.replace("&", "_").replace(" ", "_").replace("/", "_")
            strand = "minus" if obj.Strand=='-' else 'plus'
            if filetype == 'bed':
                strand = 'both'
            new_name = f"{enc(obj.Technology)}_{enc(obj.Species)}_{enc(obj.Journal)}_{obj.Year}_{enc(obj.Reagent)}_{enc(obj.Condition)}_{strand}_{obj.DataType}_" + os.path.basename(fullname)
            
            #if not os.path.exists(fullname):
            #    return JsonResponse({'error_code': 4, 'error_text': fullname+' does not exists'})
            #if not os.path.isfile(fullname):
            #    return JsonResponse({'error_code': 4, 'error_text': fullname+' is not a file'})
            #if not fullname.startswith("/data2/lipan/Data/"):
            #    return JsonResponse({'error_code': 4, 'error_text': fullname+' is a invalid file path'})
            #basename = os.path.basename(fullname)
            
            tar.add(fullname, arcname=new_name)
        tar.close()
        #print(fileToDownload)
        return FileResponse( ReadTempFile(fileToDownload ,'rb'), as_attachment=True, filename="RASP_files.tar" )
        #temp = tempfile.TemporaryFile(suffix='.tar', dir="/data2/lipan/tmp")
        #archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        #for fullname in filelist:
        #    if not os.path.exists(fullname):
        #        return JsonResponse({'error_code': 4, 'error_text': fullname+' does not exists'})
        #    basename = os.path.basename(fullname)
        #    archive.write(fullname, basename)
        #archive.close()
        #seeker = ReadTempFile(fileToDownload, 'rb')
        #wrapper = FileWrapper(seeker)
        #response = HttpResponse(wrapper, content_type='application/zip')
        #response['Content-Disposition'] = 'attachment; filename=bigwig_files.tar'
        #return response
    else:
        return JsonResponse({'error_code': 3, 'error_text': 'filetype should be one of gff/fasta/bw'})
    


