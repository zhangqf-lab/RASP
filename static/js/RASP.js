
const humanName2dbName = {
    'Human': 'hg38',
    'Mouse': 'mm10',
    'Zebrafish': 'GRCZ11',
    'Ara.tha': 'TAIR10',
    'Rice': 'rice',
    'Yeast': 'yeast',
    'Ecoli': 'ecoli',
    'P.putida': 'Pputida',
    'Synechococcus': 'Synechococcus',
    'Y_pseudotuberculosis': 'Y_pseudotuberculosis',
    'Zika': 'Zika',
    'Dengue': 'Dengue',
    'HCV': 'HCV',
    'HIV': 'HIV',
    'STMV': 'STMV',
    'IAV': 'IAV',
    'CMV': 'CMV',
    'SARS-CoV-2': 'SARS2',
    'Nucleotides': 'Nucleotides'
};

function swapKV(obj) {
  const entrySet = Object.entries(obj);
  const reversed = entrySet.map(([k, v])=>[v, k]);
  const result = Object.fromEntries(reversed);
  return result;
}

const dbName2humanName = swapKV(humanName2dbName);

const species_anno_track = {
    'hg38': 'refseq_genes',
    'mm10': 'refseq_genes',
    'GRCZ11': 'ensembl_genes',
    'TAIR10': 'ensembl_genes',
    'rice': 'ensembl_genes',
    'yeast': 'ensembl_genes',
    'ecoli': 'genbank_genes',
    'Pputida': 'refseq_genes',
    'Synechococcus': 'refseq_genes',
    'Y_pseudotuberculosis': 'genes',
    'Zika': 'Flaviviridae_genes',
    'Dengue': 'refseq_genes',
    'HCV': 'Flaviviridae_genes',
    'HIV': 'refseq_genes',
    'STMV': 'Genbank_gens',
    'IAV': 'refseq_genes',
    'CMV': 'refseq_genes',
    'SARS2': 'Gene_annotation',
    'Nucleotides': ''
};

const species_seq_track = {
    'hg38': 'hg38_genome',
    'mm10': 'mm10_genome',
    'GRCZ11': 'GRCZ11_genome',
    'TAIR10': 'TAIR10_genome',
    'rice': 'rice_genome',
    'yeast': 'yeast_genome',
    'ecoli': 'ecoli_genome',
    'Pputida': 'Pputida_genome',
    'Synechococcus': 'Synechococcus_genome',
    'Y_pseudotuberculosis': 'genome_sequence',
    'Zika': 'Zika_genome',
    'Dengue': 'Dengue_genome',
    'HCV': 'HCV_genome',
    'HIV': 'HIV1_genome',
    'STMV': 'STMV_genome',
    'IAV': 'IAV_genome',
    'CMV': 'CMV_genome',
    'Nucleotides': 'RNA_sequence',
    'SARS2': 'SARS2_sequence'
};


function explorer(){
    // Opera 8.0+
    var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
    if(isOpera) return "Opera";

    // Firefox 1.0+
    var isFirefox = typeof InstallTrigger !== 'undefined';
    if(isFirefox) return "Firefox";

    // Safari 3.0+ "[object HTMLElementConstructor]" 
    var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));
    if(isSafari) return "Fafari";

    // Internet Explorer 6-11
    var isIE = /*@cc_on!@*/false || !!document.documentMode;
    if(isIE) return "IE";

    // Edge 20+
    var isEdge = !isIE && !!window.StyleMedia;
    if(isEdge) return "Edge";

    // Chrome 1 - 79
    var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);

    // Edge (based on chromium) detection
    var isEdgeChromium = isChrome && (navigator.userAgent.indexOf("Edg") != -1);
    if(isEdgeChromium) return "EdgeChromium";

    if(isChrome) return "Chrome";

    // Blink engine detection
    var isBlink = (isChrome || isOpera) && !!window.CSS;
    if(isBlink) return "Blink";
}


/* 设置Alignment右边的数字 */
function set_user_alignment_cache_num(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        var data = JSON.parse(this.responseText);
        if(data['error_code']==3){
            $('#CookiePage').modal('show');
            return;
        }else if(data['error_code']!=0){
            alert(data['error_text']);
            return;
        }
        if(data['count']==0)
            $('#align_indicator').hide();
        else{
            $('#align_indicator').html( String(data['count']) );
            $('#align_indicator').show();
        }
    }
    };
    xhttp.open("GET", "/api/get_align_seq_count/", true);
    xhttp.send();
}

function alerter(title, text, mtype){
    var mtype = mtype || "fail";

    $('#alerter strong').html(title);
    $('#alerter .toast-body').html(text);
    if(mtype=="fail")
    {
        $('#alerter rect').attr('fill', '#f44336');
        $('#alerter strong').css('color', '#f44336');
    }    
    else if(mtype=="success")
    {
        $('#alerter rect').attr('fill', '#4caf50');
        $('#alerter strong').css('color', '#4caf50');
    }
    else if(mtype=="warning")
    {
        $('#alerter rect').attr('fill', '#17a2b8');
        $('#alerter strong').css('color', '#17a2b8');
    }
    $('#alerter').parent()[0].style.zIndex = "999";
    $('#alerter').toast('show');
}

