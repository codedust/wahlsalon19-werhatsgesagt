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
    with open(path, 'r+', encoding="utf-8") as f:
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

@app.route('/api/quote')
def api_quote():
    return get_quote()

@app.route('/api/quote/<party>/<line_number>/<sentence_number>')
def api_quote_by_param(party, line_number, sentence_number):
    return get_quote(party, int(line_number), int(sentence_number))

def json_error(reason):
    return jsonify({
        'short': reason,
        'short_not_redacted': '',
        'long': '',
        'headline': '',
        'party': '',
        'line_number': '',
        'sentence_number' : '',
        'programName': '',
        'url': '',
    })

def get_quote(party=None, line_number=None, sentence_number=None):
    if party is None:
        party = list(programs.keys())[randint(0, len(programs) - 1)]
    elif party not in list(programs.keys()):
        return json_error("Keine gültige Partei")

    while True:
        if line_number is None:
            sentence_number = None # might be the case in any but the first iteration of the while loop
            line = '#'
            while line[0] == '#':
                line_number = randint(0, len(programs[party]) - 1)
                line = programs[party][line_number]
        elif line_number < 0 or line_number >= len(programs[party]):
            return json_error("Ungültige Zeile")

        line = programs[party][line_number]
        headline = headline_from_line_number(party, line_number)
        paragraph = find_paragraph(party, line_number)
        sentences = tokenize.sent_tokenize(line, language='german')

        if sentence_number is None:
            sentence_number = randint(0, len(sentences) - 1)
        elif sentence_number < 0 or sentence_number >= len(sentences):
            return json_error("Ungültiger Satz")

        quote = sentences[sentence_number]

        if quote[-1] in [':', ',']:
            line_number == None
            continue
        if quote[0:2] == '- ':
            line_number == None
            continue
        if quote[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            line_number == None
            continue

        quote_redacted = quote
        quote_redacted = quote_redacted.replace('AfD', '[Partei]')
        quote_redacted = quote_redacted.replace('Alternative für Deutschland', '[Partei]')
        quote_redacted = quote_redacted.replace('CDU', '[Partei]')
        quote_redacted = quote_redacted.replace('DIE LINKE', '[Partei]')
        quote_redacted = quote_redacted.replace('Wir Freie Demokraten', 'Wir')
        quote_redacted = quote_redacted.replace('BÜNDNIS 90/DIE GRÜNEN', '[Partei]')
        quote_redacted = quote_redacted.replace('Wir GRÜNEN', 'Wir')
        quote_redacted = quote_redacted.replace('GRÜNEN', '[Partei]')
        quote_redacted = quote_redacted.replace('SPD', '[Partei]')

        return jsonify({
            'short': quote_redacted,
            'short_not_redacted': quote,
            'long': paragraph,
            'headline': headline,
            'party': party,
            'line_number': line_number,
            'sentence_number' : sentence_number,
            'programName': election_programs[party]['program_name'],
            'url': election_programs[party]['url'],
        })

@app.route('/api/program/<party>')
def api_program(party):
    return jsonify(programs[party])
