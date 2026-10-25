#!/usr/bin/env python3
"""从 promo.html 里提取用到的字符，把 Noto Serif SC 子集化成 woff2。
   完整字体 14.8MB/字重 → 子集约 90KB/字重，仓库才放得下。
   注意：子集只覆盖当前文案；改了字幕要重跑本脚本。"""
import re, os
from fontTools.subset import main as subset_main

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 仓库根目录
SRC_HTML = os.path.join(HERE, 'promo.html')
FULL = '/opt/data/projects/wave/fonts'          # 完整字体所在处
OUT = os.path.join(HERE, 'fonts')
os.makedirs(OUT, exist_ok=True)

html = open(SRC_HTML, encoding='utf-8').read()
chars = set(chr(c) for c in range(0x20, 0x7f))   # ASCII 全量
chars |= set(re.findall(r'[^\x00-\x7f]', html))  # 所有非 ASCII（中文/希腊/符号）
chars |= set('λπΩμ≈°·—…⁶²³⁴⁰')

for w in ('400', '700'):
    src = os.path.join(FULL, f'NotoSerifSC-{w}.ttf')
    dst = os.path.join(OUT, f'NotoSerifSC-{w}.woff2')
    subset_main([src, f'--text={"".join(sorted(chars))}', f'--output-file={dst}',
                 '--flavor=woff2', '--layout-features=*', '--no-hinting'])
    print(f'  {w}: {os.path.getsize(src)/1048576:.1f}MB → {os.path.getsize(dst)/1024:.0f}KB')

print(f'字符集 {len(chars)} 个 → {OUT}')
