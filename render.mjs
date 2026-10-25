#!/usr/bin/env node
/**
 * 零依赖逐帧导出器 —— 只用 Node 内置 WebSocket 说 Chrome DevTools Protocol。
 * 不需要 npm install，不需要 puppeteer。
 *
 * 用法:
 *   node render.mjs                          # 整片 1080p30 导出为 out.mp4
 *   node render.mjs --from 0 --to 6          # 只渲染 0-6 秒（试片）
 *   node render.mjs --fps 15 --out test.mp4  # 低帧率快出
 *   node render.mjs --shots 3,10,30          # 只导出这几个时间点的静帧
 *
 * 依赖: node >= 22 (内置 WebSocket), ffmpeg, Chrome/Chromium
 * 环境变量 CHROME 可指定浏览器路径。
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

// ---------- 参数 ----------
const argv = process.argv.slice(2);
const arg = (k, d) => {
  const i = argv.indexOf('--' + k);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : d;
};
const HERE = path.dirname(new URL(import.meta.url).pathname);
const PAGE = path.resolve(arg('page', path.join(HERE, 'promo.html')));
const MP3 = arg('mp3', path.join(HERE, 'music.mp3'));
const OUT = arg('out', path.join(HERE, 'out.mp4'));
const FPS = Number(arg('fps', 30));
const CRF = arg('crf', '18');
const SHOTS = arg('shots', '');
const CHROME = process.env.CHROME || '/usr/bin/google-chrome';
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'framedump-'));

// ---------- 极简 CDP 客户端 ----------
class CDP {
  constructor(url) { this.url = url; this.id = 0; this.pending = new Map(); }
  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);
      this.ws.addEventListener('open', () => resolve());
      this.ws.addEventListener('error', e => reject(new Error('CDP connect failed: ' + (e.message || e))));
      this.ws.addEventListener('message', ev => {
        const msg = JSON.parse(ev.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
        }
      });
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.pending.has(id)) { this.pending.delete(id); reject(new Error(`${method} timeout`)); }
      }, 120000);
    });
  }
  async evaluate(expression) {
    const r = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error('JS: ' + (r.exceptionDetails.text || '') + ' ' + (r.exceptionDetails.exception?.description || ''));
    return r.result.value;
  }
  close() { try { this.ws.close(); } catch {} }
}

// ---------- 启动 Chrome ----------
const sleep = ms => new Promise(r => setTimeout(r, ms));

function launch() {
  const port = 9333 + Math.floor(Math.random() * 400);
  const proc = spawn(CHROME, [
    '--headless', '--no-sandbox', '--disable-dev-shm-usage', '--hide-scrollbars',
    '--disable-gpu', '--window-size=1920,1080', '--force-device-scale-factor=1',
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${path.join(TMP, 'profile')}`,
    `file://${PAGE}?export=1`,
  ], { stdio: ['ignore', 'ignore', 'pipe'] });
  proc.stderr.on('data', () => {});            // 吞掉 ALSA/GPU 噪声
  return { proc, port };
}

async function findPage(port, tries = 60) {
  for (let i = 0; i < tries; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const page = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error('Chrome 没起来，或 CDP 端口不可达。检查 CHROME 环境变量是否指向可执行的浏览器。');
}

// ---------- 主流程 ----------
const { proc, port } = launch();
let cdp;
try {
  cdp = new CDP(await findPage(port));
  await cdp.connect();
  await cdp.send('Runtime.enable');

  // 等字体与场景就绪（页面暴露的 __ready 是函数，调用后返回布尔）
  let ready = false;
  for (let i = 0; i < 120; i++) {
    ready = await cdp.evaluate(
      'typeof window.__ready === "function" ? !!window.__ready() : window.__ready === true');
    if (ready) break;
    await sleep(250);
  }
  if (!ready) throw new Error('页面 __ready 超时（字体未加载完？）');

  const TOTAL = await cdp.evaluate('window.__duration');

  // 只出静帧
  if (SHOTS) {
    for (const s of SHOTS.split(',')) {
      const t = Number(s);
      const dataUrl = await cdp.evaluate(`__frame(${t})`);
      const file = path.join(HERE, 'shots', `t${t.toFixed(2).padStart(7, '0')}.jpg`);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, Buffer.from(dataUrl.split(',')[1], 'base64'));
      console.log('shot', file);
    }
    process.exit(0);
  }

  const from = Number(arg('from', 0));
  const to = Math.min(Number(arg('to', TOTAL)), TOTAL);
  const n = Math.round((to - from) * FPS);
  console.log(`渲染 ${from}s → ${to}s，${n} 帧 @${FPS}fps，共 ${TOTAL.toFixed(3)}s`);

  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const t = from + i / FPS;
    const dataUrl = await cdp.evaluate(`__frame(${t})`);
    fs.writeFileSync(path.join(TMP, `f${String(i).padStart(5, '0')}.jpg`), Buffer.from(dataUrl.split(',')[1], 'base64'));
    if (i % 30 === 0 || i === n - 1) {
      const el = (Date.now() - t0) / 1000;
      const fps = (i + 1) / Math.max(el, .001);
      process.stdout.write(`\r  ${i + 1}/${n} 帧  ${fps.toFixed(1)} fps  剩余约 ${((n - i - 1) / Math.max(fps, .01)).toFixed(0)}s   `);
    }
  }
  console.log('\n编码 mp4 …');

  await new Promise((resolve, reject) => {
    const ff = spawn('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-framerate', String(FPS), '-i', path.join(TMP, 'f%05d.jpg'),
      ...(fs.existsSync(MP3) ? ['-i', MP3] : []),
      '-c:v', 'libx264', '-preset', 'medium', '-crf', CRF, '-pix_fmt', 'yuv420p',
      ...(fs.existsSync(MP3) ? ['-c:a', 'aac', '-b:a', '192k', '-shortest'] : []),
      '-movflags', '+faststart',
      OUT,
    ], { stdio: ['ignore', 'inherit', 'inherit'] });
    ff.on('exit', c => c === 0 ? resolve() : reject(new Error('ffmpeg 失败，退出码 ' + c)));
  });

  console.log('✓', OUT, (fs.statSync(OUT).size / 1048576).toFixed(1) + ' MB');
} finally {
  cdp?.close();
  proc.kill('SIGKILL');
  fs.rmSync(TMP, { recursive: true, force: true });
}
