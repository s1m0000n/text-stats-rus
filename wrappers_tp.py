import base64
from copy import deepcopy
from io import BytesIO
import matplotlib.pyplot as plt
from text_processing import TextProcessing, pos_name_to_rus, cases_translation

td = lambda s: f'<td>{s}</td>'
p = lambda s: f'<p>{s}</p>'
br = lambda s: f'{s}<br>'
translation_keys = {
    'Animacy': 'Одушевлённость',
    'Case': 'Падеж',
    'Gender': 'Род',
    'Number': 'Число',
    'Voice': 'Залог',
    'Mood': 'Наклонение',
    'Person': 'Лицо',
    'Tense': 'Время',
    'Aspect': 'Вид'}
translation_values = {
    'Nom': 'Именительный',
    'Gen': 'Родительный',
    'Loc': 'Предложный',
    'Acc': 'Винительный',
    'Ins': 'Творительный',
    'Dat': 'Дательный',
    'Inan': 'Неодушевлённое',
    'Anim': 'Одушевлённое',
    'Masc': 'Мужской',
    'Neut': 'Средний',
    'Fem': 'Женский',
    'Sing': 'Единственное',
    'Plur': 'Множественное',
    'Mid': 'Пассивный',
    'Act': 'Активный',
    'Ind': 'Изъявительное',
    'Imp': 'Повелительное',
    '3': '3-е',
    '2': '2-е',
    '1': '1-е',
    'Pres': 'Настоящее',
    'Fut': 'Будущее',
    'Past': 'Прошедшее',
}
translation_values_aspect = {
    'Imp': 'Несовершенный',
    'Perf': 'Совершенный'}


def fig_to_html(fig):
    tempfile = BytesIO()
    fig.savefig(tempfile, format='png')
    encoded = base64.b64encode(tempfile.getvalue()).decode('utf-8')
    return '<img class="img img-fluid" src=\'data:image/png;base64,{}\'>'.format(encoded)


def table_to_html(headings, data):
    return '<table class="table"><thead><tr><th scope="col">#</th>' + \
           ''.join(tuple(f'<th>{v}</th>' for v in headings)) + '</tr></thead> <tbody>' + \
           ''.join(tuple(f'<tr><th scope="row">{i + 1}</th>' + ''.join(tuple(td(str(el)) for el in t)) +
                         '</tr>' for i, t in enumerate(data))) + '</tbody> </table>'


def translate_features(feats):
    feats = dict(feats)
    f = deepcopy(feats)
    for key in f.keys():
        if key == 'Aspect':
            if feats[key] in translation_values_aspect.keys():
                feats[key] = translation_values_aspect[feats[key]]
            else:
                feats.pop(key)
        else:
            if feats[key] in translation_values.keys():
                feats[key] = translation_values[feats[key]]
            else:
                feats.pop(key)
        if key in translation_keys.keys() and key in feats.keys():
            feats[translation_keys[key]] = feats.pop(key)
    return feats


