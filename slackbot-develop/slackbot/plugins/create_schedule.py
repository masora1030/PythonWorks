#coding: UTF-8
import sys
import re
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import datetime
from datetime import date, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# 'credentials.json'はrun.pyと同じ階層に！
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
# カレンダーのIDを入れる。(GUIから取得可能)
CalendarId_event = 'b0o2ekiqe1ejla81a40g2g2h74@group.calendar.google.com' # イベントカレンダー
CalendarId_odisan = 'jtkqqd3lhmoijamsfuvbpqjt9o@group.calendar.google.com' # おじさんカレンダー

# 日付の妥当性を判定
def checkDate(year,month,day):
    from datetime import date
    try:
        newDate=date(year,month,day)
        return True
    except ValueError:
        return False

# 時間の妥当性を判定
def checkTime(start, end):
    hs = int(start[:2])
    he = int(end[:2])
    ss = int(start[3:])
    se = int(end[3:])
    s = int(start[:2]+start[3:])
    e = int(end[:2]+end[3:])
    if (0 <= hs and hs < 24) and (0 <= he and he < 24) and (0 <= ss and ss < 60) and (0 <= se and se < 60) and (s < e):
        return True
    else:
        return False

# タイトル32文字まで
def checkContent(text):
    if len(text) < 33:
        return True
    else:
        return False

# 日付とイベントを抽出
def extraction_event(text):
    year,month,day = [0]*3
    start = ''
    end = ''
    content = ''
    eventRegex = re.compile(r'日程:(\d{4})(\s|-|.)(\d{1,2})(\s|-|.)(\d{1,2})(\s|-|.)([012]\d:[012345]\d)(\s|-|.)([012]\d:[012345]\d)\n内容:(.*)', re.DOTALL)

    for groups in eventRegex.findall(text):
        year,month,day = int(groups[0]), int(groups[2]), int(groups[4])
        start += groups[6]
        end += groups[8]
        content += groups[9]

    if (checkDate(year,month,day)):
        return year,month,day,start,end,content
    else:
        return -1,-1,-1,'','',''

