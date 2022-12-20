from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView
from django.shortcuts import render, redirect

from .forms import RegisterUserForm, AddImage
from .models import Question, Choice, AbsUser, Vote
from django.urls import reverse
from django.views import generic
from django.urls import reverse_lazy

from .forms import ChangeUserInfoForm
from django.contrib import messages


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question_vote = get_object_or_404(Question, pk=question_id)
    vote, created = Vote.objects.get_or_create(voter=request.user, question_vote = question_vote)
    if not created:
        return render(request, 'polls/detail.html',{
            'question': question_vote,
            'error_message': 'Проголосовать можно один раз'
        })
    try:
        selected_choice = question_vote.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question_vote,
            'error_message': 'вы не сделали выбор'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question_vote.id,)))


class RegisterViews(CreateView):
    template_name = 'main/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('polls:login')


class LoginView(LoginView):
    template_name = 'main/login.html'
    success_url = reverse_lazy('polls:index')


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class BBLoginView(LoginView):
    template_name = 'main/login.html'


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


@login_required
def profile(request):
    return render(request, 'main/profile.html')


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin,
                         UpdateView):
    model = AbsUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('polls:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AbsUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('polls:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class AddImage(SuccessMessageMixin, UpdateView):
    model = Question
    template_name = 'main/add_image.html'
    form_class = AddImage
    success_url = reverse_lazy('polls:index')
    success_message = 'Картинка успешно добавлена'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)