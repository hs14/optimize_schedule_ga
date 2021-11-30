FROM python:3.10

# ライブラリのインストール
ADD ./requirements.txt /var/piplib/requirements.txt
RUN pip install -r /var/piplib/requirements.txt
