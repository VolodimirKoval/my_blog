from django import forms
from blog.models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=255)
    self_email = forms.EmailField()
    to_email = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    query = forms.CharField()
    