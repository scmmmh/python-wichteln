import argparse
import collections
import configparser
import getpass
import itertools
import random
import smtplib

parser = argparse.ArgumentParser(description='Wichteln für Pythonistas')
parser.add_argument('smtp_host')
parser.add_argument('smtp_user')
parser.add_argument('wichtel', nargs='+')
args = parser.parse_args()

settings = {}
for configfile in args.wichtel:
    parser = configparser.ConfigParser()
    parser.read(configfile)
    settings[parser.get('general', 'contact')] = {'email': parser.get('general', 'email'),
                                                  'people': {},
                                                  'noassignment': parser.get('general', 'noassignment', fallback=False),
                                                  'assigned': []}
    for person, details in parser.items('people'):
        settings[parser.get('general', 'contact')]['people'][person.capitalize()] = details

contacts = list(settings.keys())
people = [p for c in settings.values() for p in c['people'].items()]
assignments = []

while True:
    assignments = []
    random.shuffle(people)
    for person, details in people:
        contact = random.choice(contacts)
        while person in settings[contact]['people'] or settings[contact]['noassignment']:
            contact = random.choice(contacts)
        assignments.append((contact, person, details))
    counts = collections.Counter([t for t, _, _ in assignments])
    if abs(max(counts.values()) - min(counts.values())) <= 1:
        break

for contact, person, details in assignments:
    settings[contact]['assigned'].append((person, details))

if ':' in args.smtp_host:
    host, port = args.smtp_host.split(':')
else:
    host = args.smtp_host
    port = 25
smtp = smtplib.SMTP(host=host, port=port)
smtp.starttls()
smtp.login(args.smtp_user, getpass.getpass('SMTP Password:'))

for key, value in settings.items():
    if value['assigned']:
        msg = '''From: Weihnachtsmann <weihnachtsmann-noreply@mail.room3b.eu>
To: %s <%s>
Subject: Wichteln
Content-Type: text/text; charset=utf-8

Lieber %s,

Du wichtelst heuer für:

%s

Liebe Grüße,
Der Weihnachtsmann''' % (key,
                         value['email'],
                         key,
                         '\n'.join(['%s: %s' % a for a in value['assigned']]))
        smtp.sendmail('weihnachtsmann-noreply@mail.room3b.eu',
                      value['email'],
                      msg.encode('utf-8'))
