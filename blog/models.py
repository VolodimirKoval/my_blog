from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
    
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')  # slug должно быть уникальным для даты, сохраненной в поле publish
    body = models.TextField()
    
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='blog_posts')
    
    publish = models.DateTimeField(default=timezone.now)  # поле дата публикации
    created = models.DateTimeField(auto_now_add=True)  # поле дата создания
    updated = models.DateTimeField(auto_now=True)  # поле дата изменения
    
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    
    # Менеджер tags позволит добавлять, извлекать и удалять теги из объектов Post
    tags = TaggableManager()
    
    objects = models.Manager()  # менеджер, применяемый по умолчанию
    published = PublishedManager()  # конкретно-прикладной менеджер
    
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[
                           self.publish.year,
                           self.publish.month,
                           self.publish.day,
                           self.slug,
                       ]
                       )


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
    
    def __str__(self):
        return f'Comment by {self.name} on {self.post}.'
    