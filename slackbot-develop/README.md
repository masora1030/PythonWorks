https://github.com/lins05/slackbot/ のslack-bot開発用のワークフレームをベースラインに用いて作成した、Google Callendarを参照してくれる[Slack](https://slack.com)のおじさん風味なチャットボットです。


## 機能

* slack [Real Time Messaging API](https://api.slack.com/rtm) に基づいています
* チャンネル内の投稿を自動で同時に処理することができます
* 接続が失われたときに自動的に再接続します
* Python3 をサポートしています


できることは現状以下の通りです。

   【イベントを作成する】
```
日程:2020/10/30/10:30-19:30
内容:SoraTakashimaの誕生日
```
上のようにslackチャンネル内でイベント内容を投稿してください。登録したGoogle Calenderに投稿された内容の予定を書き込みます。
 
   (時間まで指定してください。区切り文字は、「/ . -」の３ついずれも使えます。)

   (改行後の文章もメッセージ終わりまで「内容」に含まれます。)

   (時間は、例えば「午後5時5分」なら、「17:05」のように表記してください。また、内容は32文字以下までしか受け付けていません。)
   
   
   
   【イベントが入っているか確認する】
```
イベント確認:2020/10/30
```
上のようにslackチャンネル内で確認したい日程を投稿してください。
前後二週間のイベント情報を取得できます。



   【自作予定情報を確認する】
```
おじさん確認:2020/10/30
```
上のように確認したい日程を投稿してください。
前後一週間の自作カレンダーに書き込まれた予定を取得できます。



## 使い方

pipコマンドが使えること、Python3 (3.6.8)が入っていること、slackのワークスペースが作成されていること、Google Calendarが有効になっているGoogleアカウントを持っていることが前提条件です。

1. まずは、以下のコマンドでslackbotライブラリをインストールします。

```
pip install slackbot
```

2. 次に、SlackのAPIトークンを取得します。[slack bot](https://my.slack.com/services/new/bot)から、slackの新しいBotを作成します。作ったbotはテスト用のチャンネルに招待しておきます。作成したslackbotのインテグレーションページでAPIトークンを確認し、メモします。


3. Google Calender APIも使えるようにしておきます。[Python Quickstart](https://developers.google.com/calendar/quickstart/python?hl=ja)に用意したGoogleアカウントにログインした状態でアクセスします。そして「ENABLE THE GOOGLE CALENDAR API」というボタンを押し下します。新しく出てきたwindow内の「DOWNLOAD CLIENT CONFIGURATION」というボタンを押して、credentials.jsonというファイルをダウンロードします。(ここで、client IDとclient secretはメモする必要はありません。)

4. Google Client Libraryを以下のコマンドでインストールします。
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

5. [Google Calender](https://calendar.google.com/calendar/)のGUI上で、参照したいカレンダーのカレンダーIDを取得してください。カレンダーの設定から閲覧できます。(このslackbotで書き込みたいカレンダーと確認したいカレンダーが異なる場合は、[Google Calender](https://calendar.google.com/calendar/)のGUI上で予定書き込み用の新しいカレンダーを作成し、そのカレンダーIDも取得してください。)

6. このgithubのディレクトリを適当なワークスペースにcloneしてください。その後、
slackbot-develop/slackbot/settings.py の中の<YOUR BOT token ID>部分を2ステップ目で取得したtokenの文字列に書き換えてください。
   
7. slackbot-develop/plugins/create_schedule.py の中のCalendarId_eventとCalendarId_odisanの値を、それぞれ、5ステップ目で取得したカレンダーIDに置き換えてください。(同じ場合は同じものを入れてください。)
   
8. 3ステップ目で取得したcredentials.jsonというファイルを、slackbot-developディレクトリ直下においてください。

9. コマンドプロンプト上でslackbot-developの中に入り、以下のコマンドを実行してください。するとslackbotが立ち上がり、slack上で機能が使えるようになっています。slackbotが招待されているチャンネルで機能をお試しください。(端末の接続が切れると、プロセスが中断されbotが機能しなくなります。再度使う場合は、もう一度下記コマンドを実行してslackbotを再起動してください。)

```
python run.py
```

* サーバ上にプロジェクトフォルダを移して、このコマンドを永続化することにより、端末側で接続が切れてもslackbotが機能するようになります。永続化にはnohupコマンドが便利です。(バックグラウンド実行)

* 機能を追加したい場合は、slackbot-develop/plugins/create_schedule.py の中でドキュメントの回答を追加したり編集したりすると良いです。



## 参考にしたサイト様

* [Pythonのslackbotライブラリでterraform plan実行してもらう](https://qiita.com/andromeda/items/d68a0c36667cc802987c)

* [【Python】Google Calendar APIを使ってGoogle Calendarの予定を取得・追加する](https://non-dimension.com/python-googlecalendarapi/)
