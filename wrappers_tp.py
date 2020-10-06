from text_processing import TextProcessing


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
        td = lambda s: f'<td>{s}</td>'
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
