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

pp = pprint.PrettyPrinter(indent=4)
nlp = spacy.load('en_core_web_sm')
dictionary=PyDictionary()

pp = pprint.PrettyPrinter(indent=4)

wl = set(nlp.vocab.strings)
nwl = set()
for w in wl:
    nwl.add(w.lower())
nwl = list(nwl)
nwl.sort()

entries = dict()
for w in nwl:
    if not re.search("\d", w) and not re.search("\W", w):
        try:
            lookup = dictionary.meaning(w)
            if len(list(lookup.keys())) > 0:
                meanings = list()
                for k in lookup.keys():
                    meanings.append(k)
#                entries.append({w:meanings})
                entries[w] = meanings
#                pp.pprint({w:meanings})
#                print(str(len(entries)),w,meanings.join(', '))
                print(str(len(entries)) + '. ' + w + ': ' + ', '.join(meanings))
#                if len(entries) == 100:
#                    break
        except:
            continue

with open('vocab.json', 'w') as outfile:
    json.dump(entries, outfile)
