#!/usr/bin/env python3
"""
Copyright (c) 2021 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from flask import Flask, request, session, render_template
#import spacy
from pattern.en import pluralize, conjugate, lemma, lexeme, parse, tag
import json
import regex
#import mlconjug3
import sys
import nltk

app = Flask(__name__)
application = app
if __name__ == "__main__":
    app.run()

# Set the secret key to some random bytes. Keep this really secret!
#nlp = spacy.load('en_core_web_sm')
#vocab_file = 'splus7/vocab02.json'
#mlc = mlconjug3.Conjugator(language='en')

#with open(vocab_file) as json_file:
#    vocab_dict = json.load(json_file)
#vocab = list(vocab_dict.keys())
vocab = nltk.corpus.words.words()
#vocab.sort()

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
select_treebank = {'VB', 'VBZ', 'VBP', 'VBD', 'VBN', 'VBG', 'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'}

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

    for sent in parse(text, chunks=False, lemmata=True).split():
        for token in sent:
# output:
#[[['The', 'DT', 'the'], ['children', 'NNS', 'child'], ['cried', 'VBD', 'cry'], ['.', '.', '.']]]
#    for token in nlp(text):
#        parsed.append(token.text)
            parsed.append(token[0])
#        word_list = [token.lemma_] * 11
            word_list = [token[2]] * 11
#        pos = token.pos_
#        string = token.lemma_
#            if token.pos_ in {'PUNCT', 'SYM'} and len(word_array) > 0:
            if token[1] in {'.', ',', ':', '(', ')' 'SYM'} and len(word_array) > 0:
            # Penn Treebank II tag set
                for i in range(11):
#                    word_array[-1][1][i] += token.text
                    word_array[-1][1][i] += token[0]
#                parsed.remove(token.text)
                parsed.remove(token[0])
                continue
#            elif token.pos_ in {'VERB', 'NOUN', 'ADJ', 'ADV', 'PROPN'} and token.lemma_.lower() in vocab:
            elif token[1] in select_treebank and token[2] in vocab:
#                if token.pos_ == 'VERB':
#                    pos = token.tag_
#                elif token.pos_ == 'PROPN':
#                    pos = 'NOUN'
#                    string = token.lemma_.lower()
#                word_list = get_ten_around(vocab.index(string), pos, step)
                word_list = get_ten_around(vocab.index(token[2]), token[1], step)
            word_array.append([pos, word_list])

    session['parsed'] = parsed
    session.modified = True
    return word_array

#def get_ten_around(i, pos, step):
#    pos_map = {'VERB': 'Verb', 'NOUN': 'Noun', 'ADJ': 'Adjective', 'ADV': 'Adverb'}
#
#    def get_five(i, pos, step):
#        word_list = list()
#        while len(word_list) < 5:
#            i += step
#            ind = i % len(vocab)
##            ind = i if i < len(vocab) else i - len(vocab)
#            if pos in vocab_dict[vocab[ind]]:
#                if step > 0:
#                    word_list.append(vocab[ind])
#                else:
#                    word_list.insert(0,vocab[ind])
#        return word_list
#
#    if pos[:2] == 'VB':
#        pos = 'VERB'
#    return get_five(i, pos_map[pos], -step) + [vocab[i]] + get_five(i, pos_map[pos], step)

def get_ten_around(i, pos, step):
    return get_five(i, pos, -step) + [vocab[i]] + get_five(i, pos, step)

def check_capitalization(a):
    orig = session['parsed']
    p = regex.compile(r"^[[:upper:]]+")
    for j in range(len(a)): # len(a) = number of words in version
        for i in range(11): # there are 11 versions
            if p.match(orig[j]):
                a[j][1][i] = a[j][1][i].capitalize()
    return a

def get_five(i, pos, step):
    initial_lemma = vocab[i]
    word_list = list()
    direction = 1
    if step < 0:
        step = -step
        direction = -1

    counter = step
    while len(word_list) < 5:
        ind = direction * (counter if counter < len(vocab) else len(vocab)-counter)
#            ind = i if i < len(vocab) else i - len(vocab)
#            if pos in vocab_dict[vocab[ind]:
        if inflects(vocab[ind], pos):
            if direction > 0:
                word_list.append(vocab[ind])
            else:
                word_list.insert(0,vocab[ind])
            counter += step * direction
        else:
            counter += direction
    return word_list

def inflects(lemma, pos):
    if pos == 'VB':
    elif pos == 'VBZ':
    elif pos == 'VBP':
    elif pos == 'VBD':
    elif pos == 'VBN':
    elif pos == 'VBG':
    elif pos == 'NN':
    elif pos == 'NNS':
    elif pos == 'NNP':
    elif pos == 'NNPS':
    elif pos == 'JJ':
    elif pos == 'JJR':
    elif pos == 'JJS':
    elif pos == 'RB':
    elif pos == 'RBR':
    elif pos == 'RBS':
    else:

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
