#!/usr/bin/env python3
"""
Copyright (c) 2021 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import spacy
import pprint
from PyDictionary import PyDictionary
import re
import json
import os.path
fname = 'vocab02.json'

def write_dict(d):
    with open(fname, 'w') as outfile:
        json.dump(d, outfile)

pp = pprint.PrettyPrinter(indent=4)
nlp = spacy.load('en_core_web_sm')
dictionary=PyDictionary()

pp = pprint.PrettyPrinter(indent=4)

wl = set(nlp.vocab.strings)
nwl = set()
for w in wl:
    sent = nlp(w.lower())
    nwl.add(sent[0].lemma_)
#    nwl.add(w.lower())
nwl = list(nwl)
nwl.sort()

entries = dict()
if os.path.isfile(fname):
    with open(fname) as json_file:
        entries = json.load(json_file)


for w in nwl:
    if not re.search("\d", w) and not re.search("\W", w):
        if w in entries.keys():
            continue
        try:
            lookup = dictionary.meaning(w)
            if len(list(lookup.keys())) > 0:
                meanings = list()
                for k in lookup.keys():
                    meanings.append(k)
                entries[w] = meanings
                print(str(len(entries)) + '. ' + w + ': ' + ', '.join(meanings))
                if len(entries) % 100 == 0:
                    write_dict(entries)
                    print('Saved ' + str(len(entries)) + ' entries')
        except:
            continue

write_dict(entries)
print('Saved ' + str(len(entries)) + ' entries')
