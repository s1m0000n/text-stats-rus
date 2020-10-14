from itertools import chain
from heapq import nlargest
from natasha import MorphVocab, Segmenter, NewsMorphTagger, NewsEmbedding, Doc
from nltk.corpus import stopwords

parts_of_speech = {('NOUN',): 'Существительное', ('VERB',): 'Глагол', ('ADJ',): 'Прилагательное',
                   ('PART', 'AUX',): 'Частица', ('PROPN',): 'Имя собственное', ('DET', 'PRON',): 'Местоимение',
                   ('ADP', 'SCONJ',): 'Предлог', ('PUNCT',): 'Знак препинания',
                   ('', 'X',): 'Неизвестное или иноязычное', ('ADV',): 'Наречие', ('INTJ',): 'Междометие',
                   ('SYM',): 'Символ', ('CCONJ',): 'Союз'}
parts_of_speech_pl = {('NOUN',): 'Существительные', ('VERB',): 'Глаголы', ('ADJ',): 'Прилагательные',
                      ('PART', 'AUX',): 'Частицы', ('PROPN',): 'Имена собственные', ('DET', 'PRON'): 'Местоимения',
                      ('ADP', 'SCONJ',): 'Предлоги', ('PUNCT',): 'Знаки препинания',
                      ('', 'X',): 'Неизвестные и иноязычные', ('ADV',): 'Наречия', ('INTJ',): 'Междометия',
                      ('SYM',): 'Символы', ('CCONJ',): 'Союзы'}
cases_translation = {'Nom': 'Именительный',
                     'Gen': 'Родительный',
                     'Dat': 'Дательный',
                     'Acc': 'Винительный',
                     'Ins': 'Творительный',
                     'Loc': 'Предложный',}
cases = cases_translation.keys()
sw_filter = lambda lst: tuple(filter(lambda x: str(x).lower() not in stopwords.words('russian'), lst))


def pos_name_to_rus(pos, plural=False):
    for item in (parts_of_speech_pl.items() if plural else parts_of_speech.items()):
        if pos in item[0]:
            return item[1]
    return 'Неизвестно'


