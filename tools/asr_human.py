"""真人录音（Wikimedia Commons / Lingua Libre 的志愿者录音）的听写检查：用 faster-whisper 把每条录音听一遍，和单词比，
找出录错词、只录了一半、听不清的。只检查公开的单词录音（index-en-human.json、ja/index-ja-human.json），结果写进 asr-human-<lang>.json。
    python3 tools/asr_human.py en|ja [limit]"""
import difflib, json, re, sys, unicodedata
from faster_whisper import WhisperModel

lang = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
idx_path, base = ('index-en-human.json', '') if lang == 'en' else ('ja/index-ja-human.json', 'ja/')
idx = json.load(open(idx_path, encoding='utf-8'))
items = list(idx.items())[:limit or None]
model = WhisperModel('small', device='cpu', compute_type='int8')

if lang == 'ja':
    import pykakasi
    K = pykakasi.kakasi()
    def norm(s):
        s = unicodedata.normalize('NFKC', s)
        s = ''.join(x['hira'] for x in K.convert(s))
        return re.sub(r'[^ぁ-ゖー]', '', s).replace('ー', '')
else:
    def norm(s):
        return re.sub(r'[^a-z0-9]', '', s.lower())

out = []
for i, (w, f) in enumerate(items):
    segs, _ = model.transcribe(base + f, language=lang, beam_size=5, vad_filter=False, condition_on_previous_text=False,
                               initial_prompt=None, without_timestamps=True)
    hyp = ''.join(s.text for s in segs).strip()
    a, b = norm(w), norm(hyp)
    score = difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0
    out.append([w, f, hyp, round(score, 2)])
    if (i + 1) % 200 == 0:
        print(f'{i + 1}/{len(items)}', flush=True)
bad = [x for x in out if x[3] < 0.6]
json.dump({'n': len(out), 'low': sorted(bad, key=lambda x: x[3]), 'all_scores': {x[0]: x[3] for x in out}},
          open(f'asr-human-{lang}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(lang, 'checked', len(out), 'low score', len(bad))
