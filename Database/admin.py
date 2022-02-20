from django.contrib import admin

# Register your models here.

from .models import News, Topic, Discussion, DataRequest

class NewsAdmin(admin.ModelAdmin):
	list_display = ['title', 'content']
	list_per_page = 10
	action_on_bottom = True

class TopicAdmin(admin.ModelAdmin):
	list_display = [ 'topicID', 'date', 'title', 'nickName' ]
	list_per_page = 20
	action_on_bottom = True

class DiscussionAdmin(admin.ModelAdmin):
	list_display = [ 'topic', 'date', 'nickName', 'content' ]
	list_per_page = 20
	action_on_bottom = True

class DataRequestAdmin(admin.ModelAdmin):
	list_display = ['title', 'name', 'email', 'url', 'description']
	list_per_page = 10
	action_on_bottom = True

admin.site.register(News, NewsAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(DataRequest, DataRequestAdmin)
