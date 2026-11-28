# 宣传动画的英语配音（Kokoro, Apache 2.0, af_heart）：读 promo/lines-en.json，生成 promo/voice-en/*.wav
import json, pathlib, sys, numpy as np, soundfile as sf
# 参数：台词文件、输出目录、声音、语速（默认 promo/lines-en.json → promo/voice-en，af_heart，1.05）
LINES = sys.argv[1] if len(sys.argv) > 1 else 'promo/lines-en.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'promo/voice-en'
VOICE = sys.argv[3] if len(sys.argv) > 3 else 'af_heart'
SPEED = float(sys.argv[4]) if len(sys.argv) > 4 else 1.05
from kokoro import KPipeline
pipe = KPipeline(lang_code='a')
out = pathlib.Path(OUT); out.mkdir(parents=True, exist_ok=True)
for key, en, _ja in json.load(open(LINES, encoding='utf-8')):
    a = np.concatenate([x for _, _, x in pipe(en, voice=VOICE, speed=SPEED)])
    a = a / max(1e-6, np.abs(a).max()) * 0.89
    sf.write(out / f'{key}.wav', a, 24000)
    print(key, round(len(a) / 24000, 2))
