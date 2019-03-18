# ベースイメージ
FROM python

RUN mkdir /var/www
# workdirの指定
WORKDIR /var/www

# 依存Pythonライブラリ一覧コピー
COPY requirements.txt ./
COPY uwsgi.ini ./

# 依存Pythonライブラリインストール
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /var/www/src

COPY ./src /var/www/src

CMD ["uwsgi","--ini","/var/www/uwsgi.ini"]
