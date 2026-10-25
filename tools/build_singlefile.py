#!/usr/bin/env python3
"""把 promo.html 打成单文件预览版：字体子集化 + 音乐 base64 内嵌，双击即播，零依赖。"""
import base64, re, subprocess, sys, os

HERE = '/opt/data/projects/wave'
SRC = f'{HERE}/promo.html'
OUT = f'{HERE}/wave_preview.html'
PY = '/opt/data/venv/music/bin/python'

html = open(SRC, encoding='utf-8').read()

# ---- 1. 收集所有要渲染的字符（HTML 文本 + JS 字符串 + 动态标签文案）----
extra = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
         ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
         'λμΩωπΔ×÷±≈⊥∥→←↑↓⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉·—–…、。，；：？！“”‘’（）《》【】')
chars = set(extra)
chars |= set(re.findall(r'[^\x00-\x7f]', html))          # 页面里出现的全部非 ASCII
# 场景里会用到的补充字（保险）
chars |= set('电波频谱射长中短超微毫赫兹绕地球圈秒速度完全相同波长越短频率越高变原地抖动出圈向传播的天线里子其实一步都没走它们只是上下电场本身在空间前进不是跑和磁场互相垂直同时涨落彼此激发化的生出又你此刻听到每字都这飞过来')
text = ''.join(sorted(chars))
print(f'字符集: {len(text)} 个')

# ---- 2. 字体子集化 → woff2 ----
fonts = {}
for w in ('400', '700'):
    src_f = f'{HERE}/fonts/NotoSerifSC-{w}.ttf'
    out_f = f'/tmp/subset-{w}.woff2'
    r = subprocess.run([PY, '-m', 'fontTools.subset', src_f,
                        f'--text={text}', f'--output-file={out_f}',
                        '--flavor=woff2', '--layout-features=*',
                        '--no-hinting', '--desubroutinize',
                        '--drop-tables+=DSIG'], capture_output=True, text=True)
    if r.returncode != 0:
        print('subset 失败:', r.stderr[-800:]); sys.exit(1)
    fonts[w] = out_f
    print(f'  字重 {w}: {os.path.getsize(src_f)/1e6:.1f}MB → {os.path.getsize(out_f)/1024:.0f}KB')

for w in ('400', '700'):
    b64 = base64.b64encode(open(fonts[w], 'rb').read()).decode()
    html = html.replace(
        f"url('fonts/NotoSerifSC-{w}.ttf') format('truetype')",
        f"url(data:font/woff2;base64,{b64}) format('woff2')")
    assert 'fonts/NotoSerifSC' not in html or w == '400', '字体替换不完整'

# ---- 3. 音乐内嵌 ----
mp3 = open(f'{HERE}/music.mp3', 'rb').read()
html = html.replace('src="music.mp3"',
                    'src="data:audio/mpeg;base64,' + base64.b64encode(mp3).decode() + '"')
print(f'  音乐: {len(mp3)/1e6:.1f}MB → base64 {len(mp3)*4/3/1e6:.1f}MB')
assert 'src="music.mp3"' not in html, '音乐替换失败'
assert 'fonts/' not in html.replace('fonts/Noto', 'fonts/Noto'), '还有外部字体引用' if 'url(\'fonts' in html else True

open(OUT, 'w', encoding='utf-8').write(html)
print(f'\n✓ {OUT}  {os.path.getsize(OUT)/1e6:.2f} MB')
