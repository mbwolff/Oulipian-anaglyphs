#!/usr/bin/env python3
"""
Copyright (c) 2021 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from flask import Flask, request, session, render_template
#import spacy
from pattern.en import pluralize, conjugate, parse, superlative, comparative, lemma
import pickle
import re, regex
#import mlconjug3
import sys
import nltk

app = Flask(__name__)
application = app
if __name__ == "__main__":
    app.run()

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
select_treebank = {'VB', 'VBZ', 'VBP', 'VBD', 'VBN', 'VBG', 'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'}
pos_map = {
    'Noun': ['NN', 'NNS', 'NNP', 'NNPS'],
    'Verb': ['VB', 'VBZ', 'VBP', 'VBD', 'VBN', 'VBG'],
    'Adjective': ['JJ', 'JJR', 'JJS'],
    'Adverb': ['RB', 'RBR', 'RBS']
}

dict_fname = 'splus7/vocab03.pickle'
with open(dict_fname, 'rb') as handle:
    vocab_dict = pickle.load(handle)
vocab = list(vocab_dict.keys())
vocab.sort()

@app.route('/')
def index():
    pos = ['Noun', 'Verb', 'Adjective', 'Adverb']
    if 'words' in session:
        del session['words']
#        del session['parsed']
        del session['text']
        del session['display']
        for type in pos:
            if type in session:
                del session[type]
    session['display'] = 'normal'
    session['step'] = 1
    session['partsofspeech'] = pos
    session.modified = True
    return render_template('index.html')

@app.route('/display', methods=['GET', 'POST'])
def display():
    if 'message' in session:
        del session['message']
    words = list()
    if 'text' in request.form:
        session['text'] = request.form['text']
        session['step'] = request.form['step']
        session['display'] = request.form['display']
        pos = list()
        for type in session['partsofspeech']:
            if type in request.form:
                pos += pos_map[type]
                session[type] = 'on'
            elif type in session:
                del session[type]
            session.modified = True
        if len(pos) == 0:
            session['message'] = 'Please select at least one part of speech to modify.'
            session.modified = True
            return render_template('index.html')
        words = parse_input(request.form['text'], int(request.form['step']), pos)
    else:
        return render_template('error.html')

    session['words'] = words
    session.modified = True
    displayed = prep_display(words)
    return render_template('display.html', displayed=displayed)

def parse_input(text, step, pos):
    word_array = list()
    parsed = list()

    for sent in parse(text, chunks=False, lemmata=True).split():
        for token in sent:
            parsed.append(token[0])
            word_list = [token[0]] * 11
            if token[2] in {'be', 'have'} and token[1][:2] == 'VB':
                word_list = [token[0]] * 11
            elif token[1] in {'.', ',', ':'} and len(word_array) > 0:
            # Penn Treebank II tag set
                for i in range(11):
                    word_array[-1][1][i] += token[0]
                parsed.remove(token[0])
                continue
#            elif token[1] in select_treebank and token[2] in vocab_dict.keys():
            elif token[1] in pos and token[2] in vocab_dict.keys():
                word_list = get_ten_around(vocab.index(token[2]), token[1], step)
            word_array.append([token[1], word_list])

    session['parsed'] = parsed
    session.modified = True
    return word_array

def get_ten_around(i, pos, step):
    return get_five(i, pos, -step) + [vocab[i]] + get_five(i, pos, step)

def prep_display(a): # capitalize and conjugate, pluralize, etc.
    orig = session['parsed']
    p = regex.compile(r"^[[:upper:]]+")
    for j in range(len(a)): # len(a) = number of words in version
        for i in range(11): # there are 11 versions
            a[j][1][i] = find_form(a[j][1][i], a[j][0])
            if j < len(a) - 1 and a[j][0] == 'DT':
                if a[j][1][i].lower() == 'a' and a[j+1][1][i][0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    a[j][1][i] = 'an'
                elif a[j][1][i].lower() == 'an' and a[j+1][1][i][0].lower() not in ['a', 'e', 'i', 'o', 'u']:
                    a[j][1][i] = 'a'
            if p.match(orig[j]):
                a[j][1][i] = a[j][1][i].capitalize()
    return a

def get_five(i, pos, step):
#    initial_lemma = vocab[i]
    word_list = list()
    direction = 1
    if step < 0:
        step = -step
        direction = -1

    counter = i + step
    while len(word_list) < 5:
        ind = direction * (counter if counter < len(vocab) else (counter-len(vocab))%len(vocab))
        if pos in vocab_dict[vocab[ind]]:
            if direction > 0:
                word_list.append(vocab[ind])
            else:
                word_list.insert(0,vocab[ind])
            counter += step
        else:
            counter += 1
    return word_list

def find_form(lem, pos):
    w = regex.sub(r'[[:punct:]]+$', '', lem)
    p = regex.sub(r'^[[:alnum:]]+', '', lem)
    if pos[:2] == 'VB' and lemma(w) in { 'be', 'have' }:
        return lem
    elif pos in { 'VB', 'NN', 'NNP', 'JJ', 'RB' }:
        return lem
    elif pos == 'VBZ':
        return conjugate(w, "3sg") + p
    elif pos == 'VBP':
        return conjugate(w, "1sg") + p
    elif pos == 'VBD':
        return conjugate(w, "p") + p
    elif pos == 'VBN':
        return conjugate(w, "ppart") + p
    elif pos == 'VBG':
        return conjugate(w, "part") + p
    elif pos in { 'NNS', 'NNPS' }:
        return pluralize(w) + p
    elif pos in { 'JJR', 'RBR' }:
        if w[-2:] == 'er':
            return lem
        else:
            return comparative(w) + p
    elif pos in { 'JJS', 'RBS' }:
        if w[-2:] == 'st':
            return lem
        else:
            return superlative(w) + p
    else:
        return lem

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
