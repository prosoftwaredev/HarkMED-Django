from __future__ import unicode_literals
from django.db import models
from tinymce.models import HTMLField
from django.utils.translation import ugettext_lazy as _
from .validators import validate_regex, validate_question_answers
from collections import OrderedDict


class Condition(models.Model):
    title = models.CharField(max_length=128, verbose_name=_('Title'))
    description = HTMLField(blank=False, null=False, verbose_name=_('Description'))

    def __str__(self):
        return self.title


class Diagnosis(models.Model):
    name = models.SlugField(max_length=128, verbose_name=_('Name'))
    title = models.CharField(max_length=128, verbose_name=_('Title'))
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    description = HTMLField(blank=False, null=False, verbose_name=_('Description'))
    conditions = models.ManyToManyField('Condition', related_name='conditions', blank=True)
    mod_datetime = models.DateTimeField(auto_now=True,
                                        verbose_name=_('Modification'
                                                       ' DateTime'))

    def question_or_group(self):
        foo = OrderedDict()
        for q in self.question_set.all():
            foo[(q.id, None)] = [q]
        spam = []
        for key in list(foo.keys()):
            keyval = key[1]
            spam.append((keyval, foo[key]))
        return spam

    def start_question(self):
        questions = self.question_set.all().order_by('sort_index')
        if questions:
            return questions[0]


    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        ordering = ['mod_datetime']
        verbose_name = _('Diagnosis')
        verbose_name_plural = _('Diagnosis')


class Question(models.Model):
    QTYPE_INPUT = 'I'
    QTYPE_RADIO = 'R'
    QTYOE_CHECKBOX = 'C'
    QTYPE_RADIO_INPUT = 'RI'
    QTYPE_CHECKBOX_INPUT = 'CI'
    QUESTION_TYPES = (
        (QTYPE_INPUT, _('input')),
        (QTYPE_RADIO, _('choice')),
        (QTYOE_CHECKBOX, _('multiple choice')),
        (QTYPE_RADIO_INPUT, _('choice with input')),
        (QTYPE_CHECKBOX_INPUT, _('multiple choice with input')),
    )

    diagnosis = models.ForeignKey(Diagnosis, verbose_name=_('Diagnosis'))
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES,
                                     default='I', verbose_name=_('Type'))
    text = models.CharField(max_length=256, verbose_name=_('Text'))
    requires_answer = models.BooleanField(default=True,
                                          verbose_name=_('Requires Answer'))
    sort_index = models.PositiveIntegerField(default=1,
                                             verbose_name=_('Sort By Asc'))
    next = models.ForeignKey("Question", verbose_name=_('Next Question'), blank=True, null=True)

    def __str__(self):
        return '{}: {}'.format(self.diagnosis, self.text)

    class Meta:
        ordering = ['sort_index']
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


class OfferedAnswer(models.Model):
    ATYPE_INPUT = 'I'
    ATYPE_CHOICE = 'C'
    ANSWER_TYPES = (
        (ATYPE_INPUT, 'input'),
        (ATYPE_CHOICE, 'choice'),
    )

    question = models.ForeignKey(Question, verbose_name=_('Question'))
    next_question = models.ForeignKey(Question, related_name='next_question', verbose_name=_('Next Question'),
                                      blank=True, null=True)
    answer_type = models.CharField(max_length=1, choices=ANSWER_TYPES,
                                   default='C', verbose_name=_('Type'))
    prefix = models.CharField(max_length=128, null=True, blank=True,
                              verbose_name=_('Text Prefix'))
    text = models.CharField(max_length=128, null=True, blank=True,
                            verbose_name=_('Text'))
    sufix = models.CharField(max_length=128, null=True, blank=True,
                             verbose_name=_('Text Sufix'))
    # for choice if has value then answer is selected by default
    default = models.CharField(max_length=128, null=True, blank=True,
                               verbose_name=_('Default Value'))
    validation_format = models.CharField(max_length=256, null=True, blank=True,
                                         verbose_name=_('Validation Regex'),
                                         validators=[validate_regex])
    sort_index = models.PositiveIntegerField(default=1,
                                             verbose_name=_('Sort By Asc'))

    def __str__(self):
        return '{}: {}: {}: {}'.format(self.answer_type,
                                       self.prefix,
                                       self.text,
                                       self.sufix)

    def clean(self):
        validate_question_answers(self.question, self)

    class Meta:
        ordering = ['sort_index']
        verbose_name = _('Offered Answer')
        verbose_name_plural = _('Offered Answers')


class Answer(models.Model):
    client_id = models.CharField(max_length=256, verbose_name=_('Client ID'))
    datetime = models.DateTimeField(auto_now=True,
                                    verbose_name=_('DateTime'))
    answer = models.ForeignKey(OfferedAnswer, verbose_name=_('Offered Answer'))
    # entered text for inputs
    text = models.CharField(max_length=256, verbose_name=_('Entered Text'))

    def __unicode__(self):
        return '{}: {}: {}'.format(self.client_id,
                                   self.answer,
                                   self.text)
