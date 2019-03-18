#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from requests_oauthlib import OAuth1Session
import requests
from urllib.parse import parse_qsl
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.secret_key = os.environ['FLASK_SESSION_SECRET']
callback_url = os.environ['CALLBACK_URL']
consumer_key = os.environ['TW_CONSUMER_KEY']
consumer_secret = os.environ['TW_CONSUMER_KEY_SECRET']

base_url = 'https://api.twitter.com/'

request_token_url = base_url + 'oauth/request_token'
authenticate_url = base_url + 'oauth/authenticate'
access_token_url = base_url + 'oauth/access_token'

base_json_url = 'https://api.twitter.com/1.1/%s.json'
user_timeline_url = base_json_url % ('statuses/home_timeline')
search_url = base_json_url % ('search/tweets')
post_url = base_json_url % ('statuses/update')

# 以下View部
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'oauth_token_secret' in session:
            # tokenとtoken_secretは使い回す
            response = get_tagged_tweets(
                oauth_token = session.get('oauth_token'),
                oauth_token_secret = session.get('oauth_token_secret'),
                tags = session.get('tags')
            )
            return render_template('index.html', msgs=response['statuses'], tags=' '.join(session.get('tags')))
        if request.args.get('oauth_token'):
            # redirect_urlで返ってきたら認証とデータ取得を行う
            oauth_token = request.args.get('oauth_token')
            oauth_verifier = request.args.get('oauth_verifier')
            session['oauth_verifier'] = oauth_verifier
            response = get_twitter_access_token(
                oauth_token = oauth_token,
                oauth_verifier = oauth_verifier
            )
            session['oauth_token'] = response['oauth_token']
            session['oauth_token_secret'] = response['oauth_token_secret']
            response = get_tagged_tweets(
                oauth_token = session.get('oauth_token'),
                oauth_token_secret = session.get('oauth_token_secret'),
                tags = session.get('tags')
            )
            return render_template('index.html', msgs=response['statuses'], tags=' '.join(session.get('tags')))
        else:
            # ログイン画面
            return render_template('login.html')
    else:
        if 'oauth_token_secret' in session:
            # postとリロード
            msg = request.form['msg']
            tags = request.form['tags']
            session['tags'] = tags.split()
            if not msg:
                return redirect('/')
            else:
                params = {
                    'oauth_token': session['oauth_token'],
                    'oauth_token_secret': session['oauth_token_secret'],
                    'status': msg + ' ' + tags,
                    'lang': 'ja'
                }
                response = post_tweet(params)
                return redirect('/')
        else:
            # ログイン、というかtwitter連携処理
            response = get_twitter_request_token(
                oauth_callback = callback_url
            )
            session['oauth_token'] = response['oauth_token']
            session['tags'] = request.form['tags'].split()
            return redirect(response['authenticate_endpoint'])

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('tags', None)
    session.pop('oauth_token', None)
    session.pop('oauth_verifier', None)
    session.pop('oauth_token_secret', None)
    return redirect('/')

# 以下API部。分けてもいいけど小規模だし。。。
def get_twitter_request_token(oauth_callback):
    twitter = OAuth1Session(consumer_key, consumer_secret)

    response = twitter.post(
        request_token_url,
        params={'oauth_callback': oauth_callback}
    )

    # responseからリクエストトークンを取り出す
    request_token = dict(parse_qsl(response.content.decode("utf-8")))

    # リクエストトークンから連携画面のURLを生成
    authenticate_endpoint = '%s?oauth_token=%s' \
        % (authenticate_url, request_token['oauth_token'])
    request_token.update({'authenticate_endpoint': authenticate_endpoint})

    return request_token

def get_twitter_access_token(oauth_token, oauth_verifier):
    twitter = OAuth1Session(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_verifier
    )

    response = twitter.post(
        access_token_url,
        params={'oauth_verifier': oauth_verifier}
    )

    access_token = dict(parse_qsl(response.content.decode("utf-8")))
    return access_token

def get_tagged_tweets(oauth_token, oauth_token_secret, tags):
    params = {
        'q': tags
    }

    twitter = OAuth1Session(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret,
    )

    response = twitter.get(search_url, params=params)
    results = json.loads(response.text)

    return results

def get_twitter_home_timeline(oauth_token, oauth_token_secret):
    params = {
        'exclude_replies': True,
        'include_rts': False,
        'count': 20,
        'trim_user': False,
        'tweet_mode': 'extended',    # full_textを取得するために必要
    }

    twitter = OAuth1Session(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret,
    )

    response = twitter.get(user_timeline_url, params=params)
    results = json.loads(response.text)

    return results

def post_tweet(post_body):
    oauth_token = post_body['oauth_token']
    oauth_token_secret = post_body['oauth_token_secret']
    params = {
        'status': post_body['status']
    }
    twitter = OAuth1Session(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret,
    )

    response = twitter.post(post_url, params=params)
    results = json.loads(response.text)

    return results

if __name__ == '__main__':
    app.debug = True
    app.run(port = 3031)