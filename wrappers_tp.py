import base64
from io import BytesIO

import matplotlib.pyplot as plt

from text_processing import TextProcessing

_td = lambda s: f'<td>{s}</td>'


def _plt_to_html(fig):
    tempfile = BytesIO()
    fig.savefig(tempfile, format='png')
    encoded = base64.b64encode(tempfile.getvalue()).decode('utf-8')
    return '<img class="img img-fluid" src=\'data:image/png;base64,{}\'>'.format(encoded)


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
            result += f'<tr><th scope="row">{i + 1}</th>{_td(token.text)}{_td(token.pos)}{_td(token.lemma)}{_td(token.feats)}</tr>'
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

    def pos_freq(self):
        result = '''<table class="table">\n<thead><tr>\n
              <th scope="col">#</th>
              <th scope="col">Часть речи</th>
              <th scope="col">Абсолютная частота</th>
              <th scope="col">Относительная частота</th>
            </tr>
          </thead> <tbody>'''
        for i, t in enumerate(self.pos_freq_data):
            result += f'<tr><th scope="row">{i + 1}</th>{_td(t[3] + f" ({t[2]})")}{_td(str(t[0]) + " раз")}{_td(str(t[1]) + "%")}</tr>'
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
        return _plt_to_html(fig)
