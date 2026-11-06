# nihonggo-dojo-audio

猫先生（https://koshokai.github.io/nihonggo-dojo/）英语板块的录音，用 GitHub Pages 提供（主站放不下：一个 GitHub Pages 网站最多 1 GB）。

- `en-k/`：单词、例句、语法例句、阅读正文（Kokoro TTS，Apache 2.0；`index-en.json`：原文 → 文件）
- `en-listen/`：听力对话，每题一个文件（`index-en-listen.json`：题目 id → 文件）
- `en-h/`：单词的真人录音（Wikimedia Commons / Lingua Libre，作者和授权见主站「内容来源」；`index-en-human.json`）

录音由 `.github/workflows/kokoro.yml` 生成：文字和脚本取自 koshokai/nihonggo-dojo。
