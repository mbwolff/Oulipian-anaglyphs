#!/usr/bin/env python3
"""
Copyright (c) 2021 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from flask import Flask, request, session, render_template
import spacy
import json
import regex
import mlconjug3
import sys
import pprint

app = Flask(__name__)
application = app
if __name__ == "__main__":
    app.run()

# Set the secret key to some random bytes. Keep this really secret!
nlp = spacy.load('en_core_web_sm')
vocab_file = 'splus7/vocab02.json'

with open(vocab_file) as json_file:
    vocab_dict = json.load(json_file)
vocab = list(vocab_dict.keys())
vocab.sort()

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mlc = mlconjug3.Conjugator(language='en')

@app.route('/')
def index():
    if 'words' in session:
        del session['words']
#        del session['parsed']
        del session['text']
        session.modified = True
    return render_template('index.html')

@app.route('/display', methods=['GET', 'POST'])
def display():
    if 'words' in session:
#        eprint('first')
#        eprint(pprint.pprint(session['words']))
        words = mod_word(session['words'], int(request.args.get('w')), int(request.args.get('d')))
        eprint(pprint.pprint(words))
        session['words'] = words
        session.modified = True
#        eprint(pprint.pprint(session['words']))
#        eprint(pprint.pprint(words))
    elif 'text' in request.form:
#        eprint('second')
        session['text'] = request.form['text']
        session['step'] = request.form['step']
        session['words'] = parse(request.form['text'], int(request.form['step']))
        eprint(pprint.pprint(session['words']))
    else:
        return render_template('error.html')

#    session['words'] = words
    session.modified = True
#    eprint(pprint.pprint(words))
    ws = conjugate_verbs(session['words'])
    return render_template('display.html', words=ws, text=session['text'], step=session['step'])

def mod_word(words, i, d):
    step = int(session['step'])
#    w = regex.sub(r'[[:punct:]]+$', '', words[i][1][d])
#    punct = regex.sub(r'^[[:alnum:]]+', '', words[i][1][d])
#    eprint('W', w, 'P', p)
#    eprint('Testing vocab', w, vocab.index(w))
    if words[i][1][d] in vocab:
        words[i][1] = get_ten_around(vocab.index(words[i][1][d]), words[i][0], step)
#        for j in range(11):
#            words[i][1][j] += punct
    return words

def parse(text, step):
    word_array = list()
    parsed = list()

    for token in nlp(text):
        parsed.append(token.text)
        word_list = [token.lemma_] * 11
        pos = token.pos_
        string = token.lemma_
        if token.pos_ in {'VERB', 'NOUN', 'PROPN', 'ADJ', 'ADV'} and string.lower() in vocab:
            pos = token.pos_
            if token.pos_ == 'VERB':
                pos = token.tag_
            elif token.pos_ == 'PROPN':
                pos = 'NOUN'
                string = string.lower()
#            word_list = find_words(token.text, token.pos_)
#            punct = regex.sub(r'^[[:alnum:]]+', '', string)
#            string = regex.sub(r'[[:punct:]]+$', '', string)
#            eprint('String', string, 'P', punct)
#            eprint('Testing vocab', string, vocab.index(string))
            word_list = get_ten_around(vocab.index(string), pos, step)
        word_array.append([pos, word_list])
#        if token.pos_ not in {'PUNCT', 'SYM'}:
#            parsed.append(token.text)
    session['parsed'] = parsed
    session.modified = True
    return check_capitalization(word_array)

def get_ten_around(i, pos, step):
    pos_map = {'VERB': 'Verb', 'NOUN': 'Noun', 'ADJ': 'Adjective', 'ADV': 'Adverb'}

    tag_map = { 'VB': 'VERB', 'VBD': 'VERB', 'VBG': 'VERB', 'VBN': 'VERB', 'VBP': 'VERB', 'VBZ': 'VERB', 'JJ': 'ADJ', 'JJR': 'ADJ', 'JJS': 'ADJ', 'NN': 'NOUN', 'NNP': 'NOUN', 'NNPS': 'NOUN', 'NNS': 'NOUN', 'RB': 'ADV', 'RBR': 'ADV', 'RBS': 'ADV', 'RP': 'ADV'}

    def get_five(i, pos, step):
        word_list = list()
#        tag = pos
#        if pos[0] == 'V':
#            pos = 'VERB'
        while len(word_list) < 5:
            i += step
            ind = i % len(vocab)
            if pos in vocab_dict[vocab[ind]]:
                if step > 0:
                    word_list.append(vocab[ind])
                else:
                    word_list.insert(0,vocab[ind])
        return word_list

    if pos[0] == 'V':
        pos = 'VERB'
    return get_five(i, pos_map[pos], -step) + [vocab[i]] + get_five(i, pos_map[pos], step)

def check_capitalization(a):
    orig = session['parsed']
    p = regex.compile(r"^[[:upper:]]+")
    for j in range(len(a)): # len(a) = number of words in version
        for i in range(11): # there are 11 versions
            if p.match(orig[j]):
                a[j][1][i] = a[j][1][i].capitalize()
    return a

def conjugate_verbs(wa):
    def conj(base, t):
        c = str()
        if t == 'VBD':
            c = mlc.conjugate(base).conjug_info['indicative']['indicative past tense']['1s']
        elif t == 'VBG':
            c = mlc.conjugate(base).conjug_info['indicative']['indicative present continuous']['1s']
        elif t == 'VBN':
            c = mlc.conjugate(base).conjug_info['indicative']['indicative present perfect']['1s']
        elif t == 'VBP':
            c = mlc.conjugate(base).conjug_info['indicative']['indicative present']['1s']
        elif t == 'VBZ':
            c = mlc.conjugate(base).conjug_info['indicative']['indicative present']['3s']
        else: # VB
            c = base
#        eprint(base, t, c)
        return c

#    for w in wa:
#    eprint(pprint.pprint(wa))
    for i in range(len(wa)):
#        eprint(wa[i][0])
        if wa[i][0][0] == 'V':
#        if w[0][0] == 'V':
#            for f in w[1]:
            for j in range(len(wa[i][1])):
#                eprint(wa[i][1][j], wa[i][0])
                wa[i][1][j] = conj(wa[i][1][j], wa[i][0])
#                eprint(wa[i][1][j])
#                f = conjugate(f, w[0])
#                eprint(f)
    return wa

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