$('#alerter').on('hide.bs.toast', function(){ $('#alerter').parent()[0].style.zIndex = "-1"; });

function valid_textarea_seq(text, must_strict_fasta, min_seq_num, max_seq_num, min_length, max_length,alphabet)
{
    must_strict_fasta = must_strict_fasta || false;
    min_seq_num = min_seq_num || null;
    max_seq_num = max_seq_num || null;
    min_length = min_length || null;
    max_length = max_length || null;
    alphabet | alphabet || null;

    var seq_lines = text.trim().split("\n");
    if( seq_lines.length==1 && seq_lines[0]=="" )
        return {'error_type': 1, 'error_msg': 'Empty sequence'}
    
    var is_fasta = (seq_lines[0][0]==">");
    if( !is_fasta && must_strict_fasta )
        return {'error_type': 2, 'error_msg': 'Is not a fasta file'}

    var seq_id = "unknown";
    if( is_fasta )
        seq_id = seq_lines[0].slice(1).trim();
    
    sequence = {};
    sequence[seq_id] = "";
    for(var line of seq_lines)
    {
        if(line[0]==">"){
            seq_id = line.slice(1).trim();
            sequence[seq_id] = "";
        }
        else
            sequence[seq_id] += line.trim().toUpperCase();
    }
    
    var seq_keys = Object.keys(sequence);
    if(min_seq_num && seq_keys.length<min_seq_num)
        return {'error_type': 3, 'error_msg': 'Too little sequences ('+String(seq_keys.length)+'), at least '+String(min_seq_num)+' sequences allowed'};
    
    if(max_seq_num && seq_keys.length>max_seq_num)
        return {'error_type': 4, 'error_msg': 'Too many sequences ('+String(seq_keys.length)+'), only '+String(max_seq_num)+' sequences allowed'};

    for(var seq of Object.values(sequence))
    {
        if(min_length && seq.length<min_length)
            return {'error_type': 5, 'error_msg': 'Too short sequence ('+String(seq.length)+'), at least '+String(min_length)+'nt allowed'};
        if(max_length && seq.length>max_length)
            return {'error_type': 6, 'error_msg': 'Too long sequence ('+String(seq.length)+'), at most '+String(max_length)+'nt allowed'};
        if(alphabet && !seq.split("").every(x => alphabet.includes(x)))
            return {'error_type': 7, 'error_msg': 'Some base not in alphabet '+String(alphabet)};
    }

    return {'error_type':0, 'sequence':sequence };
}

function valid_textarea_score(text, must_strict_fasta, min_score_num, max_score_num, min_length, max_length)
{
    must_strict_fasta = must_strict_fasta || false;
    min_score_num = min_seq_num || null;
    max_score_num = max_seq_num || null;
    min_length = min_length || null;
    max_length = max_length || null;

    var score_lines = text.trim().split("\n");
    if( score_lines.length==1 && score_lines[0]=="" )
        return {'error_type': 1, 'error_msg': 'Empty score'}
    
    var is_fasta = (score_lines[0][0]==">");
    if( !is_fasta && must_strict_fasta )
        return {'error_type': 2, 'error_msg': 'Is not a fasta file'}

    var score_id = "unknown";
    if( is_fasta )
        score_id = score_lines[0].slice(1).trim();
    
    scoredict = {}
    scoredict[score_id] = [];
    for(var line of score_lines)
        if(line[0]==">"){
            score_id = line.slice(1).trim();
            scoredict[score_id] = [];
        }
        else
        {
            var arr = line.trim().split(/\s+/);
            //console.log(arr);
            scoredict[score_id] = scoredict[score_id].concat(arr);
        }
    
    var score_keys = Object.keys(scoredict);
    if(min_score_num && score_keys.length<min_score_num)
        return {'error_type': 3, 'error_msg': 'Too little scores ('+String(score_keys.length)+'), at least '+String(min_score_num)+' sequences allowed'};
    
    if(max_score_num && score_keys.length>max_score_num)
        return {'error_type': 4, 'error_msg': 'Too many scores ('+String(score_keys.length)+'), only '+String(max_score_num)+' sequences allowed'};

    for(var score of Object.values(scoredict))
    {
        if(min_length && score.length<min_length)
            return {'error_type': 5, 'error_msg': 'Too short score ('+String(score.length)+'), at least '+String(min_length)+'nt allowed'};
        if(max_length && score.length>max_length)
            return {'error_type': 6, 'error_msg': 'Too long score ('+String(score.length)+'), at most '+String(max_length)+'nt allowed'};
    }

    return {'error_type':0, 'scoredict':scoredict };
}

const copyToClipboard = str => {
    const el = document.createElement('textarea');
    el.value = str;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
};

function load_gif(obj, gif_file){
    var parent = $(obj).parent();
    parent.empty();
    parent.append($('<img src="/static/img/'+gif_file+'" alt="gif picture" width="100%">'));
}
