from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Like, Post, Comment
from .forms import PostForm, CommentForm
from django.core.exceptions import ObjectDoesNotExist

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date') 
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if (Like.objects.filter(post=post).count() > 0):
        qtd_like = Like.objects.filter(post=post, choice='like').count()
        qtd_notlike = Like.objects.filter(post=post, choice='notlike').count()
        percentage_likes = (qtd_like/(qtd_like + qtd_notlike))*100
        percentage_notlikes = (qtd_notlike/(qtd_like + qtd_notlike))*100
    else:
        percentage_likes = 0
        percentage_notlikes = 0

    contexto = {
        'post': post,
        'likes': percentage_likes,
        'notlikes': percentage_notlikes,
    }

    return render(request, 'blog/post_detail.html', contexto)

@login_required
def post_new(request):
     if request.method == "POST":
         form = PostForm(request.POST)
         if form.is_valid():
             post = form.save(commit=False)
             post.author = request.user
             post.save()
             return redirect('post_detail', pk=post.pk)
     else:
         form = PostForm()
     return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
     post = get_object_or_404(Post, pk=pk)
     if request.method == "POST":
         form = PostForm(request.POST, instance=post)
         if form.is_valid():
             post = form.save(commit=False)
             post.author = request.user
             post.save()
             return redirect('post_detail', pk=post.pk)
     else:
         form = PostForm(instance=post)
     return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)

def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    try:
        feedback = Like.objects.get(post=post, author=request.user)
        if feedback.choice == 'notlike':
            feedback.choice = 'like'
            feedback.save()
        else:
            feedback.delete()
    except ObjectDoesNotExist:
        Like.objects.create(post=post, author=request.user, choice='like')

    return redirect('post_detail', pk=pk)

def not_like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    try:
        feedback = Like.objects.get(post=post, author=request.user)
        if feedback.choice == 'like':
            feedback.choice = 'notlike'
            feedback.save()
        else:
            feedback.delete()
    except ObjectDoesNotExist:
        Like.objects.create(post=post, author=request.user, choice='notlike')

    return redirect('post_detail', pk=pk)

'''
def percentage_of_likes(request, pk):
    post = get_object_or_404(Post, pk=pk)

    contexto = {
        'post': post,
        'likes': Like.objects.filter(post=post, choice='like'),
    }
    
    return render('post_detail', contexto)
'''