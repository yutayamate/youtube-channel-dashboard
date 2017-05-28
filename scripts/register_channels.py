#!/usr/bin/env python3

import sys, os, json, urllib.request, urllib.parse, sqlite3, dateutil.parser
import xml.etree.ElementTree as et

DB_PATH = os.path.join(os.path.dirname(__file__), '../', 'db.sqlite3')
API_KEY = os.environ['YOUTUBE_API_KEY']
API_ENDPOINT = 'https://www.googleapis.com/youtube/v3/channels?'

def main():
    if len(sys.argv) != 2:
        sys.stderr.write('Error: Input XML file is not specified\n')
        sys.exit(1)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    tree = et.parse(sys.argv[1])
    root = tree.getroot()
    for element in root.findall('./body/outline/outline'):
        qs = urllib.parse.urlparse(element.attrib['xmlUrl']).query
        channel_id = urllib.parse.parse_qs(qs)['channel_id'][0]
        snippet = get_snippet(channel_id)
        data = [
            channel_id,
            snippet['title'],
            snippet['description'],
            snippet['thumbnails']['high']['url'],
            dateutil.parser.parse(snippet['publishedAt'])
        ]
        # Register channels
        cursor.execute('''
            INSERT OR IGNORE INTO channels (id, title, description, thumbnail_url, published_at) VALUES (?, ?, ?, ?, ?)
        ''', data)

    connection.commit()
    connection.close()


def get_snippet(channel_id):
    params = {
        'id': channel_id,
        'key': API_KEY,
        'part': 'snippet'
    }
    url = API_ENDPOINT + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as response:
        response_body = response.read().decode('utf-8')
        response_data = json.loads(response_body)
        snippet = response_data['items'][0]['snippet']
        return snippet


if __name__ == '__main__':
    main()
