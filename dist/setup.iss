; Script de instalação para YT Downloader
[Setup]
; Informações básicas
AppName=YT Downloader
AppVersion=2.1
AppPublisher=Victor
AppPublisherURL=https://github.com/victorrh1/yt
DefaultDirName={pf}\YT Downloader
DefaultGroupName=YT Downloader
OutputDir=output
OutputBaseFilename=YTDownloaderSetup
Compression=lzma
SolidCompression=yes

; Atalhos
[Icons]
Name: "{autoprograms}\YT Downloader"; Filename: "{app}\YTDownloader.exe"
Name: "{autodesktop}\YT Downloader"; Filename: "{app}\YTDownloader.exe"

; Arquivos a instalar
[Files]
Source: "dist\YTDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion

; Desinstalação
[UninstallDelete]
Type: filesandordirs; Name: "{app}"
