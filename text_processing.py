from natasha import MorphVocab, Segmenter, NewsMorphTagger, NewsEmbedding, Doc


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

    def unique_lemmas(self, pos=None):
        if pos is None:
            return set([dt.lemma for dt in self.words])
        else:
            return set([dt.lemma for dt in filter(lambda dt: dt.pos == pos, self.words)])

    def avg_sent_len(self):
        return sum(map(lambda s: len(s.tokens), self.doc.sents)) / len(self.doc.sents)

    def total_word_usages(self):
        return len(self.words)

    def pos_percent(self, pos):
        return round(100 * (len(list(filter(lambda dt: dt.pos == pos, self.words)))/len(self.words)))