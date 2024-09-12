from django.urls import path
from blog.views import blog_list, post_detail, post_share

app_name = 'blog'

urlpatterns = [
    path('', blog_list, name='blog_list'),
    path('post_detail/<int:post_year>/<int:post_month>/<int:post_day>/<slug:post_slug>/', post_detail, name='post_detail'),
    path('share_post/<int:post_id>/', post_share, name='post_share'),
]
