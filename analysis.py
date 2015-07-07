#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

import argparse
import mailbox
import re
import sys

import dateutil.parser

row_pattern = re.compile(r'<td>([^<]+)</td>')



def get_patterns():
    phrases = [
        r'WLAN-Gerät am Gastzugang wird (?P<action>abgemeldet): WLAN-Gerät antwortet nicht\. MAC-Adresse: (?P<mac>[0-9A-F:]+), Name: (?P<name>.+)\. \(#0302\)\.',
        r'WLAN-Gerät am Gastzugang wird (?P<action>abgemeldet): WLAN-Gerät antwortet nicht\. MAC-Adresse: (?P<mac>[0-9A-F:]+)\. \(#0302\)\.',
        r'WLAN-Gerät erstmalig über Gastzugang (?P<action>angemeldet)\. Geschwindigkeit (?P<mbits>\d+) Mbit/s\. MAC-Adresse: (?P<mac>[0-9A-F:]+), Name: (?P<name>.+)\.',
        r'WLAN-Gerät erstmalig über Gastzugang (?P<action>angemeldet)\. Geschwindigkeit (?P<mbits>\d+) Mbit/s\. MAC-Adresse: (?P<mac>[0-9A-F:]+)\.',
        r'WLAN-Gerät hat sich am Gastzugang neu (?P<action>angemeldet)\. Geschwindigkeit (?P<mbits>\d+) Mbit/s\. MAC-Adresse: (?P<mac>[0-9A-F:]+), Name: (?P<name>.+)\.',
        r'WLAN-Gerät hat sich am Gastzugang neu (?P<action>angemeldet)\. Geschwindigkeit (?P<mbits>\d+) Mbit/s\. MAC-Adresse: (?P<mac>[0-9A-F:]+)\.',
        r'WLAN-Gerät hat sich vom Gastzugang (?P<action>abgemeldet)\. MAC-Adresse: (?P<mac>[0-9A-F:]+), Name: (?P<name>.+)\.',
        r'WLAN-Gerät hat sich vom Gastzugang (?P<action>abgemeldet)\. MAC-Adresse: (?P<mac>[0-9A-F:]+)\.',
        r'WLAN-Gerät über Gastzugang (?P<action>angemeldet)\. Geschwindigkeit (?P<mbits>\d+) Mbit/s\. MAC-Adresse: (?P<mac>[0-9A-F:]+), Name: (?P<name>.+)\.',
        r'WLAN-Gerät über Gastzugang (?P<action>angemeldet)\. Geschwindigkeit (?P<mbits>\d+) Mbit/s\. MAC-Adresse: (?P<mac>[0-9A-F:]+)\.',
    ]

    patterns = [re.compile(phrase) for phrase in phrases]
    return patterns

def get_all_pairs(mbox_filename):
    box = mailbox.mbox(mbox_filename)

    pairs = []

    for message in box:
        text = message.get_payload(decode=True).decode()
        text = text.replace('\n', '')
        text = text.replace('\r', '')

        elements = row_pattern.findall(text)

        dates = [dateutil.parser.parse(item, dayfirst=True) for item in elements[::2]]
        events = elements[1::2]

        pairs += zip(dates, events)

    unique = list(set(pairs))
    unique.sort()

    return unique

def main():
    options = _parse_args()
    patterns = get_patterns()
    pairs = get_all_pairs(options.mbox)

    for date, event in pairs:
        matched = False

        for pattern in patterns:
            match = pattern.match(event)

            if match:
                print(match.groupdict())
                matched = True
                break


        if not matched:
            print('Could not match:', event)
            sys.exit(1)

def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbox')
    options = parser.parse_args()

    return options

if __name__ == '__main__':
    main()
