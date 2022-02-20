from django.db import models

# Create your models here.

class RangeManager(models.Manager):
    def get_samples_in(self, chrId, start, end, strand):
        query_set = super(RangeManager,self).get_queryset().filter(chrId__exact=chrId).\
            filter(strand__exact=strand).filter(end__lte=end).filter(start__gte=start)
        return query_set
    def get_samples_overlap(self, chrId, start, end, strand):
        query_set = super(RangeManager,self).get_queryset().filter(chrId__exact=chrId).\
            filter(strand__exact=strand).filter(start__lt=end).filter(end__gt=start)
        return query_set


#############################
###  This is the template to create models for one species
#############################

template="""
class {0:s}_Gene(models.Model):
    class Meta:
        db_table = "RASP_{0:s}_gene"
    
    RM = RangeManager()
    objects = models.Manager()

    ind = models.IntegerField(primary_key=True, unique=True)
    gid = models.CharField(max_length=30)
    symbol = models.CharField(max_length=30)
    chrId = models.CharField(max_length=20)
    start = models.IntegerField()
    end = models.IntegerField()
    strand = models.BooleanField()

class {0:s}_Transcript(models.Model):
    class Meta:
        db_table = "RASP_{0:s}_transcript"

    RM = RangeManager()
    objects = models.Manager()

    ind = models.IntegerField(primary_key=True, unique=True)
    tid = models.CharField(max_length=30)
    chrId = models.CharField(max_length=20)
    start = models.IntegerField()
    end = models.IntegerField()
    strand = models.BooleanField()
    biotype = models.CharField(max_length=35) # gene type
    gene = models.ForeignKey( "{0:s}_Gene", on_delete=models.CASCADE )

class {0:s}_Exon(models.Model):
    class Meta:
        db_table = "RASP_{0:s}_exon"

    RM = RangeManager()
    objects = models.Manager()

    ind = models.IntegerField(primary_key=True, unique=True)
    chrId = models.CharField(max_length=20)
    start = models.IntegerField()
    end = models.IntegerField()
    strand = models.BooleanField()
    transcript = models.ForeignKey( "{0:s}_Transcript", on_delete=models.CASCADE )

class {0:s}_CDS(models.Model):
    class Meta:
        db_table = "RASP_{0:s}_cds"

    RM = RangeManager()
    objects = models.Manager()

    ind = models.IntegerField(primary_key=True, unique=True)
    chrId = models.CharField(max_length=20)
    start = models.IntegerField()
    end = models.IntegerField()
    strand = models.BooleanField()
    transcript = models.ForeignKey( "{0:s}_Transcript", on_delete=models.CASCADE )
""".strip()

from . import variable
species_list = variable.animals_list+variable.plants_list+variable.bacteria_fungi_list+variable.virus_list
for species in species_list:
    exec(template.format(species))


#########################################
####   For paper index
#########################################

class BwData(models.Model):
    """
    Each bigWig file should have a record in the database
    """
    class Meta:
        db_table = "RASP_BwData"
    
    objects = models.Manager()

    Species = models.CharField(max_length=35)
    Journal = models.CharField(max_length=40)
    Year = models.CharField(max_length=4)
    DOI = models.CharField(max_length=40)
    Title = models.CharField(max_length=200)
    FirstAuthor = models.CharField(max_length=30)
    CorrespondingAuthor = models.CharField(max_length=30)
    DataSource = models.CharField(max_length=25) # 自己处理的还是文章提供的
    Reagent = models.CharField(max_length=20)
    Technology = models.CharField(max_length=25, blank=True)
    DataType = models.CharField(max_length=20)
    Principle = models.CharField(max_length=60)

    CellLine = models.CharField(max_length=100)
    Condition = models.CharField(max_length=200, blank=True)

    Strand = models.CharField(max_length=1)
    label = models.CharField(max_length=55)
    FilePath = models.CharField(max_length=150)
    BedFilePath = models.CharField(max_length=150, blank=True)


##==========> Cookie <===========###

class CookieData(models.Model):
    class Meta:
        db_table = "RASP_cookieData"
    
    cookieID = models.CharField(max_length=40, primary_key=True, unique=True)
    nickName = models.CharField(max_length=40)
    align_name1 = models.CharField(max_length=100, blank=True, null=True)
    align_name2 = models.CharField(max_length=100, blank=True, null=True)
    align_name3 = models.CharField(max_length=100, blank=True, null=True)

    align_seq1 = models.TextField(null=True, blank=True)
    align_seq2 = models.TextField(null=True, blank=True)
    align_seq3 = models.TextField(null=True, blank=True)

    align_score1 = models.TextField(null=True, blank=True)
    align_score2 = models.TextField(null=True, blank=True)
    align_score3 = models.TextField(null=True, blank=True)


##==========> FeedBack <===========###

from tinymce.models import HTMLField
from datetime import datetime
from django.utils import timezone

class Topic(models.Model):
    class Meta:
        db_table = "RASP_Topic"

    topicID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=300)
    content = HTMLField()
    image_links = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(blank=True, auto_now=True)
    time = models.DateTimeField(blank=True, auto_now=True)
    nickName = models.CharField(max_length=30)

class Discussion(models.Model):
    class Meta:
        db_table = "RASP_Discussion"

    content = HTMLField()
    image_links = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(blank=True, auto_now=True)
    time = models.DateTimeField(blank=True, auto_now=True)
    nickName = models.CharField(max_length=30)
    topic = models.ForeignKey( "Topic", on_delete=models.CASCADE )


##==========> News <===========###

class News(models.Model):
    class Meta:
        db_table = "RASP_News"
    
    title = models.CharField(max_length=300)
    date = models.DateField(blank=True, auto_now=True)
    content = HTMLField()


##==========> Data request <===========###

class DataRequest(models.Model):
    class Meta:
        db_table = "RASP_DataRequest"
    
    title = models.CharField(max_length=300)
    url = models.CharField(max_length=600)
    description = models.CharField(max_length=6000)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)



