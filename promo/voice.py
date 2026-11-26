# 宣传动画的日语配音：VOICEVOX（春日部つむぎ），每句一个 wav
import json, urllib.request, urllib.parse, sys
E = 'http://127.0.0.1:50021'
SPK = 8
for key, ja, en in json.load(open('promo/lines.json', encoding='utf-8')):
    q = json.loads(urllib.request.urlopen(urllib.request.Request(f'{E}/audio_query?' + urllib.parse.urlencode({'text': ja, 'speaker': SPK}), method='POST')).read())
    q['speedScale'] = 1.05; q['intonationScale'] = 1.25; q['pitchScale'] = 0.02; q['prePhonemeLength'] = 0.05; q['postPhonemeLength'] = 0.15
    w = urllib.request.urlopen(urllib.request.Request(f'{E}/synthesis?speaker={SPK}', data=json.dumps(q).encode(), headers={'Content-Type': 'application/json'})).read()
    open(f'promo/voice/{key}.wav', 'wb').write(w)
    # 口型用：每个音拍的长度（秒）和元音
    mor = [[m['vowel'], (m.get('consonant_length') or 0) + m['vowel_length']] for p in q['accent_phrases'] for m in p['moras'] + ([p['pause_mora']] if p.get('pause_mora') else [])]
    json.dump({'pre': q['prePhonemeLength'] / q['speedScale'], 'speed': q['speedScale'], 'moras': mor}, open(f'promo/voice/{key}.json', 'w'))
    print(key, len(w))
