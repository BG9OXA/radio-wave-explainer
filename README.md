# 电波 · The Wave

一支 **75 秒的无线电波科普动画**：单页 Canvas 手绘全部画面，配乐由代码程序化生成，音画硬卡小节线同步。零依赖、可复现、可从零重渲。

> A 75-second explainer on radio waves. Every frame is drawn by hand-written Canvas 2D code; the soundtrack is generated procedurally from source. Picture and sound are locked to the same bar grid, so the animation cuts exactly on the beat.

**▶ 在线观看（手机也能播）** — 打开 `wave_preview.html` 即可，单文件、字体与音乐全部内嵌，不需要服务器：
`https://bg9oxa.github.io/radio-wave-explainer/wave_preview.html`

---

## 目录

- [它讲了什么](#它讲了什么)
- [科学要点（也是这个项目最在意的地方）](#科学要点也是这个项目最在意的地方)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [文件说明](#文件说明)
- [音画同步是怎么做到的](#音画同步是怎么做到的)
- [许可](#许可)
- [致谢](#致谢)

---

## 它讲了什么

六个章节，回答一个朴素的问题：**我按下发射键，电波是怎么飞出去的？**

| 时间 | 章节 | 内容 |
|---|---|---|
| 0–4s | 引子 | 一条波从中间断开——走掉的是场，留下的是电子 |
| 4–12s | 01 电子 | 导体里的自由电子**集体同步振荡**，一步都没走 |
| 12–22s | 02 场的传播 | 抖动甩出一圈圈向外扩散的电场 |
| 22–34s | 03 E 与 B | 用三维坐标系呈现电场、磁场、传播方向三者两两垂直且同相 |
| 34–46s | 04 速度 | `c = λf`：波长变，频率变，真空中的速度不变 |
| 46–58s | 05 波段 | 从长波到微波的频谱，20 米波段（14 MHz）落在短波里 |
| 58–68s | 06 天波 | 短波不贴地走，靠电离层反射一跳几千公里 |
| 68–75.45s | 收尾 | 你此刻听到的每个字，都是这样飞过来的 |

---

## 科学要点（也是这个项目最在意的地方）

科普动画最容易死在"好看但讲错"。以下每一条都在画面里被显式表达，改动时请不要破坏：

1. **电子没有跑出去。** 天线里是自由电子的集体同步振荡，位移只有**皮米级**——100 W、14 MHz 条件下约 1.18 pm，不到一个原子直径的 1%（`nm` 都高估了三个数量级）。
2. **所有电子同相。** 不是"每个电子各自抖"。半波振子上电流呈驻波分布 `I(z) ∝ cos(πz/L)`：中间电流最大、两端为零，所以中间的电子抖得最厉害，两端的几乎不动。
3. **电荷堆在两端，且随相位交换符号。** 电子带负电——电子向上聚集时**上端为负**、下端为正。这个振荡偶极子才是辐射的源头。
4. **E ⟂ B ⟂ c，且 E 与 B 同相。** 不是"一个衰减另一个生成"，而是同时达到最大、同时过零。
5. **不说"变化的电场生出磁场"。** 这句话在同相平面波里有循环论证的毛病（E 达最大时 dE/dt = 0，却要"生出"同样最大的 B）。片中改为"一个稍有变化，另一个立刻响应，一道向前"。
6. **真空中的光速不变，介质里会变慢。** 字幕明确写了"在真空里"。
7. **短波远距离靠天波，不靠地波。** 14 MHz 的地波只能传几十公里；跨洋通信靠电离层（约 300 km 高空）反射，一次跳跃约 2000–3000 km。
8. **"光 1 秒绕地球 7.5 圈"只用来做速度尺度感**，绝不能让观众以为短波贴着地表绕地球跑。

---

## 技术架构

```
promo.html          单页 Canvas 2D 动画（约 780 行，无任何框架）
  ├── 七个场景函数 seg1…seg8，按时间切片调度
  ├── 四个导出钩子：__ready / __frame(t) / __duration / __cues
  └── 字体子集内嵌，不依赖网络

music_wave.py       程序化配乐源码（120 BPM，D 宫五声）
  └── 输出 music.mp3（75.452s，823 音符，7 轨）

render.mjs          零依赖逐帧导出器（Node 内置 WebSocket 直连 CDP）
  ├── 打开 ?export=1 → 等 __ready → 逐帧调 __frame(t)
  └── ffmpeg 合成 H.264 + AAC，+faststart
```

**为什么用 Canvas 2D 而不是 WebGL？** 这支片子是矢量线条 + 发光叠加，Canvas 2D 足够；而且在无 GPU 的环境里，Canvas 2D 比 WebGL 软件渲染快约 18 倍（实测 0.2 fps → 3.6 fps）。

**为什么不用多 worker 并行？** 实测单标签页顺序渲染 **15.2 fps**，比之前 2–4 个 Chrome 进程并行（3.6 fps）快 4 倍——多开浏览器的进程开销远大于收益。

---

## 快速开始

### 只想看

双击 `wave_preview.html`。单文件 2.7 MB，字体和音乐全内嵌，拷到任何地方都能播。

### 想改画面

编辑 `promo.html`，然后把整个目录起个静态服务：

```bash
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000/promo.html
```

带 `?t=30` 可以直接定格到第 30 秒检查构图（改画面时最常用）。

### 想改配乐

配乐依赖 [AI_MUSIC_CREATOR](https://github.com/maxtinnate/AI_MUSIC_CREATOR) 的合成引擎（本仓库未包含，见[致谢](#致谢)）。把引擎装好后：

```bash
python music_wave.py      # 生成 song.wav + notes.json
ffmpeg -i song.wav -c:a libmp3lame -b:a 192k music.mp3
```

⚠️ **改配乐必须同步改画面。** 段落边界 `4 / 12 / 22 / 34 / 46 / 58 / 68` 秒同时写死在 `music_wave.py` 的 `bar()` 调用和 `promo.html` 的 `const SEG` 里，两边必须一致，否则音画不同步。

### 想重新出片

需要 Node ≥ 22、ffmpeg、Chrome/Chromium：

```bash
node render.mjs                                   # 整片 1080p30
node render.mjs --from 22 --to 34 --fps 15        # 只渲染 E/B 那段试片
node render.mjs --shots 6,31,63                   # 只出几张静帧
CHROME=/path/to/chrome node render.mjs            # 指定浏览器
```

Windows 用户见 `tools/setup_4f.ps1` 与 `tools/render_4f.ps1`（PowerShell 原生版）。

---

## 文件说明

| 文件 | 说明 |
|---|---|
| `promo.html` | 动画本体，所有画面都是这个文件里的 Canvas 代码画的 |
| `wave_preview.html` | 打包好的单文件预览版（字体子集 + 音乐 base64 内嵌） |
| `music_wave.py` | 配乐源码，注释里标了每个段落对应的画面 |
| `music.mp3` | 配乐成品，75.452 秒 |
| `render.mjs` | 零依赖导出器 |
| `fonts/*.woff2` | Noto Serif SC 子集（只含本片用到的 538 个字符，86 KB/字重） |
| `tools/make_font_subset.py` | 重新生成字体子集（**改了字幕必须重跑**，否则新字会缺） |
| `tools/build_singlefile.py` | 把 `promo.html` 打包成单文件预览版 |
| `tools/*.ps1` | Windows 渲染脚本 |
| `docs/shots/` | 各章节关键帧 |

### 关于字体

仓库里只放**字体子集**（原字体 14.1 MB/字重 → 子集 86 KB）。子集只覆盖当前文案用到的字：

- 只改画面不动文字 → 不用管
- **改了字幕 → 必须重跑 `tools/make_font_subset.py`**，否则新加的字会缺
- 想要完整字体：[Noto Serif SC](https://fonts.google.com/noto/specimen/Noto+Serif+SC)（SIL OFL 1.1），下好放 `fonts/` 并把 `.ttf` 命名成 `NotoSerifSC-400.ttf` / `-700.ttf`，`@font-face` 会优先用 woff2、回退到 ttf

---

## 音画同步是怎么做到的

不是"大致对齐"，是**数学上锁死**：

1. 配乐定 **120 BPM** → 每小节整 **2.000 秒**，一节不差。
2. 所有段落边界都落在小节线上：`bar3=4s`、`bar7=12s`、`bar12=22s`、`bar18=34s`、`bar24=46s`、`bar30=58s`、`bar35=68s`。
3. 画面用同一组数字切场景（`const SEG`），重音点用 `HITS` 驱动闪白。
4. 导出时按 `__frame(t)` 逐帧求值，同一个 `t` 永远得到同一帧——**渲染与机器快慢无关**，可复现。

改任何一个段落边界，三处必须同时改：`music_wave.py` 的 `bar()`、`promo.html` 的 `SEG`、`SUBS`/`CHAP` 的时间戳。

---

## 许可

本项目**按部分**授权，请注意区别：

| 部分 | 许可 | 说明 |
|---|---|---|
| 代码（`promo.html`、`render.mjs`、`tools/*.py`、`tools/*.ps1`） | **MIT** | 见 [LICENSE](LICENSE) |
| 配乐（`music.mp3`、`music_wave.py`） | **CC BY-NC-SA 4.0** | 因使用 CC BY-NC-SA 4.0 的合成引擎生成，配乐沿用同一协议；非商业、署名、相同方式共享 |
| 字体 `fonts/*.woff2` | **SIL OFL 1.1** | Noto Serif SC 子集，署名见下 |

**简单说**：代码随便用、随便改；配乐可以非商业使用，要署名并以相同协议分享；不要拿去做付费内容。

---

## 致谢

- **配乐引擎**：[maxtinnate/AI_MUSIC_CREATOR](https://github.com/maxtinnate/AI_MUSIC_CREATOR)（创作者 reaesteve），C 语言合成的 SoundFont 引擎 + 制作文档，CC BY-NC-SA 4.0。本仓库**不包含**该引擎，只包含用它生成的曲子与调用脚本。
- **动画架构参考**：[AnctyEnly453/abstract-algebra-promo](https://github.com/AnctyEnly453/abstract-algebra-promo) — `__ready` / `__frame(t)` / `__duration` / `__cues` 这套逐帧导出接口的思路来自这个项目。该仓库未声明许可证，因此本项目的 `render.mjs` 是**另行实现**的，未复制其代码。
- **字体**：[Noto Serif SC](https://fonts.google.com/noto/specimen/Noto+Serif+SC)，SIL Open Font License 1.1。
- **科学审校**：本项目在制作过程中修正了多处常见科普误述（见[科学要点](#科学要点也是这个项目最在意的地方)），特别感谢指出"电子到底在导体里还是球体里"这个问题的读者——它直接导致整段重写。

---

<p align="center"><i>Made with Canvas, a bar grid, and a lot of second thoughts about physics.</i></p>
