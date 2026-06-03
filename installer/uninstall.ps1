$destination = "C:\Program Files\Samenvoeger"

if (Test-Path $destination) {
    Remove-Item -Path $destination -Recurse -Force
}

if (Test-Path "HKLM:\Software\Samenvoeger") {
    Remove-Item -Path "HKLM:\Software\Samenvoeger" -Recurse -Force
}
