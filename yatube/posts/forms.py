from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        widgets = {
            'text': forms.Textarea(
                attrs={'cols': 40, 'rows': 10, 'class': 'form-control'}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'text': forms.Textarea(
                attrs={'cols': 40, 'rows': 10, 'class': 'form-control'}
            ),
        }
