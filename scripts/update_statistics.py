#!/usr/bin/env python3

import sys, os, json, urllib.request, urllib.parse, sqlite3, dateutil.parser
import register_channels

DB_PATH = os.path.join(os.path.dirname(__file__), '../', 'db.sqlite3')
API_KEY = os.environ['YOUTUBE_API_KEY']
API_ENDPOINT = 'https://www.googleapis.com/youtube/v3/channels?'


def get_channels(cursor):
    cursor.execute('''
        SELECT * FROM channels;
    ''')
    channels = cursor.fetchall()
    return channels


def retrive_statistics(channel_id):
    params = {
        'id': channel_id,
        'key': API_KEY,
        'part': 'statistics'
    }
    url = API_ENDPOINT + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as response:
        response_header = response.info()
        response_body = response.read().decode('utf-8')
        response_data = json.loads(response_body)
        statistics = response_data['items'][0]['statistics']
        data = [
            channel_id,
            dateutil.parser.parse(response_header['Date']),
            statistics['subscriberCount'],
            statistics['videoCount'],
            statistics['viewCount']
        ]
        return data


def main():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        PRAGMA foreign_keys = ON;
    ''')

    channels = get_channels(cursor)
    for channel in channels:
        channel_id = channel[0]

        # Update channel information
        snippet = register_channels.get_snippet(channel_id)
        information = [
            snippet['title'],
            snippet['description'],
            channel_id
        ]
        cursor.execute('''
            UPDATE channels SET title = ?, description = ? WHERE id = ?;
        ''', information)

        # Update statistics
        statistics = retrive_statistics(channel_id)
        cursor.execute('''
            INSERT INTO statistics (channel_id, added_at, subscriber_count, video_count, view_count) VALUES (?, ?, ?, ?, ?);
        ''', statistics)

    connection.commit()
    connection.close()


if __name__ == '__main__':
    main()
