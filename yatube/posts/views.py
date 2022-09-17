from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = User.objects.get(username=username)
    posts = Post.objects.select_related(
        'author',
        'group'
    ).filter(
        author__username=username
    ).all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'posts_count': posts.count(),
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.select_related('author', 'group').get(id=post_id)
    title = post.text[:30]
    posts_count = post.author.posts.count()
    context = {
        'title': title,
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, template, context)


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
            return redirect('posts:profile', username=request.user.username)
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
            return redirect('posts:profile', username=request.user.username)
        return render(request, template, context)
    return render(request, template, context)
