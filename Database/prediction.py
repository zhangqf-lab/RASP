#--------------------------
#
#  Code for RNA 2nd structure prediction
#
#--------------------------

import tempfile
import shutil
import os, sys
import subprocess
from django.http import HttpResponse

def load_ct(ctFn):
    """
    Read ct file
    
    ctFn                -- ct file name
    
    Return:
        {1:[seq,dotList,length], ...}
    """
    Ct = {}
    
    ID = 1
    ctList = []
    seq = ""
    last_id = 0
    
    seqLen = 0
    
    for line in open(ctFn):
        data = line.strip().split()
        if not data[0].isdigit():
            raise RuntimeError("cf file format Error: the first item should be a digit")
        elif seqLen==0:
            seqLen = int(data[0])
            energy = float(data[-2])
        elif int(data[0])!=last_id+1:
            raise RuntimeError("ct file format error...")
        else:
            left_id = int(data[0])
            right_id = int(data[4])
            seq += data[1]
            if right_id != 0 and left_id<right_id:
                ctList.append((left_id, right_id))
            last_id += 1
            if left_id == seqLen:
                #print(data, last_id+1)
                dot = ct2dot(ctList, len(seq))
                Ct[ID] = [seq, dot, energy]
                assert seqLen==len(seq)
                last_id = 0
                seq = ""
                ctList = []
                ID += 1
                seqLen = 0
    
    if seq:
        assert seqLen==len(seq)
        dot = ct2dot(ctList, len(seq))
        Ct[ID] = [seq, dot, energy]
        if seqLen != left_id:
            raise RuntimeError("ct file format error...")
    
    return Ct

def save_seq(sequence, outFn):
    """
    sequence                -- Raw sequence
    outFn                   -- File name to save
    
    Build single-seq .fasta file for RNAstructure
    """
    SEQ = open(outFn, 'w')
    SEQ.writelines(">test\n%s\n" % (sequence, ))
    SEQ.close()

def save_shape_constraint(shape_list, outFn):
    """
    shape_list              -- A list of SHAPE scores
    outFn                   -- File name to save
    
    Build a SHAPE constraint file for RNAstructure
    """
    SHAPE = open(outFn, 'w')
    
    for idx in range(len(shape_list)):
        if shape_list[idx] != "NULL":
            SHAPE.writelines("%d\t%s\n" % (idx+1, shape_list[idx]))
        else:
            SHAPE.writelines("%d\t%s\n" % (idx+1, -999))
    
    SHAPE.close()

def save_bp_constraint(bp_constraint, outFn):
    """ 
    bp_constraint           -- [[1,10], [2,9], [3,8]...] 1-based
    outFn                   -- File name to save
    
    Build a constraint file for RNAstructure
    """
    OUT = open(outFn, 'w')
    OUT.writelines("DS:\n-1\nSS:\n-1\nMod:\n-1\n")
    OUT.writelines("Pairs:\n")
    for left, right in bp_constraint:
        OUT.writelines("%s %s\n" % (left, right))
    
    OUT.writelines("-1 -1\n")
    OUT.writelines("FMN:\n-1\nForbids:\n-1 -1\n\n")
    OUT.close()

def parse_pseudoknot(ctList):
    """
    ctList              -- paired-bases: [(3, 8), (4, 7)]
    
    Parse pseusoknots from clList
    Return:
        [ [(3, 8), (4, 7)], [(3, 8), (4, 7)], ... ]
    """
    ctList.sort(key=lambda x:x[0])
    ctList = [ it for it in ctList if it[0]<it[1] ]
    paired_bases = set()
    for lb,rb in ctList:
        paired_bases.add(lb)
        paired_bases.add(rb)
    
    # Collect duplex
    duplex = []
    cur_duplex = [ ctList[0] ]
    for i in range(1, len(ctList)):
        bulge_paired = False
        for li in range(ctList[i-1][0]+1, ctList[i][0]):
            if li in paired_bases:
                bulge_paired = True
                break
        if ctList[i][1]+1>ctList[i-1][1]:
            bulge_paired = True
        else:
            for ri in range(ctList[i][1]+1, ctList[i-1][1]):
                if ri in paired_bases:
                    bulge_paired = True
                    break
        if bulge_paired:
            duplex.append(cur_duplex)
            cur_duplex = [ ctList[i] ]
        else:
            cur_duplex.append(ctList[i])
    if cur_duplex:
        duplex.append(cur_duplex)
    
    # Discriminate duplex are pseudoknot
    Len = len(duplex)
    incompatible_duplex = []
    for i in range(Len):
        for j in range(i+1, Len):
            bp1 = duplex[i][0]
            bp2 = duplex[j][0]
            if bp1[0]<bp2[0]<bp1[1]<bp2[1] or bp2[0]<bp1[0]<bp2[1]<bp1[1]:
                incompatible_duplex.append((i, j))
    
    pseudo_found = []
    while incompatible_duplex:
        # count pseudo
        count = {}
        for l,r in incompatible_duplex:
            count[l] = count.get(l,0)+1
            count[r] = count.get(r,0)+1
        
        # find most possible pseudo
        count = list(count.items())
        count.sort( key=lambda x: (x[1],-len(duplex[x[0]])) )
        possible_pseudo = count[-1][0]
        pseudo_found.append(possible_pseudo)
        i = 0
        while i<len(incompatible_duplex):
            l,r = incompatible_duplex[i]
            if possible_pseudo in (l,r):
                del incompatible_duplex[i]
            else:
                i += 1
    
    pseudo_duplex = []
    for i in pseudo_found:
        pseudo_duplex.append(duplex[i])
    
    return pseudo_duplex