class HtmlTP(TextProcessing):
    def __init__(self, text):
        super().__init__(text)

    def morhp_analysis(self, pos=None, include_punct=False):
        tokens = self.doc.tokens if include_punct else self.words
        if pos is not None:
            tokens = filter(lambda dt: dt.pos == pos, tokens)
        # generating html code
        result = '''<table class="table">\n<thead><tr>\n
      <th scope="col">#</th>
      <th scope="col">Словоупотребление</th>
      <th scope="col">Часть речи</th>
      <th scope="col">Начальная форма(лемма)</th>
      <th scope="col">Прочие характеристики</th>
    </tr>
  </thead> <tbody>'''
        for i, token in enumerate(tokens):
            # preparing features
            feats = translate_features(token.feats)
            feats_s = ',<br>'.join(tuple(f'{k}: {v.lower()}' for k, v in feats.items()))
            result += f'<tr><th scope="row">{i + 1}</th>{td(token.text)}{td(pos_name_to_rus(token.pos) + f" ({token.pos})")}{td(token.lemma)}{td(feats_s)}</tr>'
        result += '</tbody> </table>'
        return result

    def gen_stats_data(self):
        res = ''
        for stat in (f'Всего предложений: {len(self.doc.sents)}',
                     f'Средняя длина предложений: {self.avg_sent_len()}'):
            res += br(stat)
        return p(res)

    def gen_stats_with_punct(self):
        res = ''
        for stat in (f'Общее число словоупотреблений: {self.total_lemma_usages()}',
                     f'Число различных словоформ: {len(self.unique_token_usages())}',
                     f'Число уникальных лемм: {len(self.unique_lemmas())}'):
            res += br(stat)
        return p(res)

    def gen_stats_wo_punct(self):
        res = ''
        for stat in (f'Общее число словоупотреблений: {self.total_word_usages()}',
                     f'Число различных словоформ: {len(self.unique_word_usages())}',
                     f'Число разных слов: {len(self.unique_words())}'):
            res += br(stat)
        return p(res)

    def pos_freq(self):
        processed_freqs = tuple(
            (t[3] + f" ({t[2]})", str(t[0]), str(t[1]) + '%', str(t[4]), str(t[5]) + '%')
            for t in sorted(self.pos_freq_compute(), key=lambda x: x[0], reverse=True))
        return table_to_html(('Часть речи', 'Абсолютная(словоупотребления)', 'Относительная(словоупотребления)',
                              'Абсолютная(слова)', 'Относительная(слова)'), processed_freqs)

    def pos_freq_graph(self, use_tokens=True):
        data = sorted(self.pos_freq_compute(), key=lambda x: x[0] if use_tokens else x[4], reverse=True)
        absolutes = tuple(v[0] if use_tokens else v[4] for v in data)
        poses = tuple(f'{v[3]} ({v[2]})' for v in data)
        plt.rcParams['ytick.labelsize'] = 12
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 8, forward=True)
        ax.barh(poses, absolutes, align='center')
        ax.set_yticks(poses)
        ax.set_yticklabels(poses)
        ax.invert_yaxis()
        fig.suptitle('Абсолютная частота(словоупотребления)' if use_tokens else 'Абсолютная частота(слова)',
                     fontsize=20)
        return fig_to_html(fig)

    def omon_freq(self, top=None, include_stopwords=True):
        processed_freqs = tuple((t[0], str(t[1]), str(t[2]) + '%') for t in
                           sorted(self.omon_freq_compute(include_stopwords), key=lambda x: x[1], reverse=True))
        if top is not None:
            processed_freqs = processed_freqs[:top]
        return table_to_html(('Словоформа', 'Абсолютная частота', 'Относительная частота'), processed_freqs)

    def case_analysis_table(self):
        processed_freqs = tuple((cases_translation[t[0]],
                            str(t[1]), str(t[2]) + '%',
                            str(t[3]), str(t[4]) + '%',
                            str(t[5]), str(t[6]) + '%') for t in self.case_analysis())
        return table_to_html(
            ('Падеж', 'abs(сущ.+им.собств.)', 'rel(сущ.+им.собств.)', 'abs(прилагательные)',
             'rel(прилагательные)', '&#8721; abs', '&#8721; rel'), processed_freqs)

    def case_analysis_graph_nouns(self):
        data = self.case_analysis()
        labels = tuple(cases_translation[d[0]] for d in data if d[2] != 0)
        sizes = tuple(d[2] for d in data if d[2] != 0)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        fig1.suptitle('Распределение падежей по существительным и именам собственным')
        return fig_to_html(fig1)

    def case_analysis_graph_adjs(self):
        data = self.case_analysis()
        labels = tuple(cases_translation[d[0]] for d in data if d[4] != 0)
        sizes = tuple(d[4] for d in data if d[4] != 0)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        fig1.suptitle('Распределение падежей по прилагательным')
        return fig_to_html(fig1)

    def case_analysis_graph_sum(self):
        data = self.case_analysis()
        labels = tuple(cases_translation[d[0]] for d in data if d[6] != 0)
        sizes = tuple(d[6] for d in data if d[6] != 0)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        fig1.suptitle('Суммарное распределение падежей')
        return fig_to_html(fig1)

    def verb_form_analysis_tense_table(self):
        processed_freqs = tuple((translation_values[t[0]], str(t[1])) for t in self.verb_form_analysis_tense())
        return table_to_html(('Время', 'Количество словоупотреблений'), processed_freqs)

    def verb_form_analysis_person_table(self):
        processed_freqs = tuple((translation_values[t[0]], str(t[1])) for t in self.verb_form_analysis_person())
        return table_to_html(('Лицо', 'Количество словоупотреблений'), processed_freqs)

    def verb_form_analysis_number_table(self):
        processed_freqs = tuple((translation_values[t[0]], str(t[1])) for t in self.verb_form_analysis_number())
        return table_to_html(('Число', 'Количество словоупотреблений'), processed_freqs)

    def summary(self):
        return ' '.join(self.simple_summarization())

    def top_sents(self, top=10):
        sents = tuple((s,) for s in self.simple_summarization(top))
        return table_to_html(('Предложение',), sents)
