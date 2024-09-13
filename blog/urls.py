from django.urls import path
from blog.views import blog_list, post_detail, post_share, post_comment

app_name = 'blog'

urlpatterns = [
    path('', blog_list, name='blog_list'),
    path('tag/<slug:tag_slug>/', blog_list, name='blog_list_by_tag'),
    path('post_detail/<int:post_year>/<int:post_month>/<int:post_day>/<slug:post_slug>/', post_detail, name='post_detail'),
    path('share_post/<int:post_id>/', post_share, name='post_share'),
    path('comment/<int:post_id>/', post_comment, name='post_comment'),
]
