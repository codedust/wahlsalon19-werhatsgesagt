from flask import Flask, current_app, jsonify
from nltk import tokenize
from random import randint
import os.path
app = Flask(__name__)

# read election programs
election_programs = {
    'dielinke': {
        'program_name': 'Wahlprogramm der Partei DIE LINKE zur Europawahl 2019',
        'url': 'https://www.die-linke.de/europawahl/wahlprogramm/'
    },
    'gruene': {
        'program_name': 'Wahlprogramm der Partei BÜNDNIS 90/DIE GRÜNEN zur Europawahl 2019',
        'url': 'https://www.gruene.de/artikel/gruenes-wahlprogramm-zur-europawahl-2019'
    },
    'spd': {
        'program_name': 'Wahlprogramm der SPD zur Europawahl 2019',
        'url': 'https://www.spd.de/europa-ist-die-antwort/unsere-ziele/unser-europaprogramm/',
    },
    'cdu': {
        'program_name': 'Wahlprogramm der CDU zur Europawahl 2019',
        'url': 'https://www.cdu.de/europaprogramm',
    },
    'fdp': {
        'program_name': 'Wahlprogramm der FDP zur Europawahl 2019',
        'url': 'https://www.fdp.de/content/auf-dem-weg-zum-europawahlprogramm-2019',
    },
    'afd': {
        'program_name': 'Wahlprogramm der AfD zur Europawahl 2019',
        'url': 'https://www.afd.de/europawahlprogramm/'
    }
}

programs = {}
for party in list(election_programs.keys()):
    path = 'wahlprogramme/eu_' + party + '.md'
    if not os.path.isfile(path):
        print('No program for party ' + party + '!')
        continue
    with open(path) as f:
        content = f.readlines()
    programs[party] = list(filter(lambda line: line != '', [x.strip().replace('\*', '*') for x in content]))

print('Found ' + str(len(programs)) + ' programs: ' + ', '.join(list(programs.keys())))


def find_headline_line_number(party, line_number):
    while line_number > 0:
        line_number -= 1
        if programs[party][line_number][:1] == '#':
          return line_number
    return None

def find_next_headline_line_number(party, line_number):
    while line_number < len(programs[party]) - 1:
        line_number += 1
        if programs[party][line_number][:1] == '#':
            return line_number
    return line_number

def headline_from_line_number(party, line_number):
    headline_line_number = find_headline_line_number(party, line_number)
    if headline_line_number == None or headline_line_number < 0 or headline_line_number > len(programs[party]):
        return ""
    return programs[party][headline_line_number].lstrip('#').strip()

def find_paragraph(party, line_number):
    headline_line_number = find_headline_line_number(party, line_number)
    next_headline_line_number = find_next_headline_line_number(party, line_number)
    return '<p>' + '</p><p>'.join(programs[party][headline_line_number+1:next_headline_line_number]) + '</p>'


@app.route('/')
def index():
    return current_app.send_static_file('index.html')

@app.route('/api/question')
def api_question():
    party = list(programs.keys())[randint(0, len(programs) - 1)]
    sentence = '#'
    while sentence == '#':
        line = '#'
        while line[0] == '#':
            line_number = randint(0, len(programs[party]) - 1)
            line = programs[party][line_number]

        headline = headline_from_line_number(party, line_number)
        paragraph = find_paragraph(party, line_number)

        sentences = tokenize.sent_tokenize(line, language='german')
        sentence = sentences[randint(0, len(sentences) - 1)]
        if sentence[-1] in [':', ',']:
            sentence = '#'
        if sentence[0:2] == '- ':
            sentence = sentence[2:]
        if sentence[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            sentence = '#'

        sentence = sentence.replace('AfD', '[Partei]')
        sentence = sentence.replace('Alternative für Deutschland', '[Partei]')
        sentence = sentence.replace('CDU', '[Partei]')
        sentence = sentence.replace('DIE LINKE', '[Partei]')
        sentence = sentence.replace('Wir Freie Demokraten', 'Wir')
        sentence = sentence.replace('BÜNDNIS 90/DIE GRÜNEN', '[Partei]')
        sentence = sentence.replace('Wir GRÜNEN', 'Wir')
        sentence = sentence.replace('GRÜNEN', '[Partei]')
        sentence = sentence.replace('SPD', '[Partei]')

    return jsonify({
        'short': sentence,
        'long': paragraph,
        'headline': headline,
        'party': party,
        'programName': election_programs[party]['program_name'],
        'url': election_programs[party]['url'],
    })

@app.route('/api/program/<party>')
def api_program(party):
    return jsonify(programs[party])