class TextProcessing:
    def __init__(self, text):
        self.doc = Doc(text)
        self.doc.segment(Segmenter())
        self.doc.tag_morph(NewsMorphTagger(NewsEmbedding()))
        morph_vocab = MorphVocab()
        for token in self.doc.tokens:
            token.lemmatize(morph_vocab)
        self.words = tuple(filter(lambda x: x.pos not in ('X', 'PUNCT'), self.doc.tokens))
        self.tokens_nouns = tuple(filter(lambda t: t.pos in ['NOUN', 'PROPN'], self.doc.tokens))
        self.tokens_adjs = tuple(filter(lambda t: t.pos == 'ADJ', self.doc.tokens))
        self.tokens_verbs = tuple(filter(lambda t: t.pos == 'VERB', self.doc.tokens))

    def unique_lemmas(self, pos=None):
        if pos is None:
            return tuple(set(dt.lemma for dt in self.doc.tokens))
        else:
            return tuple(set(dt.lemma for dt in filter(lambda dt: dt.pos == pos, self.doc.tokens)))

    def unique_words(self, pos = None):
        if pos is None:
            return tuple(set(dt.lemma for dt in self.words))
        else:
            return tuple(set(dt.lemma for dt in filter(lambda dt: dt.pos == pos, self.words)))

    def word_usages(self):
        return tuple(dt.text for dt in self.words)

    def token_usages(self):
        return tuple(dt.text for dt in self.doc.tokens)

    def unique_word_usages(self):
        return tuple(set(self.word_usages()))

    def unique_token_usages(self):
        return tuple(set(self.token_usages()))

    def omonyms_freq_compute(self, include_stopwords=True):
        wu = self.word_usages() if include_stopwords else sw_filter(self.word_usages())
        wu_repeats = {i: wu.count(i) for i in wu}
        res = []
        for case in wu_repeats.items():
            absolute = case[1]
            if absolute > 1:
                relative = round((absolute / len(self.words if include_stopwords else sw_filter(self.words))) * 100)
                text = case[0]
                res.append((text, absolute, relative))
        return tuple(res)

    def avg_sent_len(self):
        return round(sum(map(lambda s: len(s.tokens), self.doc.sents)) / len(self.doc.sents))

    def total_word_usages(self):
        return len(self.words)

    def total_lemma_usages(self):
        return len(self.doc.tokens)

    def pos_freq_compute(self):
        tokens_by_poses = []
        for pos in chain(*parts_of_speech.keys()):
            words_of_pos = tuple(filter(lambda dt: dt.pos == pos, self.words))
            absolute_words_usages = len(words_of_pos)
            if absolute_words_usages != 0:
                relative_word_usages = round((absolute_words_usages / len(self.words)) * 100)
                pos_translated = pos_name_to_rus(pos, True)
                absolute_unique_words = len(self.unique_words(pos))
                relative_unique_words = round((absolute_unique_words / len(self.unique_words())) * 100)
                tokens_by_poses.append((absolute_words_usages, relative_word_usages,
                                        pos, pos_translated,
                                        absolute_unique_words, relative_unique_words))
        return tuple(tokens_by_poses)

    def nouns_adj_by_cases(self):
        nouns = tuple(filter(lambda t: 'Case' in dict(t.feats).keys(), self.tokens_nouns))
        adjs = tuple(filter(lambda t: 'Case' in dict(t.feats).keys(), self.tokens_adjs))
        return tuple((case,
                      tuple(filter(lambda t: t.feats['Case'] == case, nouns)),
                      tuple(filter(lambda t: t.feats['Case'] == case, adjs))) for case in cases)

    def case_analysis(self):
        nabc = self.nouns_adj_by_cases()
        result = []
        for i, case in enumerate(cases):
            abs_nouns = len(nabc[i][1])
            abs_adj = len(nabc[i][2])
            rel_nouns = abs_nouns / len(self.tokens_nouns)
            rel_nouns = round(rel_nouns*100)
            rel_adj = abs_adj / len(self.tokens_adjs)
            rel_adj = round(100*rel_adj)
            abs_sum = abs_nouns + abs_adj
            rel_sum = round((abs_sum / (len(self.tokens_adjs) + len(self.tokens_nouns)))*100)
            result.append((case,
                           abs_nouns, rel_nouns,
                           abs_adj, rel_adj,
                           abs_sum, rel_sum))
        return tuple(result)

    def verb_form_analysis_tense(self):
        verbs = tuple(filter(lambda t: 'Tense' in dict(t.feats).keys(), self.tokens_verbs))
        return tuple((tense, len(tuple(filter(lambda t: t.feats['Tense'] == tense, verbs))))
                     for tense in ('Past', 'Pres', 'Fut'))

    def verb_form_analysis_person(self):
        verbs = tuple(filter(lambda t: 'Person' in dict(t.feats).keys(), self.tokens_verbs))
        return tuple((p, len(tuple(filter(lambda t: t.feats['Person'] == p, verbs))))
                 for p in ('1', '2', '3'))

    def verb_form_analysis_number(self):
        verbs = tuple(filter(lambda t: 'Number' in dict(t.feats).keys(), self.tokens_verbs))
        return tuple((p, len(tuple(filter(lambda t: t.feats['Number'] == p, verbs))))
                     for p in ('Sing', 'Plur'))

    def simple_summarization(self, top = None):
        if top is None:
            top = len(self.doc.sents)*0.20
            if top < 1:
                top = 1
            else:
                top = round(top)
        words = sw_filter(self.words)
        lemma_frequencies = {}
        for word in words:
            if word.lemma not in lemma_frequencies.keys():
                lemma_frequencies[word.lemma] = 1
            else:
                lemma_frequencies[word.lemma] += 1
        max_frequency = max(lemma_frequencies.values())
        sent_scores = {}
        for sentence in self.doc.sents:
            # Cумма относительных частот словоупотреблений для каждого предложения текста
            sent_scores[sentence.text] = sum(tuple(lemma_frequencies[word.lemma]/max_frequency
                                             for word in filter(lambda w: w.lemma in lemma_frequencies.keys(),
                                                                sentence.tokens)))
        summary_sentences = nlargest(top, sent_scores.items(), key=lambda item: item[1])
        return tuple(t for t,_ in summary_sentences)