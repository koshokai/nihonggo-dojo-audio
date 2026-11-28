# 宣传动画的日语配音：VOICEVOX（春日部つむぎ），每句一个 wav
import json, urllib.request, urllib.parse, sys
E = 'http://127.0.0.1:50021'
# 参数：台词文件、输出目录、角色编号（默认：promo/lines.json → promo/voice，8 = 春日部つむぎ）
LINES = sys.argv[1] if len(sys.argv) > 1 else 'promo/lines.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'promo/voice'
SPK = int(sys.argv[3]) if len(sys.argv) > 3 else 8
TUNE = {8: dict(speedScale=1.05, intonationScale=1.25, pitchScale=0.02), 2: dict(speedScale=1.18, intonationScale=1.55, pitchScale=0.04, volumeScale=1.1)}.get(SPK, dict(speedScale=1.08, intonationScale=1.15, pitchScale=0.0))
for key, ja, *_ in json.load(open(LINES, encoding='utf-8')):
    q = json.loads(urllib.request.urlopen(urllib.request.Request(f'{E}/audio_query?' + urllib.parse.urlencode({'text': ja, 'speaker': SPK}), method='POST')).read())
    q.update(TUNE); q['prePhonemeLength'] = 0.05; q['postPhonemeLength'] = 0.15
    w = urllib.request.urlopen(urllib.request.Request(f'{E}/synthesis?speaker={SPK}', data=json.dumps(q).encode(), headers={'Content-Type': 'application/json'})).read()
    open(f'{OUT}/{key}.wav', 'wb').write(w)
    # 口型用：每个音拍的长度（秒）和元音
    mor = [[m['vowel'], (m.get('consonant_length') or 0) + m['vowel_length']] for p in q['accent_phrases'] for m in p['moras'] + ([p['pause_mora']] if p.get('pause_mora') else [])]
    json.dump({'pre': q['prePhonemeLength'] / q['speedScale'], 'speed': q['speedScale'], 'moras': mor}, open(f'{OUT}/{key}.json', 'w'))
    print(key, len(w))
