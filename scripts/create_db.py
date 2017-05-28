#!/usr/bin/env python3

import sys, os, sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '../', 'db.sqlite3')

def main():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        PRAGMA foreign_keys = ON
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id TEXT,
            title TEXT,
            description TEXT,
            thumbnail_url TEXT,
            published_at DATETIME,
            PRIMARY KEY (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            channel_id TEXT,
            added_at DATETIME,
            subscriber_count INTEGER,
            video_count INTEGER,
            view_count INTEGER,
            PRIMARY KEY (channel_id, added_at),
            FOREIGN KEY (channel_id) REFERENCES channels (id)
        )
    ''')
    connection.commit()
    connection.close()


if __name__ == '__main__':
    main()
