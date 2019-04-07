from flask import Flask, current_app, jsonify
from nltk import tokenize
from random import randint
import os.path
app = Flask(__name__)

# read manifestos
manifestos = {}
for party in ['dielinke', 'diegruenen', 'spd', 'cdu', 'fdp', 'afd']:
    path = 'wahlprogramme/eu_' + party + '.md'
    if not os.path.isfile(path):
        print('No manifesto for party ' + party + '!')
        continue
    with open(path) as f:
        content = f.readlines()
    manifestos[party] = list(filter(lambda line: line != '', [x.strip() for x in content]))

print('Found ' + str(len(manifestos)) + ' manifestos.')
print(list(manifestos.keys()))


@app.route('/')
def index():
    return current_app.send_static_file('index.html')

@app.route('/api/question')
def question():
    party = list(manifestos.keys())[randint(0, len(manifestos) - 1)]
    sentence = '#'
    while sentence == '#':
        line = '#'
        while line[0] == '#':
            line_number = randint(0, len(manifestos[party]) - 1)
            line = manifestos[party][line_number]
        paragraph = line
        sentences = tokenize.sent_tokenize(line, language='german')
        sentence = sentences[randint(0, len(sentences) - 1)]
        if sentence[-1] in [':', ',']:
            sentence = '#'
        if sentence[0:2] == '- ':
            sentence = sentence[2:]
        headline = ''
        while(line_number > 0 and (len(headline) == 0 or headline[0] != '#')):
            print(headline)
            line_number -= 1
            headline = manifestos[party][line_number]
        while headline[0] == '#':
            headline = headline[1:]
        headline = headline[1:]

    return jsonify({
        'short': sentence,
        'long': paragraph,
        'headline': headline,
        'party': party
    })

@app.route('/api/manifesto/<party>')
def manifesto(party):
    return jsonify(manifestos[party])
