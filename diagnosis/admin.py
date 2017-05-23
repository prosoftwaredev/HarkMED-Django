from django.contrib import admin
from .models import Diagnosis, Question, OfferedAnswer, Condition
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from mce_filebrowser.admin import MCEFilebrowserAdmin


class ConditionAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description')
    list_display = ('title', 'description')
    fields = ('title', 'description')


class ConditionInline(admin.StackedInline):
    model = Condition
    extra = 1


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class DiagnosisAdmin(MCEFilebrowserAdmin):
    prepopulated_fields = {'title': ('name',)}
    fields = ('title', 'name', 'description', 'conditions', 'active')
    list_display = ('title', 'name', 'active')
    search_fields = ('title', 'description')
    list_filter = ('active',)
    inlines = [QuestionInline]


class OfferedAnswerInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        super(OfferedAnswerInlineFormSet, self).clean()

        cnt = 0
        question = None
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if 'answer_type' in data and data['answer_type'] == 'I':
                cnt += 1
            if not question:
                if 'question' in data:
                    question = data['question']
        if question and question.question_type in ('CI', 'RI') and cnt > 1:
            raise ValidationError(_('Choice with input and multiple choice'
                                  ' with input type of question cannot have'
                                  ' more than one input type of answer'))


class OfferedAnswerInline(admin.StackedInline):
    model = OfferedAnswer
    formset = OfferedAnswerInlineFormSet
    fk_name = 'question'
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    inlines = [OfferedAnswerInline]
    list_display = ('diagnosis', 'text', )
    search_fields = ('text', 'offeredanswer__prefix',
                     'offeredanswer__answer_type',
                     'offeredanswer__text',
                     'offeredanswer__sufix',)
    list_filter = ('question_type', 'requires_answer', 'diagnosis' )


class OfferedAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'next_question', 'prefix', 'text', 'sufix', 'sort_index')
    search_fields = ('question__text', 'prefix', 'text', 'sufix')
    list_filter = ('answer_type', 'question', 'question__diagnosis')


admin.site.register(Diagnosis, DiagnosisAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(OfferedAnswer, OfferedAnswerAdmin)
