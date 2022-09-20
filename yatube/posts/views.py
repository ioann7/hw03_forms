from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Group, User
from .forms import PostForm
from .utils import get_posts_page_obj


def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = get_posts_page_obj(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_posts_page_obj(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    current_user = User.objects.get(username=username)
    posts = current_user.posts
    page_obj = get_posts_page_obj(request, posts)
    context = {
        'current_user': current_user,
        'posts_count': posts.count(),
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author', 'group'), id=post_id)
    title = post.text[:30]
    posts_count = post.author.posts.count()
    context = {
        'title': title,
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm()
    context = {
        'action_url': reverse_lazy('posts:post_create'),
        'form': form,
    }

    if request.method == 'POST':
        form = PostForm(request.POST)
        context['form'] = form
        if form.is_valid():
            post_obj = form.save(commit=False)
            post_obj.author = request.user
            post_obj.save()
            return redirect('posts:profile', username=post_obj.author.username)
        return render(request, template, context)
    return render(request, template, context)


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    instance = Post.objects.select_related('author', 'group').get(id=post_id)
    if request.user != instance.author:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(instance=instance)
    context = {
        'action_url': reverse_lazy('posts:post_edit', args=(post_id,)),
        'form': form,
        'is_edit': True,
    }

    if request.method == 'POST':
        form = PostForm(request.POST)
        context['form'] = form
        if form.is_valid():
            post_obj = form.save(commit=False)
            post_obj.author = request.user
            post_obj.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(request, template, context)
    return render(request, template, context)
