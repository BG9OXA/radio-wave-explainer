# ============================================================
#  4F (Windows 11) 渲染环境一键安装
#  用法：右键“使用 PowerShell 运行”，或
#        powershell -ExecutionPolicy Bypass -File setup_4f.ps1
#  说明：需要管理员权限才能装软件；脚本会自己提权
# ============================================================
$ErrorActionPreference = 'Continue'

# ---- 需要管理员：没有就自己提权 ----
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "需要管理员权限，正在提权……" -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

function Show-Env {
    Write-Host "`n================ 环境检查 ================" -ForegroundColor Cyan
    $os  = (Get-CimInstance Win32_OperatingSystem).Caption
    $cpu = (Get-CimInstance Win32_Processor).Name
    $ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
    Write-Host ("OS:      {0}" -f $os)
    Write-Host ("CPU:     {0}  ({1} 核)" -f $cpu, (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors)
    Write-Host ("MEM:     {0} GB" -f $ram)
    $gpu = (Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) -join ' / '
    Write-Host ("GPU:     {0}" -f $gpu)

    $script:chromeExe = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    Write-Host ("Chrome:  {0}" -f $(if ($script:chromeExe) { $script:chromeExe } else { "缺" }))

    $script:ffmpegExe = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
    Write-Host ("ffmpeg:  {0}" -f $(if ($script:ffmpegExe) { $script:ffmpegExe } else { "缺" }))

    $script:nodeExe = (Get-Command node -ErrorAction SilentlyContinue).Source
    Write-Host ("node:    {0}" -f $(if ($script:nodeExe) { "v" + (node -v).TrimStart('v') } else { "缺" }))
}

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path","User")
}

# ---- winget 安装封装 ----
function Install-ByWinget($id, $label) {
    Write-Host "→ 安装 $label ($id)" -ForegroundColor Yellow
    winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements 2>&1 |
        Select-Object -Last 3 | ForEach-Object { Write-Host "   $_" }
    Refresh-Path
}

Show-Env

# 没有 winget（极老的 Win11 会有）就提示手装
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "`n✗ 没有 winget，请手动安装下面三个后重跑本脚本：" -ForegroundColor Red
    Write-Host "   ffmpeg  https://www.gyan.dev/ffmpeg/builds/   (解压后把 bin 加进 PATH)"
    Write-Host "   Node.js https://nodejs.org/en/download        (选 LTS msi)"
    Write-Host "   Chrome  https://www.google.com/chrome/"
    exit 1
}

Write-Host "`n================ 安装缺失项 ================" -ForegroundColor Cyan

if (-not $script:ffmpegExe) { Install-ByWinget "Gyan.FFmpeg" "ffmpeg" }
if (-not $script:nodeExe)   { Install-ByWinget "OpenJS.NodeJS.LTS" "Node.js LTS" }
if (-not $script:chromeExe) { Install-ByWinget "Google.Chrome" "Google Chrome" }

Refresh-Path
Show-Env

Write-Host @"

================ 装完，下一步 ================
1. 在容器那台机器上，把项目传过来（Windows 路径按实际改）：
     scp -r -i /opt/data/.ssh/id_ed25519_4f /opt/data/projects/wave hermes@192.168.90.32:C:/Users/hermes/
     scp -r -i /opt/data/.ssh/id_ed25519_4f /opt/data/tools/html-anim-export hermes@192.168.90.32:C:/Users/hermes/

2. 在这台 Windows 上渲染（PowerShell）：
     cd C:\Users\hermes\wave
     powershell -ExecutionPolicy Bypass -File .\render_4f.ps1

3. 拉回成片：
     scp -i /opt/data/.ssh/id_ed25519_4f hermes@192.168.90.32:C:/Users/hermes/wave/电波_1080p.mp4 /opt/data/projects/wave/

"@ -ForegroundColor Green
