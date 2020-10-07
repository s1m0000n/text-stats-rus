import base64
from copy import deepcopy
from io import BytesIO

import matplotlib.pyplot as plt

from text_processing import TextProcessing, find_pos_rus, cases_translation

_td = lambda s: f'<td>{s}</td>'
p = lambda s: f'<p>{s}</p>'
br = lambda s: f'{s}<br>'


def _plt_to_html(fig):
    tempfile = BytesIO()
    fig.savefig(tempfile, format='png')
    encoded = base64.b64encode(tempfile.getvalue()).decode('utf-8')
    return '<img class="img img-fluid" src=\'data:image/png;base64,{}\'>'.format(encoded)


def _table_generator(headings, data):
    """headings: ['h1','h2',...]
        data: [('s1','s2',),...]"""
    headings_repr = '<table class="table"><thead><tr><th scope="col">#</th>' + ''.join(
        [f'<th>{v}</th>' for v in headings]) + '</tr></thead> <tbody>'
    result = headings_repr
    for i, t in enumerate(data):
        line = ''.join([_td(str(el)) for el in t])
        result += f'<tr><th scope="row">{i + 1}</th>{line}</tr>'
    result += '</tbody> </table>'
    return result


def feats_parser(feats):
    feats_translation_names = {
        'Animacy': 'Одушевлённость',
        'Case': 'Падеж',
        'Gender': 'Род',
        'Number': 'Число',
        'Voice': 'Залог',
        'Mood': 'Наклонение',
        'Person': 'Лицо',
        'Tense': 'Время',
        'Aspect': 'Вид',
    }
    feats_translation_values = {
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
    feats_translation_values_aspect = {
        'Imp': 'Несовершенный',
        'Perf': 'Совершенный',
    }

    feats = dict(feats)
    f = deepcopy(feats)
    for key in f.keys():
        if key == 'Aspect':
            if feats[key] in feats_translation_values_aspect.keys():
                feats[key] = feats_translation_values_aspect[feats[key]]
            else:
                feats.pop(key)
        else:
            if feats[key] in feats_translation_values.keys():
                feats[key] = feats_translation_values[feats[key]]
            else:
                feats.pop(key)
        if key in feats_translation_names.keys() and key in feats.keys():
            feats[feats_translation_names[key]] = feats.pop(key)
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
            feats = feats_parser(token.feats)
            feats_s = '<br>'.join([f'{k}: {v.lower()}' for k, v in feats.items()])
            result += f'<tr><th scope="row">{i + 1}</th>{_td(token.text)}{_td(find_pos_rus(token.pos) + f" ({token.pos})")}{_td(token.lemma)}{_td(feats_s)}</tr>'
        result += '</tbody> </table>'
        return result

    def gen_stats_data(self):
        res = ''
        for stat in (f'Средняя длина предложений: {self.avg_sent_len()}',):
            res += br(stat)
        return p(res)

    def gen_stats_with_punct(self):
        res = ''
        for stat in (f'Общее число словоупотреблений: {self.total_lemma_usages()}',
                     f'Число различных словоформ: {len(self.unique_lemmas())}'):
            res += br(stat)
        return p(res)

    def gen_stats_wo_punct(self):
        res = ''
        for stat in (f'Общее число словоупотреблений: {self.total_word_usages()}',
                     f'Число различных словоформ: {len(self.unique_words())}'):
            res += br(stat)
        return p(res)

    def pos_freq(self):
        processed_freqs = [
            (t[3] + f" ({t[2]})", str(t[0]) + ' раз', str(t[1]) + '%', str(t[4]) + ' лемм', str(t[5]) + '%')
            for t in sorted(self.pos_freq_compute(), key=lambda x: x[0], reverse=True)]
        return _table_generator(['Часть речи', 'Абсолютная(словоупотребления)', 'Относительная(словоупотребления)',
                                 'Абсолютная(слова)', 'Относительная(слова)'], processed_freqs)

    def pos_freq_graph(self, use_tokens=True):
        data = sorted(self.pos_freq_compute(), key=lambda x: x[0] if use_tokens else x[4], reverse=True)
        absolutes = [v[0] if use_tokens else v[4] for v in data]
        poses = [f'{v[3]} ({v[2]})' for v in data]
        plt.rcParams['ytick.labelsize'] = 12
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 8, forward=True)
        ax.barh(poses, absolutes, align='center')
        ax.set_yticks(poses)
        ax.set_yticklabels(poses)
        ax.invert_yaxis()
        fig.suptitle('Абсолютная частота(словоупотребления)' if use_tokens else 'Абсолютная частота(слова)', fontsize=20)
        return _plt_to_html(fig)


    def omon_freq(self, top=None, include_stopwords=True):
        processed_freqs = [(t[0], str(t[1]) + ' раз', str(t[2]) + '%') for t in
                           sorted(self.omon_freq_compute(include_stopwords), key=lambda x: x[1], reverse=True)]
        if top is not None:
            processed_freqs = processed_freqs[:top]
        return _table_generator(['Словоформа', 'Абсолютная частота', 'Относительная частота'], processed_freqs)

    def case_analysis_table(self):
        processed_freqs = [(cases_translation[t[0]],
                            str(t[1]) + ' раз', str(t[2]) + '%',
                            str(t[3]) + ' раз', str(t[4]) + '%') for t in self.case_analysis()]
        return _table_generator(
            ['Падеж', 'Абсолютная(сущ.+им.собств.)', 'Относительная(сущ.+им.собств.)', 'Абсолютная(прилагательные)',
             'Относительная(прилагательные)'], processed_freqs)

    def case_analysis_graph_nouns(self):
        data = self.case_analysis()
        labels = [cases_translation[d[0]] for d in data if d[2] != 0]
        sizes = [d[2] for d in data if d[2] != 0]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        fig1.suptitle('Распределение падежей по существительным и именам собственным')
        return _plt_to_html(fig1)

    def case_analysis_graph_adjs(self):
        data = self.case_analysis()
        labels = [cases_translation[d[0]] for d in data if d[4] != 0]
        sizes = [d[4] for d in data if d[4] != 0]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        fig1.suptitle('Распределение падежей по прилагательным')
        return _plt_to_html(fig1)
