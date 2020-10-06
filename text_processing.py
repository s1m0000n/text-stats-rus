from itertools import chain

from natasha import MorphVocab, Segmenter, NewsMorphTagger, NewsEmbedding, Doc

_parts_of_speech = {('NOUN',): 'Существительное', ('VERB',): 'Глагол', ('ADJ',): 'Прилагательное',
                    ('PART', 'AUX',): 'Частица', ('PROPN',): 'Имя собственное', ('DET',): 'Детерминатив',
                    ('ADP', 'SCONJ',): 'Предлог', ('PUNCT',): 'Знак препинания',
                    ('', 'X',): 'Неизвестное или иноязычное', ('ADV',): 'Наречие', ('INTJ',): 'Междометие',
                    ('SYM',): 'Символ'}

_parts_of_speech_pl = {('NOUN',): 'Существительные', ('VERB',): 'Глаголы', ('ADJ',): 'Прилагательные',
                       ('PART', 'AUX',): 'Частицы', ('PROPN',): 'Имена собственные', ('DET',): 'Детерминативы',
                       ('ADP', 'SCONJ',): 'Предлоги', ('PUNCT',): 'Знаки препинания',
                       ('', 'X',): 'Неизвестные и иноязычные', ('ADV',): 'Наречия', ('INTJ',): 'Междометия',
                       ('SYM',): 'Символы'}


def _find_pos_rus(pos, plural=False):
    for item in (_parts_of_speech_pl.items() if plural else _parts_of_speech.items()):
        if pos in item[0]:
            return item[1]


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

        self.pos_freq_data = self.pos_freq_compute()

    def unique_lemmas(self, pos=None):
        if pos is None:
            return set([dt.lemma for dt in self.words])
        else:
            return set([dt.lemma for dt in filter(lambda dt: dt.pos == pos, self.words)])

    def avg_sent_len(self):
        return sum(map(lambda s: len(s.tokens), self.doc.sents)) / len(self.doc.sents)

    def total_word_usages(self):
        return len(self.words)

    def pos_freq_compute(self):
        tokens_by_poses = []
        for pos in chain(*_parts_of_speech.keys()):
            tokens_of_pos = list(filter(lambda dt: dt.pos == pos, self.doc.tokens))
            absolute = len(tokens_of_pos)
            if absolute != 0:
                relative = round((absolute / len(self.doc.tokens)) * 100)
                pos_translated = _find_pos_rus(pos, True)
                tokens_by_poses.append((absolute, relative, pos, pos_translated))
        tokens_by_poses.sort(key=lambda x: x[0], reverse=True)
        return tokens_by_poses