def ct2dot(ctList, length):
    """
    ctList              -- paired-bases: [(3, 8), (4, 7)]
    length              -- Length of structure
    
    Convert ctlist structure to dot-bracket
    [(3, 8), (4, 7)]  => ..((..))..
    """
    import os, sys

    dot = ['.']*length
    if len(ctList) == 0:
        return "".join(dot)
    ctList = sorted(ctList, key=lambda x:x[0])
    ctList = [ it for it in ctList if it[0]<it[1] ]
    pseudo_duplex = parse_pseudoknot(ctList)
    for l,r in ctList:
        dot[l-1] = '('
        dot[r-1] = ')'
    dottypes = [ '<>', r'{}', '[]' ]
    if len(pseudo_duplex)>len(dottypes):
        print("Warning: too many psudoknot type: %s>%s" % (len(pseudo_duplex),len(dottypes)), file=sys.stderr)
    for i,duplex in enumerate(pseudo_duplex):
        for l,r in duplex:
            dot[l-1] = dottypes[i%3][0]
            dot[r-1] = dottypes[i%3][1]

    return "".join(dot)

def predict_structure(sequence, shape_list=None, bp_constraint=None, clean=True, si=-0.6, sm=1.8, md=None, verbose=False):
    """
    sequence                -- Raw sequence
    shape_list              -- A list of SHAPE scores
    bp_constraint           -- [[1,10], [2,9], [3,8]...] 1-based
    clean                   -- Delete all tmp files
    si                      -- Intercept
    sm                      -- Slope
    md                      -- Maximum pairing distance between nucleotides.
    verbose                 -- Print command
    
    Predict RNA secondary structure using Fold or Fold-smp
    
    Require: Fold or Fold-smp, ct2dot
    """
    import shutil
    import os
    
    #tmpzip = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))+".zip"
    tmpdir = tempfile.TemporaryDirectory(prefix="Fold")
    tmp_input_fa = os.path.join(tmpdir.name, "input.fa")
    tmp_shape_cons = os.path.join(tmpdir.name, "shape.cons")
    tmp_bp_cons = os.path.join(tmpdir.name, "bp.cons")
    tmp_result_ct = os.path.join(tmpdir.name, "result.ct")
    
    Fold_CMD = "Fold %s %s -si %s -sm %s" % (tmp_input_fa, tmp_result_ct, si, sm)
    
    save_seq(sequence, tmp_input_fa)
    
    if shape_list:
        if len(sequence) != len(shape_list):
            return HttpResponse("seq_len=%d != shape_len=%d" % (len(sequence), len(shape_list)))
        save_shape_constraint(shape_list, tmp_shape_cons)
        Fold_CMD += " --SHAPE " + tmp_shape_cons
    
    if bp_constraint:
        save_bp_constraint(bp_constraint, tmp_bp_cons)
        Fold_CMD += " --constraint " + tmp_bp_cons
    
    if md:
        Fold_CMD += " --maxdistance " + str(md)
    
    #Fold_CMD += ' > /dev/null'
    
    if verbose: 
        print(Fold_CMD)
    
    subprocess.call(Fold_CMD.split(), stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    #status = os.system(Fold_CMD)
    
    ctDict = load_ct(tmp_result_ct)
    
    #shutil.make_archive(tmpzip, 'zip', tmpdir.name)
    if clean:
        tmpdir.cleanup()
    
    return ctDict

def pred_str(request):
    sequence = request.POST.get('sequence', "").strip()
    constraint = request.POST.get('constraint', "").strip()
    intercept = request.POST.get('intercept', '').strip()
    slope = request.POST.get('slope','').strip()
    
    if sequence=="":
        return HttpResponse("Sequence should be provided")
    
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
        query_seq += line.strip()
    
    if len(query_seq)<10:
        return HttpResponse("The seuqnce you provide is too short")
    
    if constraint!="": 
        if intercept=="" or slope=="":
            return HttpResponse("Intercept and Slope should be provided if constraint with SHAPE scores")
        else:
            shape_list = constraint.split()
    
    else:
        shape_list = None
    
    pred_results = predict_structure(query_seq, shape_list=shape_list)
    pred_results = list(pred_results.values())
    pred_results = [ i[1:] for i in pred_results ]
    ### color code
    import Visual
    if constraint!="":
        colors_list = energy_color_list()
        coded_query_seq, lb, ub = color_code_sequence(query_seq, shape_list, colors_list, 'color')
        for i in range(len(pred_results)):
            cmd = Visual.Plot_RNAStructure_Shape(query_seq, pred_results[i][0], shape_list, mode='heatmap', title=title+"_"+str(i),VARNAProg='VARNAv3-93.jar')
            pred_results[i].append(cmd)
            shape_str = "\\n".join([ "0.0" if i=="NULL" else str(i[:5]) for i in shape_list ])
            link = "http://nibiru.tbi.univie.ac.at/forna/forna.html?id=fasta&file=>%s\\n%s\\n%s&colors=>%s\\nrange%%3Dwhite:red\\n%s"%(title, query_seq, pred_results[i][0], title, shape_str)
            pred_results[i].append(link)
            pred_results[i][0], _, _ = color_code_sequence(pred_results[i][0], shape_list, colors_list, 'color')

    else:
        colors_list = 0
        coded_query_seq = query_seq
        lb = 0
        ub = 0
        for i in range(len(pred_results)):
            link = "http://nibiru.tbi.univie.ac.at/forna/forna.html?id=fasta&file=>%s\\n%s\\n%s"%(title, query_seq, pred_results[i][0])
            pred_results[i].append(0)
            pred_results[i].append(link)

    obj = { 
        'seq_name': title,
        'coded_seq': coded_query_seq,
        'query_seq': query_seq, 
        'constraint': constraint, 
        'intercept': intercept, 
        'slope': slope,
        'datalist': pred_results,
        'colors_list': colors_list,
        'lower_b': round(lb,3),
        'upper_b': round(ub,3)
        }
    from django.shortcuts import render
    return render(request, 'display_str.html', obj)

def energy_color_list(num=120):
    from colour import Color
    red = Color("red")
    colors = list(red.range_to(Color("green"),10))
    
    r1 = Color('#4747B6')
    r2 = Color('#4747FF')
    r3 = Color('#1CFF47')
    r4 = Color('#b0b51b')
    r5 = Color('#FF4747')
    r6 = Color('#B64747')
    
    clist1 = list(r1.range_to(r2,num//6))
    clist2 = list(r2.range_to(r3,num//4))
    clist3 = list(r3.range_to(r4,num//6))
    clist4 = list(r4.range_to(r5,num//4))
    clist5 = list(r5.range_to(r6,num//6))
    
    energy_list = clist1+clist2+clist3+clist4+clist5
    energy_list = [i.get_hex() for i in energy_list]
    return energy_list

def color_code_sequence(raw_seq, shape_list, colors_list, mode="background"):
    """
    mode                -- background or color
    """
    import numpy as np
    gray = "#9e9e9e"
    
    valid_shape = [ float(i) for i in shape_list if i!='NULL' ]
    up_bound = np.quantile(valid_shape, 0.95)
    lower_bound = np.quantile(valid_shape, 0.05)
    html_code = ""
    for base,s in zip(raw_seq,shape_list):
        if s=='NULL':
            c = gray
        else:
            s = float(s)
            s = np.clip(s, lower_bound, up_bound)
            i = int( (s-lower_bound)/(up_bound-lower_bound) * (len(colors_list)-1) )
            c = colors_list[i]
        if mode == 'background':
            html_code += '<span style="background-color:%s" class="badge">'%(c) + base + "</span>"
        else:
            html_code += '<span style="color:%s" class="dot">'%(c) + base + "</span>"
    return html_code, lower_bound, up_bound

def get_color(shape_list, colors_list):
    import numpy as np
    gray = "#9e9e9e"
    
    color_list = []
    valid_shape = [ float(i) for i in shape_list if i!='NULL' ]
    if len(valid_shape)==0:
        return [gray]*len(shape_list), 0, 0
    
    up_bound = round(np.quantile(valid_shape, 0.95),3)
    lower_bound = round(np.quantile(valid_shape, 0.05),3)
    html_code = ""
    #print(shape_list)
    for s in shape_list:
        if s=='NULL':
            c = gray
        else:
            s = float(s)
            s = np.clip(s, lower_bound, up_bound)
            i = int( (s-lower_bound)/(up_bound-lower_bound+0.0001) * (len(colors_list)-1) )
            c = colors_list[i]
        color_list.append(c)
    return color_list, lower_bound, up_bound
