# ============================================================
#  《电波》渲染 —— Windows (4F) 版
#  用法：
#     powershell -ExecutionPolicy Bypass -File .\render_4f.ps1
#     powershell -ExecutionPolicy Bypass -File .\render_4f.ps1 -Mode preview
#     powershell -ExecutionPolicy Bypass -File .\render_4f.ps1 -Workers 6
#     powershell -ExecutionPolicy Bypass -File .\render_4f.ps1 -SoftwareGL   # 显卡有问题时退回软渲染
#
#  设计要点：
#   * 分段渲染（每 15 秒一段），某段失败不连累其余；断了只重跑那一段
#   * 每个分段各自带正确的音频切片，最后 -c copy 无损拼接
#   * 成片用英文名，避开 PowerShell/ffmpeg 的中文路径编码坑
# ============================================================
param(
    [ValidateSet('full','preview')][string]$Mode = 'full',
    [int]$Workers = 4,
    [switch]$SoftwareGL
)

$ErrorActionPreference = 'Continue'
$HERE = Split-Path -Parent $MyInvocation.MyCommand.Path
$TOTAL = 75.452

# ---- 定位 export.mjs ----
$Export = $env:EXPORT
if (-not $Export) {
    $cands = @(
        (Join-Path (Split-Path -Parent $HERE) 'html-anim-export\export.mjs'),
        (Join-Path $HERE 'export.mjs'),
        'C:\Users\' + $env:USERNAME + '\html-anim-export\export.mjs'
    )
    $Export = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $Export -or -not (Test-Path $Export)) {
    Write-Host "✗ 找不到 export.mjs。请把它放在 ..\html-anim-export\ 下，或设置环境变量 EXPORT" -ForegroundColor Red
    exit 1
}

# ---- 定位 Chrome（完整版有 --headless=new，能用独显） ----
if (-not $env:CHROME) {
    $env:CHROME = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $env:CHROME) {
    Write-Host "✗ 找不到 Chrome / Edge。先跑 setup_4f.ps1" -ForegroundColor Red
    exit 1
}

# ---- 校验输入文件 ----
$Page = Join-Path $HERE 'promo.html'
$Mp3  = Join-Path $HERE 'music.mp3'
foreach ($f in @($Page, $Mp3)) {
    if (-not (Test-Path $f)) { Write-Host "✗ 缺文件: $f" -ForegroundColor Red; exit 1 }
}

# ---- 参数档位 ----
if ($Mode -eq 'preview') { $Fps = 15; $Crf = 26; $SegLen = 25; $OutName = 'wave_preview.mp4' }
else                     { $Fps = 30; $Crf = 18; $SegLen = 15; $OutName = 'wave_1080p.mp4' }

Write-Host "================ 《电波》渲染 ================" -ForegroundColor Cyan
Write-Host ("模式      : {0}  ({1}fps, CRF {2}, 每段 {3}s)" -f $Mode, $Fps, $Crf, $SegLen)
Write-Host ("Chrome    : {0}" -f $env:CHROME)
Write-Host ("export.mjs: {0}" -f $Export)
Write-Host ("并发      : {0} worker" -f $Workers)
Write-Host ("显卡      : {0}" -f $(if ($SoftwareGL) { "强制软件渲染 (SwiftShader)" } else { "自动 (优先独显)" }))
Write-Host ""

# ---- 软渲染开关（export.mjs 读这个环境变量）----
if ($SoftwareGL) { $env:SOFTWARE_GL = '1' } else { Remove-Item Env:\SOFTWARE_GL -ErrorAction SilentlyContinue }

# ---- 清理上次残留 ----
Get-ChildItem -Path $HERE -Filter '_part_*.mp4' -ErrorAction SilentlyContinue | Remove-Item -Force
Remove-Item (Join-Path $HERE '_list.txt')   -ErrorAction SilentlyContinue
Remove-Item (Join-Path $HERE '_concat.txt') -ErrorAction SilentlyContinue

# ---- 分段渲染 ----
$segs = @()
$t = 0.0; $n = 0
while ($t -lt $TOTAL) {
    $e = [math]::Min($t + $SegLen, $TOTAL)
    $segs += ,@($t, $e, "seg$n")
    $t = $e; $n++
}

$okNames = @()
$grandStart = Get-Date
foreach ($s in $segs) {
    $a = $s[0]; $b = $s[1]; $name = $s[2]
    # 关键：小数必须用不变文化格式化，否则区域设置会把 75.452 变成 75,452，node 解析出错
    $inv = [System.Globalization.CultureInfo]::InvariantCulture
    $aStr = $a.ToString('0.###', $inv)
    $bStr = $b.ToString('0.###', $inv)
    Write-Host ("──────── {0}: {1}s -> {2}s ────────" -f $name, $aStr, $bStr) -ForegroundColor Yellow
    $sw = [Diagnostics.Stopwatch]::StartNew()

    & node $Export --page $Page --mp3 $Mp3 --from $aStr --to $bStr `
        --fps $Fps --workers $Workers --crf $Crf --out (Join-Path $HERE "_part_$name.mp4")
    $code = $LASTEXITCODE
    $sw.Stop()

    if ($code -eq 0) {
        $sec = [math]::Round($sw.Elapsed.TotalSeconds, 1)
        $frames = [math]::Round(($b - $a) * $Fps)
        $rate = if ($sec -gt 0) { [math]::Round($frames / $sec, 2) } else { 0 }
        Write-Host ("✓ {0} 完成  {1}s  ({2} 帧, {3} fps)" -f $name, $sec, $frames, $rate) -ForegroundColor Green
        $okNames += $name
        Add-Content -Path (Join-Path $HERE '_list.txt') -Value "$name" -Encoding ASCII
    } else {
        Write-Host ("✗ {0} 失败 (exit {1}) —— 跳过，其余继续" -f $name, $code) -ForegroundColor Red
    }
}

# ---- 无损拼接 ----
if ($okNames.Count -eq 0) { Write-Host "✗ 没有任何分段成功" -ForegroundColor Red; exit 1 }

$concatFile = Join-Path $HERE '_concat.txt'
$lines = foreach ($nm in $okNames) { "file '_part_$nm.mp4'" }
Set-Content -Path $concatFile -Value $lines -Encoding ASCII

$Out = Join-Path $HERE $OutName
Write-Host "`n──────── 拼接 {0} 段 ────────" -ForegroundColor Yellow
& ffmpeg -y -loglevel error -f concat -safe 0 -i $concatFile -c copy -movflags +faststart $Out

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 拼接失败。分段文件还在，可手动拼：" -ForegroundColor Red
    Write-Host ("   ffmpeg -f concat -safe 0 -i `"{0}`" -c copy out.mp4" -f $concatFile)
    exit 1
}

$totalMin = [math]::Round(((Get-Date) - $grandStart).TotalMinutes, 1)
Write-Host "`n✓ 成片: $Out   （总耗时 ${totalMin} 分钟）" -ForegroundColor Green

# ---- 自检 ----
Write-Host "`n================ 成片校验 ================" -ForegroundColor Cyan
& ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,channels -of default=nw=1 $Out

Write-Host "`n分段文件保留在 _part_*.mp4（确认成片没问题后可删）：" -ForegroundColor DarkGray
Write-Host ("   Remove-Item {0}\_part_*.mp4,{0}\_list.txt,{0}\_concat.txt" -f $HERE) -ForegroundColor DarkGray
