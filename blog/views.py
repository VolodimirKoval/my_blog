from re import search

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from blog.models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity


def blog_list(request, tag_slug=None):
    post_list = Post.published.all()
    
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # Если page_number находится вне диапазона, то
        # выдать последнюю страницу результатов
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # Если page_number не целое число, то
        # выдать первую страницу
        posts = paginator.page(1)
    
    title = 'All posts'
    context = {
        'title': title,
        'posts': posts,
        'tag': tag,
    }
    
    return render(request, 'blog/list.html', context=context)


def post_detail(request, post_year, post_month, post_day, post_slug):
    post = get_object_or_404(Post,
                             publish__year=post_year,
                             publish__month=post_month,
                             publish__day=post_day,
                             slug=post_slug,
                             status=Post.Status.PUBLISHED)
    # Список активных комментариев к посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    # Список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    title = 'Post detail'
    context = {
        'title': title,
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
    }
    
    return render(request, 'blog/detail.html', context=context)


def post_share(request, post_id):
    # Извлечь пост по идентификатору id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )
    
    sent = False
    
    if request.method == 'POST':
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # ... отправить электронное письмо
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read {post.title}."
            message = f"Read {post.title} at {post_url} address."
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to_email']])
            sent = True
    else:
        form = EmailPostForm()
    
    context = {
        'title': 'Share post via E-mail',
        'form': form,
        'post': post,
        'sent': sent,
    }
    
    return render(request, 'blog/share.html', context=context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
    
    context = {
        'title': 'Comment to post',
        'form': form,
        'comment': comment,
        'post': post,
    }
    return render(request, 'blog/comment.html', context=context)


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            A = 1.0
            B = 0.4
            results = Post.published.annotate(
                similarity=(A / (A + B) * TrigramSimilarity('title', query)
                            + B / (A + B) * TrigramWordSimilarity(query, 'body'))
            ).filter(similarity__gte=0.1).order_by('-similarity')
    
    context = {
        'title': 'Search',
        'form': form,
        'results': results,
        'query': query,
    }
    
    return render(request, 'blog/search.html', context=context)
