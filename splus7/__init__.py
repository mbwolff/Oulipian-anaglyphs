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

app = Flask(__name__)
application = app
if __name__ == "__main__":
    app.run()

# Set the secret key to some random bytes. Keep this really secret!
nlp = spacy.load('en_core_web_sm')
vocab_file = 'splus7/vocab02.json'
mlc = mlconjug3.Conjugator(language='en')

with open(vocab_file) as json_file:
    vocab_dict = json.load(json_file)
vocab = list(vocab_dict.keys())
vocab.sort()

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
    words = list()
    if 'words' in session:
        words = mod_word(session['words'], int(request.args.get('w')), int(request.args.get('d')))
    elif 'text' in request.form:
        session['text'] = request.form['text']
        session['step'] = request.form['step']
        words = parse(request.form['text'], int(request.form['step']))
    else:
        return render_template('error.html')

    session['words'] = words
    session.modified = True
    displayed = check_capitalization(words)
    return render_template('display.html', displayed=displayed)

def mod_word(words, i, d):
    step = int(session['step'])
    w = regex.sub(r'[[:punct:]]+$', '', words[i][1][d])
    p = regex.sub(r'^[[:alnum:]]+', '', words[i][1][d])
    eprint(w, p, words[i][1][d])
    if w.lower() in vocab:
        words[i][1] = get_ten_around(vocab.index(w.lower()), words[i][0], step)
        for j in range(len(words[i][1])):
            words[i][1][j] += p
    else:
        eprint('Word not in vocab: ', w)
    return words

def parse(text, step):
    word_array = list()
    parsed = list()

    for token in nlp(text):
        parsed.append(token.text)
        word_list = [token.lemma_] * 11
        pos = token.pos_
        string = token.lemma_
        if token.pos_ in {'PUNCT', 'SYM'} and len(word_array) > 0:
            for i in range(11):
                word_array[-1][1][i] += token.text
            parsed.remove(token.text)
            continue
        elif token.pos_ in {'VERB', 'NOUN', 'ADJ', 'ADV', 'PROPN'} and token.lemma_.lower() in vocab:
            if token.pos_ == 'VERB':
                pos = token.tag_
            elif token.pos_ == 'PROPN':
                pos = 'NOUN'
                string = token.lemma_.lower()
            word_list = get_ten_around(vocab.index(string), pos, step)
        word_array.append([pos, word_list])

    session['parsed'] = parsed
    session.modified = True
    return word_array

#def find_words(token, pos):
#    word_list = list()
#    if token in vocab:
#        word_list = get_ten_around(vocab.index(token), pos)
#    return word_list

def get_ten_around(i, pos, step):
    pos_map = {'VERB': 'Verb', 'NOUN': 'Noun', 'ADJ': 'Adjective', 'ADV': 'Adverb'}

    def get_five(i, pos, step):
        word_list = list()
        while len(word_list) < 5:
            i += step
            ind = i % len(vocab)
#            ind = i if i < len(vocab) else i - len(vocab)
            if pos in vocab_dict[vocab[ind]]:
                if step > 0:
                    word_list.append(vocab[ind])
                else:
                    word_list.insert(0,vocab[ind])
        return word_list

    if pos[:2] == 'VB':
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

def inflect(wa):
    display = list()
    for i in range(len(wa)):
        if wa[i][0][0] == 'V':
            for j in range(len(wa[i][1])):
                w = regex.sub(r'[[:punct:]]+$', '', wa[i][1][j])
                p = regex.sub(r'^[[:alnum:]]+', '', wa[i][1][j])
                wa[i][1][j] = conjugate(w, wa[i][0]) + p
        display.append(wa[i])

    return display

def conjugate(base, t):
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
#    eprint(base, t, c)
    return c

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
