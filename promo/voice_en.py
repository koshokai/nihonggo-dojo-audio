# 宣传动画的英语配音（Kokoro, Apache 2.0, af_heart）：读 promo/lines-en.json，生成 promo/voice-en/*.wav
import json, pathlib, numpy as np, soundfile as sf
from kokoro import KPipeline
pipe = KPipeline(lang_code='a')
out = pathlib.Path('promo/voice-en'); out.mkdir(parents=True, exist_ok=True)
for key, en, _ja in json.load(open('promo/lines-en.json', encoding='utf-8')):
    a = np.concatenate([x for _, _, x in pipe(en, voice='af_heart', speed=1.05)])
    a = a / max(1e-6, np.abs(a).max()) * 0.89
    sf.write(out / f'{key}.wav', a, 24000)
    print(key, round(len(a) / 24000, 2))
