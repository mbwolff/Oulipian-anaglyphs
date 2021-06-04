#!/usr/bin/env python3
"""
Copyright (c) 2021 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import spacy
import pprint
import re

pp = pprint.PrettyPrinter(indent=4)
nlp = spacy.load('en_core_web_sm')
# pp.pprint(set(nlp.vocab.strings))

wl = set(nlp.vocab.strings)
nwl = set()
for w in wl:
    nwl.add(w.lower())
nwl = list(nwl)
nwl.sort()

for w in nwl:
    if re.search("^[a-z]", w):
        print(w)
