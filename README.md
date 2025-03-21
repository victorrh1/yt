# Baixador de Vídeos do YouTube

Um aplicativo simples para baixar vídeos do YouTube nos formatos MP4 e MP3.

## O que ele faz

- Baixa vídeos do YouTube em qualidade alta (MP4)
- Extrai e salva apenas o áudio (MP3)
- Interface gráfica fácil de usar
- Barra de progresso para acompanhar os downloads
- Tratamento adequado de nomes de arquivos

## Requisitos

- Python 3.6 ou superior
- pytubefix (versão atualizada do pytube)
- tkinter (geralmente já vem com Python)

## Como instalar

1. Clone o repositório ou baixe o arquivo Python
2. Instale as dependências:

```bash
pip install pytubefix
```

3. Execute o script:

```bash
python baixador_youtube.py
```

## Como usar

1. Cole a URL do vídeo do YouTube no campo de texto
2. Clique em "Baixar MP4" para baixar o vídeo
3. Clique em "Baixar MP3" para baixar apenas o áudio
4. Os arquivos serão salvos na pasta configurada no script

## Observações

O aplicativo salva os arquivos em `C:\Users\Administrador\Desktop\System\Downloads YT`. Para mudar o local de salvamento, edite a variável `DESTINO` no código.

Este programa usa uma abordagem simplificada que não requer ferramentas de conversão adicionais como FFMPEG ou bibliotecas de processamento de áudio.
