import base64
from io import BytesIO
from itertools import chain

import matplotlib.pyplot as plt

from text_processing import TextProcessing

parts_os_speech = {('NOUN',): 'Существительное', ('VERB',): 'Глагол', ('ADJ',): 'Прилагательное',
                   ('PART', 'AUX',): 'Частица', ('PROPN',): 'Имя собственное', ('DET',): 'Детерминатив',
                   ('ADP', 'SCONJ',): 'Предлог', ('PUNCT',): 'Знак препинания',
                   ('', 'X',): 'Неизвестное или иноязычное', ('ADV',): 'Наречие', ('INTJ',): 'Междометие',
                   ('SYM',): 'Символ'}

parts_of_speech_pl = {('NOUN',): 'Существительные', ('VERB',): 'Глаголы', ('ADJ',): 'Прилагательные',
                      ('PART', 'AUX',): 'Частицы', ('PROPN',): 'Имена собственные', ('DET',): 'Детерминативы',
                      ('ADP', 'SCONJ',): 'Предлоги', ('PUNCT',): 'Знаки препинания',
                      ('', 'X',): 'Неизвестные и иноязычные', ('ADV',): 'Наречия', ('INTJ',): 'Междометия',
                      ('SYM',): 'Символы'}


def find_pos_rus(pos, plural=False):
    for item in (parts_of_speech_pl.items() if plural else parts_os_speech.items()):
        # item: (('s1', 's2', ...), 'rus')
        if pos in item[0]:
            return item[1]


td = lambda s: f'<td>{s}</td>'


def plt_to_html(fig):
    tempfile = BytesIO()
    fig.savefig(tempfile, format='png')
    encoded = base64.b64encode(tempfile.getvalue()).decode('utf-8')
    return '<img class="img img-fluid" src=\'data:image/png;base64,{}\'>'.format(encoded)


class HtmlTP(TextProcessing):
    def __init__(self, text):
        super().__init__(text)
        self.pos_freq_data = self.pos_freq_compute()

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
            result += f'<tr><th scope="row">{i + 1}</th>{td(token.text)}{td(token.pos)}{td(token.lemma)}{td(token.feats)}</tr>'
        result += '</tbody> </table>'
        return result

    def gen_stats(self):
        p = lambda s: f'<p>{s}</p>'
        br = lambda s: f'{s}<br>'
        res = ''
        for stat in (f'Общее число словоупотреблений: {self.total_word_usages()}',
                     f'Число различных словоформ: {len(self.unique_lemmas())}',
                     f'Средняя длина предложений: {self.avg_sent_len()}'):
            res += br(stat)
        return p(res)

    def pos_freq_compute(self):
        tokens_by_poses = []
        for pos in chain(*parts_os_speech.keys()):
            tokens_of_pos = list(filter(lambda dt: dt.pos == pos, self.doc.tokens))
            absolute = len(tokens_of_pos)
            if absolute != 0:
                relative = round((absolute / len(self.doc.tokens)) * 100)
                pos_translated = find_pos_rus(pos, True)
                tokens_by_poses.append((absolute, relative, pos, pos_translated))
        tokens_by_poses.sort(key=lambda x: x[0], reverse=True)
        return tokens_by_poses

    def pos_freq(self):
        result = '''<table class="table">\n<thead><tr>\n
              <th scope="col">#</th>
              <th scope="col">Часть речи</th>
              <th scope="col">Абсолютная частота</th>
              <th scope="col">Относительная частота</th>
            </tr>
          </thead> <tbody>'''
        for i, t in enumerate(self.pos_freq_data):
            result += f'<tr><th scope="row">{i + 1}</th>{td(t[3] + f" ({t[2]})")}{td(str(t[0]) + " раз")}{td(str(t[1]) + "%")}</tr>'
        result += '</tbody> </table>'
        return result

    def pos_freq_graph(self):
        data = self.pos_freq_data
        absolutes = [v[0] for v in data]
        poses = [v[3] + f' ({v[2]})' for v in data]
        plt.rcParams['ytick.labelsize'] = 12
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 8, forward=True)
        ax.barh(poses, absolutes, align='center')
        ax.set_yticks(poses)
        ax.set_yticklabels(poses)
        ax.invert_yaxis()
        ax.set_xlabel('Абсолютная частота')
        return plt_to_html(fig)
