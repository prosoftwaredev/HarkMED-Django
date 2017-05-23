from django.shortcuts import render, render_to_response, HttpResponseRedirect, Http404, get_object_or_404
from django.template import RequestContext
from django.views.generic import TemplateView, DetailView, ListView
import datetime
from django.utils.translation import ugettext_lazy as _

from diagnosis.models import Diagnosis

# Create your views here.


class LandingView(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(LandingView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['diagnosis_list'] = Diagnosis.objects.all()
        return context


class FaqView(TemplateView):
    template_name = 'base/faq.html'
