
animals_list = ['hg38', 'mm10', 'GRCZ11']
plants_list = ['TAIR10', 'rice']
bacteria_fungi_list = ['yeast', 'ecoli', 'Pputida', 'Synechococcus', 'Y_pseudotuberculosis']
virus_list = ['HIV', 'Zika', 'Dengue', 'HCV', 'STMV', 'IAV', 'CMV', 'SARS2']

humanName2dbName = {
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

dbName2humanName = dict([(value, key) for key, value in humanName2dbName.items()]) 

species_anno_track = {
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


species_seq_track = {
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
	'Zika': 'Zika_genes',
	'Dengue': 'Dengue_genome',
	'HCV': 'HCV_genome',
	'HIV': 'HIV1_genome',
	'STMV': 'STMV_genome',
	'IAV': 'IAV_genome',
	'CMV': 'CMV_genome',
	'Nucleotides': 'RNA_sequence',
	'SARS2': 'SARS2_sequence'
};

import pysam, os

fasta_root = "/data2/lipan/Data/genome_uncompress"

Genome = {
	'hg38': pysam.Fastafile( os.path.join(fasta_root, 'hg38.fa') ),
	'mm10': pysam.Fastafile( os.path.join(fasta_root, 'mm10.fa') ),
	'GRCZ11': pysam.Fastafile( os.path.join(fasta_root, 'GRCZ11.fa') ),
	'TAIR10': pysam.Fastafile( os.path.join(fasta_root, 'TAIR10.fa') ),
	'rice': pysam.Fastafile( os.path.join(fasta_root, 'rice.fa') ),
	'yeast': pysam.Fastafile( os.path.join(fasta_root, 'yeast.fa') ),	
	'ecoli': pysam.Fastafile( os.path.join(fasta_root, 'ecoli.fa') ),
	'Pputida': pysam.Fastafile( os.path.join(fasta_root, 'Pputida.fa') ),
	'Synechococcus': pysam.Fastafile( os.path.join(fasta_root, 'Synechococcus.fa') ),
	'Y_pseudotuberculosis': pysam.Fastafile( os.path.join(fasta_root, 'Y_pseudotuberculosis.fa') ),
	'Zika': pysam.Fastafile( os.path.join(fasta_root, 'Zika.fa') ),
	'Dengue': pysam.Fastafile( os.path.join(fasta_root, 'Dengue.fa') ),
	'HCV': pysam.Fastafile( os.path.join(fasta_root, 'HCV.fa') ),
	'HIV': pysam.Fastafile( os.path.join(fasta_root, 'HIV.fa') ),
	'STMV': pysam.Fastafile( os.path.join(fasta_root, 'STMV.fa') ),
	'IAV': pysam.Fastafile( os.path.join(fasta_root, 'IAV.fa') ),
	'CMV': pysam.Fastafile( os.path.join(fasta_root, 'CMV.fa') ),
	'Nucleotides': pysam.Fastafile( os.path.join(fasta_root, 'Nucleotides.fa') ),
	'SARS2': pysam.Fastafile( os.path.join(fasta_root, 'SARS2.fa') )
}

blastdb_root = "/data2/lipan/Data/blastdb/"
gff_root = "/data2/lipan/Data/gff/"
genome_root = "/data2/lipan/Data/genome/"
