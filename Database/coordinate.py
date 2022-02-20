

def genomeRegion2transRegion(model_list, chrId, start, end, strand):
    Gene_Model, Transcript_Model, Exon_Model, CDS_Model, prefix = model_list
    trans_overlap = Transcript_Model.RM.get_samples_overlap(chrId, start, end, True if strand=="+" else False)
    trans_regions = {}
    for trans_obj in trans_overlap:
        cr = [] # current regions
        exons = getattr(trans_obj, prefix.lower()+"exon_set").all()
        exons = sorted(list(exons), key=lambda x: x.start, reverse=True if strand=='-' else False)
        start_pos = 0
        for exon in exons:
            if exon.start<=end and start<=exon.end:
                if strand == '+':
                    tstart = max(start-exon.start,0) + 1 + start_pos
                    tend = min(exon.end, end) - exon.start + 1 + start_pos
                    cr.append( [tstart, tend] )
                else:
                    tstart = max(exon.end-end,0) + 1 + start_pos
                    tend = exon.end - max(exon.start, start) + 1 + start_pos
                    cr.append( [tstart, tend] )

            start_pos += exon.end-exon.start+1
        i = 1
        while i<len(cr):
            if cr[i-1][1]+1 == cr[i][0]:
                cr[i-1][1]=cr[i][1]
                del cr[i]
            else:
                i += 1
        if len(cr)>0:
            trans_regions[trans_obj.tid] = cr
    return trans_regions


def transRegion2genomeRegion(model_list, tid, start, end):
    """
    Comfirm start, end not exceed the regions of transcript
    """
    Gene_Model, Transcript_Model, Exon_Model, CDS_Model, prefix = model_list
    trans_obj = Transcript_Model.objects.filter(tid__exact=tid)
    if len(trans_obj)>=1:
        trans_obj = trans_obj[0]
    elif len(trans_obj)==0:
        raise RuntimeError("No transcript with tid="+tid+" found")
    strand = "+" if trans_obj.strand else "-"
    exons = getattr(trans_obj, prefix.lower()+"exon_set").all()
    exons = sorted(list(exons), key=lambda x: x.start, reverse=True if strand=='-' else False)
    start_pos = 0
    cr = []
    for exon in exons:
        if strand=="+":
            tstart = start_pos + 1
            tend = exon.end - exon.start + 1 + start_pos
            if tstart<=end and start<=tend:
                gstart = max(start-tstart, 0) + exon.start
                gend = min(end,tend) - tstart + exon.start
                cr.append([trans_obj.chrId, gstart, gend, strand])
        else:
            tstart = start_pos + 1 #比较小的数
            tend = exon.end-exon.start+1+start_pos # 比较大的数
            if tstart<=end and start<=tend:
                gstart = max(tend-end,0) + exon.start
                gend = tend - max(start, tstart) + exon.start
                cr.append([trans_obj.chrId, gstart, gend, strand])

        start_pos += exon.end-exon.start+1
    return cr
