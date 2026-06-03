$destination = "C:\Program Files\Samenvoeger"
$source = Split-Path -Parent $MyInvocation.MyCommand.Definition

New-Item -ItemType Directory -Force -Path $destination | Out-Null

Copy-Item -Path "$source\Samenvoeger.exe" -Destination $destination -Force
Copy-Item -Path "$source\_internal" -Destination $destination -Recurse -Force

$version = if ($env:APP_VERSION) { $env:APP_VERSION } else { "unknown" }
New-Item -Path "HKLM:\Software\Samenvoeger" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\Software\Samenvoeger" -Name "Version" -Value $version
