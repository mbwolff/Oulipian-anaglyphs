#!/usr/bin/env python3
"""
Copyright (c) 2021 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from nltk.corpus import brown
from pattern.en import parse
#import pprint
import re
import pickle
#import os.path
fname = 'vocab03.pickle'

#pp = pprint.PrettyPrinter(indent=4)
#nlp = spacy.load('en_core_web_sm')
#dictionary=PyDictionary()

dictionary = dict()

#wl = set(nlp.vocab.strings)
for chunk in brown.sents():
    text = ' '.join(chunk)
    for sent in parse(text, chunks=False, lemmata=True).split():
        for token in sent:
#            if not re.match("[A-Za-z]", token[0]):
#                continue
#            elif token[2] in dictionary.keys():
            if token[2] in dictionary.keys():
                dictionary[token[2]].add(token[1])
            else:
                dictionary[token[2]] = { token[1] }

with open(fname, 'wb') as handle:
    pickle.dump(dictionary, handle)

print('Saved ' + str(len(dictionary.keys())) + ' entries')
