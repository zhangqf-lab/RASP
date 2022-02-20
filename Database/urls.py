from django.contrib import admin
from django.urls import path, include


from . import views
from . import db
from . import blast
from . import prediction
from . import alignment
from . import api

urlpatterns = [
    path('', views.news),
    path('news/', views.news),
    path('search/', views.search),
    	path('search/search_gene/', db.search_gene),
    	path('search/search_seq/', blast.search_sequence),
    path('transView/', views.transView),
    	path('transView/query_dataset/', views.query_dataset),
    	path('transView/query_score/', views.fetch_score),
        path('transView/query_paperinfo/', views.fetch_paperinfo),
        path('transView/query_paperinfo_dataset/', views.fetch_paperinfo_dataset),
    path('alignment/', views.alignment),
        path('alignment/proc_alignment/', alignment.proc_alignment),
    path('browser/', views.browser),
    path('predstr/', views.predstr),
    	path('predstr/display_predstr', prediction.pred_str),
    path('download/', views.download),
    path('feedback/', views.feedback),
    path('topic/', views.topic),
    path('statistics/', views.statistics),
    path('help/', views.help),
    path('upload/', views.upload),
    path('links/', views.links),
    path('contact/', views.contact),
    path('test/', views.test),

    path('SARS2/', views.special_SARS2),
    path('upload_request/', views.data_request),

    path('api/query_datasets/', api.query_datasets),
    path('api/query_bwfiles/', api.query_bwfiles),
    path('api/query_symbol_match/', api.query_symbol_match),
    path('api/get_geneObj_by_symbol/', api.get_geneObj_by_symbol),
    path('api/update_align_seq/', api.update_align_seq),
    path('api/get_align_seq/', api.get_align_seq),
    path('api/get_align_seq_count/', api.get_align_seq_count),
    path('api/delete_align_seq/', api.delete_align_seq),
    path('api/create_cookie_obj/', api.create_cookie_obj_local),
    path('api/upload_file/', api.upload_file),
    path('api/new_topic/', api.new_topic),
    path('api/new_comment/', api.new_comment),
    path('api/paper_species_classification/', api.paper_species_classification),
    path('api/downloadfile/', api.downloadfile)
]
