"""Wikimedia Commons 上有没有普通话拼音音节（带声调）的真人录音：打印几种文件名写法各找到多少（只读公开信息）"""
import json, sys, urllib.parse, urllib.request
API = 'https://commons.wikimedia.org/w/api.php'
UA = 'NihongoDojo/1.0 (pronunciation research; https://koshokai.github.io/nihonggo-dojo/)'
def q(**p):
    p.update(format='json')
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(p), headers={'User-Agent': UA})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())
SYL = ['ma1', 'ma2', 'ma3', 'ma4', 'zhong1', 'shi4', 'xue2', 'nü3', 'lü4', 'er2', 'ang4']
MARK = ['mā', 'má', 'mǎ', 'mà', 'zhōng', 'shì', 'xué', 'nǚ', 'lǜ', 'ér', 'àng']
for pat in ['Zh-{}.ogg', 'Zh-pinyin-{}.ogg', 'Pinyin-{}.ogg', 'Cmn-{}.ogg', 'Zh-{}.oga']:
    found = []
    for s in SYL + MARK:
        t = 'File:' + pat.format(s)
        r = q(action='query', titles=t, prop='imageinfo', iiprop='extmetadata')
        pg = list(r['query']['pages'].values())[0]
        if 'missing' not in pg:
            lic = pg.get('imageinfo', [{}])[0].get('extmetadata', {}).get('LicenseShortName', {}).get('value', '?')
            found.append(f'{s}({lic})')
    print(pat, len(found), found[:12], flush=True)
for term in ['Mandarin pinyin syllable pronunciation', 'Category:Mandarin pronunciation', 'pinyin tone audio']:
    r = q(action='query', list='search', srsearch=term, srnamespace=14, srlimit=10)
    print('cat search', term, [x['title'] for x in r['query']['search']], flush=True)
for cat in ['Category:Mandarin pronunciation', 'Category:Pinyin', 'Category:Mandarin pronunciation of pinyin syllables', 'Category:Chinese pronunciation']:
    r = q(action='query', list='categorymembers', cmtitle=cat, cmlimit=20)
    print(cat, [x['title'] for x in r.get('query', {}).get('categorymembers', [])][:20], flush=True)
