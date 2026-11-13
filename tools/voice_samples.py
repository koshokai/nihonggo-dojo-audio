"""日语声音试听：同样的 5 句话，用几种声音各生成一遍，放在 samples/ 下，配一个试听页面（samples/index.html）。
用法：python3 tools/voice_samples.py voicevox | sbv2"""
import json, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

OUT = Path('samples'); OUT.mkdir(exist_ok=True)
SENTS = ['おはようございます。今日はいい天気ですね。', '駅の前に、新しいパン屋ができました。', 'すみません、この電車は東京駅に止まりますか。',
         '週末は友だちと映画を見に行くつもりです。', '日本語の勉強は大変ですが、とても楽しいです。']


def mp3(wav, path):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(wav), '-ac', '1', '-b:a', '64k', str(path)], check=True)


def meta(key, label, credit):
    p = OUT / 'voices.json'
    d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    d[key] = {'label': label, 'credit': credit}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')


def voicevox():
    E = 'http://127.0.0.1:50021'
    def api(path, params=None, body=None):
        url = E + path + ('?' + urllib.parse.urlencode(params) if params else '')
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else (b'' if params and body is None and path != '/speakers' else None), headers={'Content-Type': 'application/json'})
        return urllib.request.urlopen(req, timeout=300).read()
    speakers = json.loads(urllib.request.urlopen(E + '/speakers', timeout=60).read())
    want = [('冥鳴ひまり', 'ノーマル', '现在用的声音'), ('四国めたん', 'ノーマル', ''), ('春日部つむぎ', 'ノーマル', ''), ('九州そら', 'ノーマル', ''), ('No.7', 'アナウンス', '播音风格'),
            ('WhiteCUL', 'ノーマル', ''), ('青山龍星', 'ノーマル', '男声'), ('剣崎雌雄', 'ノーマル', '男声'), ('もち子さん', 'ノーマル', ''), ('ナースロボ＿タイプＴ', 'ノーマル', '')]
    for name, style, note in want:
        sp = next((s for s in speakers if s['name'] == name), None)
        st = sp and next((x for x in sp['styles'] if x['name'] == style), None)
        if not st:
            print('skip', name); continue
        key = f'vv-{st["id"]}'; (OUT / key).mkdir(exist_ok=True)
        for i, t in enumerate(SENTS):
            q = json.loads(api('/audio_query', {'text': t, 'speaker': st['id']}))
            q['speedScale'] = 0.95; q['intonationScale'] = 1.15
            wav = api('/synthesis', {'speaker': st['id']}, q)
            Path('/tmp/s.wav').write_bytes(wav); mp3('/tmp/s.wav', OUT / key / f'{i + 1}.mp3')
        meta(key, f'VOICEVOX {name}（{style}）' + (f' · {note}' if note else ''), f'VOICEVOX:{name}')
        print('ok', key)


def sbv2():
    import soundfile as sf
    from huggingface_hub import hf_hub_download, list_repo_files
    from style_bert_vits2.constants import Languages
    from style_bert_vits2.nlp import bert_models
    from style_bert_vits2.tts_model import TTSModel
    bert_models.load_model(Languages.JP, 'ku-nlp/deberta-v2-large-japanese-char-wwm')
    bert_models.load_tokenizer(Languages.JP, 'ku-nlp/deberta-v2-large-japanese-char-wwm')
    repo = 'litagin/style_bert_vits2_jvnv'
    files = list_repo_files(repo)
    for name, note in [('jvnv-F1-jp', '女声 1'), ('jvnv-F2-jp', '女声 2'), ('jvnv-M1-jp', '男声 1'), ('jvnv-M2-jp', '男声 2')]:
        try:
            st = next(f for f in files if f.startswith(name + '/') and f.endswith('.safetensors'))
            paths = [hf_hub_download(repo, f) for f in (st, f'{name}/config.json', f'{name}/style_vectors.npy')]
            model = TTSModel(model_path=Path(paths[0]), config_path=Path(paths[1]), style_vec_path=Path(paths[2]), device='cpu')
            key = 'sbv2-' + name.split('-')[1]; (OUT / key).mkdir(exist_ok=True)
            for i, t in enumerate(SENTS):
                sr, audio = model.infer(text=t, length=1.05)
                sf.write('/tmp/s.wav', audio, sr); mp3('/tmp/s.wav', OUT / key / f'{i + 1}.mp3')
            meta(key, f'Style-Bert-VITS2 JVNV {note}', 'Style-Bert-VITS2 JVNV (CC BY-SA 4.0)')
            print('ok', key)
        except Exception as e:   # 一个声音失败不影响其他的
            print('fail', name, type(e).__name__, str(e)[:200])


def page():
    v = json.loads((OUT / 'voices.json').read_text(encoding='utf-8'))
    rows = ''.join(f'<section><h2>{x["label"]}</h2>' + ''.join(f'<div class="r"><span>{t}</span><audio controls preload="none" src="{k}/{i + 1}.mp3"></audio></div>' for i, t in enumerate(SENTS)) + '</section>' for k, x in sorted(v.items()) if (OUT / k / '1.mp3').exists())
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>日语声音试听</title><style>body{{font-family:system-ui,sans-serif;max-width:640px;margin:0 auto;padding:16px;line-height:1.6}}section{{border:1px solid #ddd;border-radius:12px;padding:12px 14px;margin:14px 0}}h2{{font-size:1.05rem;margin:0 0 8px}}.r{{margin:8px 0}}.r span{{display:block;font-size:.95rem}}audio{{width:100%;height:36px}}@media(prefers-color-scheme:dark){{body{{background:#14121f;color:#eee}}section{{border-color:#444}}}}</style>
<h1>日语声音试听</h1><p>同样的 5 句话，用不同的声音各读一遍。听完告诉我想用哪一个（说标题里的名字就行）。</p>{rows}''', encoding='utf-8')


if __name__ == '__main__':
    {'voicevox': voicevox, 'sbv2': sbv2, 'page': page}[sys.argv[1]]()
