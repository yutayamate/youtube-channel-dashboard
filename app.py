#!/usr/bin/env python3

import sys, os, json, datetime, pytz, urllib, flask, sqlite3, dateutil.parser
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

app = flask.Flask(__name__)


@app.before_request
def before_request():
    flask.g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(flask, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def route_index():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT COUNT(id) FROM view_channels_latest;
    ''')
    count = cursor.fetchone()[0]
    cursor.execute('''
        SELECT * FROM view_channels_latest ORDER BY subscriber_count DESC LIMIT 10;
    ''')
    data = cursor.fetchall()
    updated_at = utc_to_jst(data[0][5]).strftime('%Y/%m/%d %H:%M:%S')
    return flask.render_template(
        'index.html',
        title='Home',
        count=count,
        data=data,
        updated_at=updated_at
    )


@app.route('/list/')
def route_list():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM view_channels_latest ORDER BY title;
    ''')
    channels = cursor.fetchall()
    return flask.render_template(
        'list.html',
        title='チャンネル一覧',
        channels=channels
    )


@app.route('/channel/<channel_id>')
def route_channel(channel_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * FROM view_channels_latest WHERE id = ?;
    ''', (channel_id,))
    channel = cursor.fetchone()
    channel = list(channel)
    channel[4] = utc_to_jst(channel[4]).strftime('%Y/%m/%d %H:%M:%S')
    print(channel)

    cursor.execute('''
        SELECT * FROM statistics WHERE channel_id = ?;
    ''', (channel_id,))
    statistics = cursor.fetchall()

    labels = list(map(lambda x: utc_to_jst(x[1]).strftime('%Y/%m/%d'), statistics))
    data = [
        [
            'チャンネル登録',
            list(map(lambda x: x[2], statistics)),
            labels
        ],
        [
            'チャンネル登録 増加数',
            np.diff(list(map(lambda x: x[2], statistics))).tolist(),
            labels[1:]
        ],
        [
            '視聴回数',
            list(map(lambda x: x[4], statistics)),
            labels
        ],
        [
            '視聴回数 増加数',
            np.diff(list(map(lambda x: x[4], statistics))).tolist(),
            labels[1:]
        ],
        [
            '動画本数',
            list(map(lambda x: x[3], statistics)),
            labels
        ]
    ]

    return flask.render_template(
        'channel.html',
        title=channel[1],
        channel=channel,
        data=data
    )


def connect_db():
    connection =  sqlite3.connect(DB_PATH)
    return connection


def utc_to_jst(utc_str):
    date = dateutil.parser.parse(utc_str)
    timezone = pytz.timezone('Asia/Tokyo')
    return date.astimezone(timezone)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
