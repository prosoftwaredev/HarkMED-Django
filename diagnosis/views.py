from django.views import generic
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
import re
from django.utils.translation import ugettext_lazy as _
import time
from django.views.decorators.http import require_POST

from .models import Diagnosis, Question, Answer, OfferedAnswer


class DiagnosislistView(generic.ListView):
    template_name = 'diagnosis/diagnosis_list.html'
    context_object_name = 'diagnosis'
    paginate_by = settings.DIAGNOSIS_PAGE_SIZE

    def get_queryset(self):
        return Diagnosis.objects.filter(active=True).order_by(
            'mod_datetime')


class DiagnosisView(generic.DetailView):
    model = Diagnosis
    slug_field = 'name'
    template_name = 'diagnosis/diagnosis.html'

    def get_queryset(self):
        diagnosis = super(DiagnosisView, self).get_queryset()
        return diagnosis.filter(active=True)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DiagnosisView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['diagnosis_list'] = Diagnosis.objects.all()
        return context


class QuestionView(generic.DetailView):
    model = Question
    slug_field = 'name'
    template_name = 'diagnosis/question.html'

    def get_queryset(self):
        diagnosis = super(QuestionView, self).get_queryset()
        return diagnosis.filter(active=True)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(QuestionView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['question_list'] = Question.objects.all()
        return context


def value_matches(pattern, value):
    if not pattern:
        return True
    pattern = '^{}$'.format(pattern)
    return re.match(pattern, value)


@require_POST
def complete_diagnosis(request, pk):
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    error_messages = []
    last_post = {}
    if not diagnosis.active:
        error_messages.append(_('Diagnosis is no longer active'))
        questions = []
    else:
        questions = diagnosis.question_set.all()
        # build last_post data dict
        for key in request.POST:
            if key.startswith('q'):
                value = request.POST.getlist(key)
                key = key[1:]
                last_post[key] = value
        # generate unique client_id
        while True:
            client_id = str(time.time())
            existing_answers = Answer.objects.filter(client_id=client_id)
            if not existing_answers:
                break
            time.sleep(0.001)
        # remove ip address from client_id - PRIVACY
        # client_id = '{}@{}'.format(client_id, utils.get_client_ip(request))
        client_answers = []
    # parse, validate and collect answers
    # if diagnosis is inactive questions is empty list (see above)
    for question in questions:
        post_name = 'q{}'.format(question.id)
        if post_name in request.POST:
            post_value = request.POST.getlist(post_name)
            # remove empty strings (can get for inputs)
            for x in post_value:
                if not x:
                    post_value.remove(x)
        else:
            post_value = None
        if question.requires_answer and not post_value:
            error_messages.append(_('Question "{}" requires answer').format(
                question.text))
        else:
            if question.question_type in ('R', 'C', 'RI', 'CI'):
                for a_id in post_value:
                    spam = get_object_or_404(OfferedAnswer, pk=int(a_id))
                    # collect choice answers that are not input for RI and CI
                    if ((question.question_type in ('RI', 'CI') and
                            spam.answer_type != 'I') or
                            (question.question_type in ('R', 'C'))):
                        clanswer = Answer()
                        clanswer.client_id = client_id
                        clanswer.answer = spam
                        client_answers.append(clanswer)
            if (question.question_type == 'RI' or
                    question.question_type == 'CI'):
                answers = question.offeredanswer_set.filter(answer_type='I')
                alen = len(answers)
                if alen > 1:
                    error_messages.append(_('Invalid form'))
                elif alen < 1:
                    oanswer = None
                else:
                    oanswer = answers[0]
                if oanswer and str(oanswer.id) in post_value:
                    # get input value for choice input
                    input_name = 'q{}_value'.format(question.id)
                    if input_name in request.POST:
                        post_value = request.POST[input_name]
                        if not post_value:
                            oanswer = None
                            validate_input_value = False
                        else:
                            validate_input_value = True
                            clanswer = Answer()
                            clanswer.client_id = client_id
                            clanswer.answer = oanswer
                            clanswer.text = post_value
                            client_answers.append(clanswer)
                    else:
                        validate_input_value = False
            elif question.question_type == 'I':
                validate_input_value = True
                oanswer = question.offeredanswer_set.all()[0]
                post_value = post_value[0]
                clanswer = Answer()
                clanswer.client_id = client_id
                clanswer.answer = oanswer
                clanswer.text = post_value
                client_answers.append(clanswer)
            else:
                validate_input_value = False
            if validate_input_value and oanswer:
                pattern = oanswer.validation_format
                if not value_matches(pattern, post_value):
                    error_messages.append(
                        _('Answer for question "{}" must be in '
                          'format "{}"').format(question.text, pattern))
    if error_messages:
        resp_dict = {
            'diagnosis': diagnosis,
            'error_messages': error_messages,
            'last_post': last_post,
        }
        return render_to_response(DiagnosisView.template_name, resp_dict,
                                  context_instance=RequestContext(request))
    for clanswer in client_answers:
        clanswer.save()
    return HttpResponseRedirect(reverse('diagnosis_thanks'))