# Google Calenderを確認するAPI。指定された日付周りの予定を調べる。
def see_in_GoogleCalender(year, month, day, CalendarId, Range=1):
    # ある日のGoogle Calender上の予定を吐き出す
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    timefrom = str(year) + '/' + str(month) + '/' + str(day)
    timeto = datetime.datetime.strftime(datetime.datetime.strptime(timefrom, '%Y/%m/%d') + timedelta(days=Range), '%Y/%m/%d')
    if (Range > 1):
        timefrom = datetime.datetime.strftime(datetime.datetime.strptime(timefrom, '%Y/%m/%d') - timedelta(days=Range), '%Y/%m/%d')
    timefrom = datetime.datetime.strptime(timefrom, '%Y/%m/%d').isoformat()+'Z'
    timeto = datetime.datetime.strptime(timeto, '%Y/%m/%d').isoformat()+'Z'
    events_result = service.events().list(calendarId=CalendarId,
                                        timeMin=timefrom,
                                        timeMax=timeto,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

# Google Calenderに予定を入れるAPI
def write_schedule_in_GoogleCalender(year, month, day, start, end, content, CalendarId):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    start = '{}-{}-{}T{}:00'.format(year, month, day, start)
    end = '{}-{}-{}T{}:00'.format(year, month, day, end)

    event = {
      'summary': content,
      'location': 'オヂサンのおうち',
      'description': 'オヂサンと一緒',
      'start': {
        'dateTime': start,
        'timeZone': 'Japan',
      },
      'end': {
        'dateTime': end,
        'timeZone': 'Japan',
      },
    }

    event = service.events().insert(calendarId=CalendarId,
                                    body=event).execute()
    return event['id']




# 予定を入れる
@listen_to(r'日程:(\d{4})(\s|-|.)(\d{1,2})(\s|-|.)(\d{1,2})(\s|-|.)([012]\d:[012345]\d)(\s|-|.)([012]\d:[012345]\d)\n内容:(.*)', re.DOTALL)  #　おじさんイベントの書き込みを探知
def create_schedule_listen(message, aa,bb,cc,dd,ee,ff,ii,jj,kk,ll):    # aa,bb,cc,dd,ee,ff,ii,jj,kk,llは正規表現の都合上出てきてしまう返り値(使わない)
    text = message.body['text']
    eventID = -1
    year,month,day,start,end,content = extraction_event(text)
    if (year != -1) and checkTime(start, end) and checkContent(content): # ちゃんとした日付、時間、内容だった
        events = see_in_GoogleCalender(year, month, day, CalendarId_event) # その日入ってるイベント情報取得
        message.send('あ！これは何らかの予定の情報だね⁉️\nオヂサンも参加していいカナ✋😅⁉️笑')
        if not events:   # ブッキングしてなかった
            eventID = write_schedule_in_GoogleCalender(year, month, day, start, end, content, CalendarId_odisan)    # グーグルカレンダーに登録
            if eventID != -1:
                message.reply("さっき投稿してた予定、Google Calenderに追加しといたヨ😁\nこの日はこの予定しか入ってないみたいだね🤔", in_thread=True)
            else:
                message.reply("アレ⁉️😅\nなんか失敗してしまったみたいダナ😓\nもう一回試してみて(直らなかったら17高島までご連絡ください。)", in_thread=True)
        else:            # ブッキングしてた
            eventID = write_schedule_in_GoogleCalender(year, month, day, start, end, content, CalendarId_odisan)    # グーグルカレンダーに登録
            if eventID != -1:
                message.reply("さっき投稿してた予定、Google Calenderに追加しといたヨ😁\nでもなんだか、この日はイベントたくさんだったから、気をつけてネ😭\n\n以下のイベントが、同じ日に見つかりました。\n", in_thread=True)
                event_summary_list = []
                for event in events:
                    event_summary = '>・' + str(event['summary'])
                    event_summary_list.append(event_summary)
                message.reply('\n'.join(event_summary_list), in_thread=True)
            else:
                message.reply("アレ⁉️😅\n予定入れようとしたらなんか失敗してしまったみたいダナ😓\nもう一回試してみて(治らなかったら17高島までご連絡ください。)", in_thread=True)
    else:
        message.reply('妄言乙w(日程に誤情報が含まれている場合があります。ご確認ください。)', in_thread=True)




# カレンダーを確認する
@listen_to(r'イベント確認:(\d{4})(\s|-|.)(\d{1,2})(\s|-|.)(\d{1,2})', re.DOTALL)  #　イベントの書き込みを探知
def tell_event(message, aa,bb,cc,dd,ee):    # aa,bb,cc,dd,eeは正規表現の都合上出てきてしまう返り値(使わない)
    text = message.body['text']
    year,month,day = [0]*3
    eventRegex = re.compile(r'イベント確認:(\d{4})(\s|-|.)(\d{1,2})(\s|-|.)(\d{1,2})$', re.DOTALL)

    for groups in eventRegex.findall(text):
        year,month,day = int(groups[0]), int(groups[2]), int(groups[4])

    if (checkDate(year,month,day)):
        events = see_in_GoogleCalender(year, month, day, CalendarId_event, Range=14)
        if not events:
            message.reply('その日周りのイベント日程が知りたいのカナ❓❓😳\nよーし笑　オヂサン、頑張っちゃうぞ❗️💪😂\n\n\n'+ 'アラ(^_^;)　何も見つからなかったナ💦\nそしたら、その日は、オヂサン😎と美味しいお寿司🍣なんてどうカナ⁉️\nナンチャッテ😁', in_thread=True)
        else:
            event_summary_list = []
            for event in events:
                time = event['start'].get('dateTime', event['start'].get('date'))
                time = datetime.datetime.strptime(time[:10], '%Y-%m-%d')
                time_str = datetime.datetime.strftime(time, '%Y/%m/%d')
                event_summary = '・' + time_str[5:] + ' : ' + str(event['summary'])
                event_summary_list.append(event_summary)
            message.reply('その日周りのイベント日程が知りたいのカナ❓❓😳\nよーし笑　オヂサン、頑張っちゃうぞ❗️💪😂\n\n\n'+ '指定された日程の前後二週間の間に、以下のイベントが見つかりました。\n' +'\n'.join(event_summary_list), in_thread=True)
    else:
        message.reply('妄言乙w(日程に誤情報が含まれている場合があります。ご確認ください。)', in_thread=True)


@listen_to(r'おじさん確認:(\d{4})(\s|-|.)(\d{1,2})(\s|-|.)(\d{1,2})', re.DOTALL)  #　おじさんの書き込みを探知
def tell_event(message, aa,bb,cc,dd,ee):    # aa,bb,cc,dd,eeは正規表現の都合上出てきてしまう返り値(使わない)
    text = message.body['text']
    year,month,day = [0]*3
    eventRegex = re.compile(r'おじさん確認:(\d{4})(\s|-|.)(\d{1,2})(\s|-|.)(\d{1,2})$', re.DOTALL)

    for groups in eventRegex.findall(text):
        year,month,day = int(groups[0]), int(groups[2]), int(groups[4])

    if (checkDate(year,month,day)):
        events = see_in_GoogleCalender(year, month, day, CalendarId_odisan, Range=7) # おじさん情報を取得
        if not events:
            message.reply('ん⁉️その頃のオヂサンと君の予定が知りたいのカナ❓❓😳\nよーし笑　オヂサン、頑張っちゃうぞ❗️💪😂\n\n\n'+ 'アラ(^_^;)　どこも取られてなかったナ💦\nそしたら、その日は、オヂサン😎と美味しいパンケーキ🎂でデート💕なんて、どうカナ⁉️\nナンチャッテ😁', in_thread=True)
        else:
            event_summary_list = []
            for event in events:
                time = event['start'].get('dateTime', event['start'].get('date'))
                time = datetime.datetime.strptime(time[:-6], '%Y-%m-%dT%H:%M:%S')
                time_str = datetime.datetime.strftime(time, '%Y/%m/%d/%H:%M:%S')
                event_summary = '・' + time_str[5:-3] + ' : ' + str(event['summary'])
                event_summary_list.append(event_summary)
            message.reply('ん⁉️その頃のオヂサンと君の予定が知りたいのカナ❓❓😳\nよーし笑　オヂサン、頑張っちゃうぞ❗️💪😂\n\n\n'+ '以下のようにおじさんが書き込んでいました。\n' +'\n'.join(event_summary_list), in_thread=True)
    else:
        message.reply('妄言乙w(日程に誤情報が含まれている場合があります。ご確認ください。)', in_thread=True)


# help
@respond_to(r'使い方', re.DOTALL)  #　イベントの書き込みを探知
def tell_use(message):
    message.reply('''おじさんは、リプライをつけなくても、おじさんのいるチャンネル内の投稿に自動で反応します。できることは現状以下の通りです。\n\n
    【イベントを作成する】\n>日程:2020/10/30/10:30-19:30\n>内容:SoraTakashimaの誕生日\n\n上のようにイベント内容を投稿してください。\n
    (時間まで指定してください。区切り文字は、「/ . -」の３ついずれも使えます。)\n
    (改行後の文章もメッセージ終わりまで「内容」に含まれます。)\n(時間は、例えば「午後5時5分」なら、「17:05」のように表記してください。また、内容は32文字以下までしか受け付けていません。)\n\n
    【イベントが入っているか確認する】\n>イベント確認:2020/10/30\n\n上のように確認したい日程を投稿してください。\n前後二週間のイベント情報を取得できます。\n\n
    【おじさん情報を確認する】\n>おじさん確認:2020/10/30\n\n上のように確認したい日程を投稿してください。\n前後一週間のおじさんが書き込んだ予定を取得できます。''', in_thread=True)
