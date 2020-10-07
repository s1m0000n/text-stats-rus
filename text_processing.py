from itertools import chain

from natasha import MorphVocab, Segmenter, NewsMorphTagger, NewsEmbedding, Doc
from nltk.corpus import stopwords

_parts_of_speech = {('NOUN',): 'Существительное', ('VERB',): 'Глагол', ('ADJ',): 'Прилагательное',
                    ('PART', 'AUX',): 'Частица', ('PROPN',): 'Имя собственное', ('DET', 'PRON',): 'Местоимение',
                    ('ADP', 'SCONJ',): 'Предлог', ('PUNCT',): 'Знак препинания',
                    ('', 'X',): 'Неизвестное или иноязычное', ('ADV',): 'Наречие', ('INTJ',): 'Междометие',
                    ('SYM',): 'Символ', ('CCONJ',): 'Союз'}

_parts_of_speech_pl = {('NOUN',): 'Существительные', ('VERB',): 'Глаголы', ('ADJ',): 'Прилагательные',
                       ('PART', 'AUX',): 'Частицы', ('PROPN',): 'Имена собственные', ('DET', 'PRON'): 'Местоимения',
                       ('ADP', 'SCONJ',): 'Предлоги', ('PUNCT',): 'Знаки препинания',
                       ('', 'X',): 'Неизвестные и иноязычные', ('ADV',): 'Наречия', ('INTJ',): 'Междометия',
                       ('SYM',): 'Символы', ('CCONJ',): 'Союзы'}

cases_translation = {'Nom': 'Именительный',
                     'Gen': 'Родительный',
                     'Dat': 'Дательный',
                     'Acc': 'Винительный',
                     'Ins': 'Творительный',
                     'Loc': 'Предложный',

                     }

cases = cases_translation.keys()

sw_filter = lambda lst: list(filter(lambda x: str(x).lower() not in stopwords.words('russian'), lst))


def find_pos_rus(pos, plural=False):
    for item in (_parts_of_speech_pl.items() if plural else _parts_of_speech.items()):
        if pos in item[0]:
            return item[1]
    return 'Неизвестно'


class TextProcessing:
    def __init__(self, text):
        self.doc = Doc(text)
        self.doc.segment(Segmenter())
        emb = NewsEmbedding()
        morph_vocab = MorphVocab()
        self.doc.tag_morph(NewsMorphTagger(emb))

        self.words = []
        for token in self.doc.tokens:
            token.lemmatize(morph_vocab)
            if token.pos not in ('X', 'PUNCT'):
                self.words.append(token)

        self.tokens_nouns = list(filter(lambda t: t.pos in ['NOUN', 'PROPN'], self.doc.tokens))
        self.tokens_adjs = list(filter(lambda t: t.pos == 'ADJ', self.doc.tokens))

    def unique_lemmas(self, pos=None):
        if pos is None:
            return list(set([dt.lemma for dt in self.doc.tokens]))
        else:
            return list(set([dt.lemma for dt in filter(lambda dt: dt.pos == pos, self.doc.tokens)]))

    def unique_words(self):
        return list(set([dt.lemma for dt in self.words]))

    def word_usages(self):
        return [dt.text for dt in self.words]

    def token_usages(self):
        return [dt.text for dt in self.doc.tokens]

    def unique_word_usages(self):
        return list(set(self.word_usages()))

    def unique_token_usages(self):
        return list(set(self.token_usages()))

    def omon_freq_compute(self, include_stopwords=True):
        wu = self.word_usages() if include_stopwords else sw_filter(self.word_usages())
        wu_repeats = {i: wu.count(i) for i in wu}
        res = []
        for case in wu_repeats.items():
            absolute = case[1]
            if absolute > 1:
                relative = round((absolute / len(self.words if include_stopwords else sw_filter(self.words))) * 100)
                text = case[0]
                res.append((text, absolute, relative))
        return res

    def avg_sent_len(self):
        return round(sum(map(lambda s: len(s.tokens), self.doc.sents)) / len(self.doc.sents))

    def total_word_usages(self):
        return len(self.words)

    def total_lemma_usages(self):
        return len(self.doc.tokens)

    def pos_freq_compute(self):
        tokens_by_poses = []
        for pos in chain(*_parts_of_speech.keys()):
            tokens_of_pos = list(filter(lambda dt: dt.pos == pos, self.doc.tokens))
            absolute_wu = len(tokens_of_pos)
            if absolute_wu != 0:
                relative_wu = round((absolute_wu / len(self.doc.tokens)) * 100)
                pos_translated = find_pos_rus(pos, True)
                unique_lemmas_pos = self.unique_lemmas(pos)
                absolute_ul = len(unique_lemmas_pos)
                relative_ul = round((absolute_ul / len(self.unique_lemmas())) * 100)
                tokens_by_poses.append((absolute_wu, relative_wu, pos, pos_translated, absolute_ul, relative_ul))
        return tokens_by_poses

    def nouns_adj_by_cases(self):
        nouns = list(filter(lambda t: 'Case' in dict(t.feats).keys(), self.tokens_nouns))
        adjs = list(filter(lambda t: 'Case' in dict(t.feats).keys(), self.tokens_adjs))
        result = []
        for case in cases:
            result.append((case,
                           list(filter(lambda t: t.feats['Case'] == case, nouns)),
                           list(filter(lambda t: t.feats['Case'] == case, adjs))))
        return result

    def case_analysis(self):
        #         ret: [(case, abs_nouns, rel_nouns, abs_adj, rel_adj), ]
        nabc = self.nouns_adj_by_cases()
        result = []
        for i, case in enumerate(cases):
            abs_nouns = len(nabc[i][1])
            abs_adj = len(nabc[i][2])
            rel_nouns = abs_nouns / len(self.tokens_nouns)
            rel_adj = abs_adj / len(self.tokens_adjs)
            result.append((case,
                           abs_nouns, round(rel_nouns*100),
                           abs_adj, round(100*rel_adj)))
        return result
