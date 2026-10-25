# 【免费分享声明】引擎创作者：reaesteve，CC BY-NC-SA 4.0
# 《电波》科普动画配乐 v2 —— 段落重排，总长不变（75.45s）
# 120 BPM，每小节整 2 秒；段落边界故意落在小节线上，供画面卡点：
#   seg1 0-4s(bar1-3)     波断
#   seg2 4-12s(bar3-7)    电子原地抖
#   seg3 12-22s(bar7-12)  电场荡开
#   seg4 22-34s(bar12-18) E 与 B（放慢，让曲线看得清）
#   seg5 34-46s(bar18-24) c = λf
#   seg6 46-58s(bar24-30) 射频频谱
#   seg7 58-68s(bar30-35) 电离层反射 · 天波跳跃   ← 新增
#   seg8 68-75.45s(bar35-150拍) 收尾
from compose_kit import *

channel(0, 'guzheng', 108, gain=1.34, pan=-0.08, reverb=0.42, hpf=120)
channel(1, 'strings', 49, gain=0.39, reverb=0.55, hpf=130, haas=15)
channel(2, 'bass', 43, gain=0.79, pan=-0.12, reverb=0.18)
channel(3, 'dizi', 73, gain=0.63, pan=0.24, reverb=0.44, hpf=280)
channel(4, 'taiko', 47, gain=0.55, reverb=0.32)
channel(5, 'pad', 88, gain=0.29, reverb=0.62, hpf=190, haas=18)
channel(9, 'drums', 0, gain=0.81, reverb=0.12)

tempo([(0, 144, 120, 120), (144, 150, 120, 90)], intro=0.0, tail=0.0, seed=2026)

prog = [('D', 4), ('Asus4', 4), ('Bm', 4), ('G', 4)]

# ---- seg1 (bar1-3, 0-4s) 静默张力
note(2, p('D2'), bar(1), 8, 42)
note(5, p('D4'), bar(1), 8, 26)
note(0, p('A5'), bar(2) + 2, 1.5, 58, tag='pulse')

# ---- seg2 (bar3-7, 4-12s) 电子原地抖：古筝单音，越敲越密
for i, (b_, n_, d_) in enumerate([(0, 'D5', 2), (2, 'E5', 2), (4, 'F#5', 1.5), (5.5, 'A5', 1),
                                  (6.5, 'B5', 1), (7.5, 'A5', 2), (9.5, 'F#5', 1.5), (11, 'E5', 1)]):
    note(0, p(n_), bar(3) + b_, d_, 62 + i * 2, tag='pulse' if i % 2 else None)

# ---- seg3 (bar7-12, 12-22s) 电场荡开：弦乐+pad 渐入，古筝琶音
bass(2, bar(7), prog + [('D', 4)], vel=54)
chords(1, bar(7), prog + [('D', 4)], vel=46)
expression(1, bar(7), bar(12), 38, 84)
chords(5, bar(7), prog + [('D', 4)], vel=34, lo=52, hi=74, n=3)
chords(0, bar(7), prog + [('D', 4)], vel=44, lo=50, hi=72, n=3, style='arp')
melody(0, bar(9), [('D5', 1.5), ('E5', 0.5), ('F#5', 1), ('A5', 1), ('B5', 2), ('A5', 2)],
       vel=70, tag='theme')

# ---- seg4 (bar12-18, 22-34s) E 与 B：节奏轻进但保持疏，配合放慢的画面
groove_a = {'kick': 'x.......x.......', 'hat': '....x.......x...'}
drums(bar(12), 6, groove_a, vel=60)
prog4 = (prog + [('D', 4), ('Bm', 4)])[:24]
bass(2, bar(12), prog4, vel=64, pattern=[(0, 1.5), (1.5, 0.5), (2, 2)])
chords(1, bar(12), prog4, vel=54)
chords(5, bar(12), prog4, vel=30, lo=52, hi=74, n=3)
chords(0, bar(12), prog4, vel=46, lo=50, hi=72, n=3, style='arp')
melody(3, bar(13), [('A5', 2), ('B5', 2), (None, 2), ('F#5', 2), ('E5', 2), (None, 2),
                    ('D5', 2), ('E5', 2), ('F#5', 4)], vel=64)
melody(0, bar(13), [('D5', 1), ('E5', 1), ('F#5', 1), ('A5', 1), ('B5', 2), ('A5', 2),
                    ('F#5', 1), ('E5', 1), ('D5', 2), ('E5', 4),
                    ('F#5', 1), ('A5', 1), ('B5', 1), ('D6', 1), ('B5', 2), ('A5', 2),
                    ('F#5', 2), ('E5', 2), ('D5', 2)], vel=78, tag='theme')

# ---- seg5 (bar18-24, 34-46s) c = λf：全奏，古筝跑动
groove_b = {'kick': 'x...x...x...x...', 'snare': '....x.......x...', 'hat': 'x.x.x.x.x.x.x.x.'}
drums(bar(18), 6, groove_b, vel=77)
for i in range(6):
    note(9, DRUM['crash'], bar(18) + i * 4, 1, 60 + i * 3)
prog5 = (prog + [('D', 4), ('Bm', 4)])[:24]
bass(2, bar(18), prog5, vel=76, pattern=[(0, 1.5), (1.5, 0.5), (2, 2)])
chords(1, bar(18), prog5, vel=62)
chords(5, bar(18), prog5, vel=28, lo=54, hi=76, n=3)
melody(0, bar(18), [('A5', 1), ('B5', 1), ('D6', 1), ('B5', 1), ('A5', 2), ('F#5', 2),
                    ('F#5', 1), ('A5', 1), ('B5', 2), ('A5', 4),
                    ('B5', 1), ('D6', 1), ('E6', 1), ('D6', 1), ('B5', 2), ('A5', 2),
                    ('F#5', 2), ('E5', 2), ('D5', 4),
                    ('A5', 1), ('B5', 1), ('D6', 2), ('E6', 2), ('D6', 2),
                    ('B5', 1), ('A5', 1), ('B5', 4), (None, 2)], vel=84, tag='theme')

# ---- seg6 (bar24-30, 46-58s) 射频频谱
groove_c = {'kick': 'x..x..x.x..x..x.', 'snare': '....x.......x...', 'hat': 'x.x.x.x.x.x.x.x.'}
drums(bar(24), 6, groove_c, vel=86)
for i in range(6):
    note(4, DRUM['tom_lo'], bar(24) + i * 4, 1, 74 + i * 2)
prog6 = (prog + [('Bm', 4), ('G', 4)])[:24]
bass(2, bar(24), prog6, vel=80, pattern=[(0, 1.5), (1.5, 0.5), (2, 2)])
chords(1, bar(24), prog6, vel=68)
chords(5, bar(24), prog6, vel=30, lo=54, hi=78, n=3)
expression(1, bar(24), bar(30), 68, 112)
melody(4, bar(24), [('D5', 4), ('B5', 4), ('A5', 4), ('F#5', 4), ('E5', 4), ('D5', 4)], vel=72)
melody(3, bar(24), [('D6', 4), ('F#5', 4), ('E5', 4), ('B5', 4), ('A5', 4), ('F#5', 4)], vel=64)
melody(0, bar(24), [('A5', 1), ('B5', 1), ('D6', 1), ('E6', 1), ('D6', 2), ('B5', 2),
                    ('A5', 1), ('B5', 1), ('D6', 2), ('E6', 4),
                    ('D6', 1), ('E6', 1), ('F#6', 1), ('E6', 1), ('D6', 2), ('B5', 2),
                    ('A5', 2), ('B5', 2), ('D6', 2), ('E6', 2)], vel=90, tag='theme')

# ---- seg7 (bar30-35, 58-68s) 电离层反射 · 天波跳跃：最高点
drums(bar(30), 5, groove_c, vel=90)
for i in range(5):
    note(4, DRUM['tom_hi'], bar(30) + i * 4, 1, 82 + i * 2)
prog7 = (prog + [('Bm', 4), ('G', 4)])[:20]
bass(2, bar(30), prog7, vel=84, pattern=[(0, 1.5), (1.5, 0.5), (2, 2)])
chords(1, bar(30), prog7, vel=72)
chords(5, bar(30), prog7, vel=32, lo=56, hi=80, n=3)
expression(1, bar(30), bar(35), 76, 118)
melody(4, bar(30), [('E6', 2), ('D6', 2), ('B5', 2), ('A5', 2), ('B5', 4), ('D6', 4)], vel=80)
melody(3, bar(30), [('A5', 4), ('F#5', 4), ('E5', 4), ('D5', 4), ('E5', 4)], vel=70)
melody(0, bar(30), [('D6', 1), ('E6', 1), ('F#6', 1), ('E6', 1), ('D6', 2), ('B5', 2),
                    ('E6', 1), ('F#6', 1), ('A6', 1), ('F#6', 1), ('E6', 2), ('D6', 2),
                    ('B5', 2), ('D6', 2), ('E6', 4), ('D6', 4)], vel=94, tag='theme')

# ---- seg8 (bar35-150, 68-75.45s) 收尾
chords(1, bar(35), [('D', 8), ('G', 8)], vel=52)
bass(2, bar(35), [('D', 8), ('G', 8)], vel=56)
chords(5, bar(35), [('D', 8), ('G', 8)], vel=30, lo=54, hi=76, n=3)
melody(3, bar(35), [('A5', 4), ('F#5', 4), ('E5', 6), (None, 2)], vel=58)
melody(0, bar(35), [('B5', 2), ('A5', 2), ('F#5', 4), ('E5', 2), ('D5', 4), (None, 2)], vel=72, tag='theme')
note(4, DRUM['crash'], bar(35), 1, 52)

export(end_beat=150)
