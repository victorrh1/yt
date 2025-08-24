from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox, ttk
import yt_dlp
import os
import sys
import threading
import subprocess
import re

DARK_BG = "#1E1E1E"
DARKER_BG = "#252526"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#007ACC"
SUCCESS_COLOR = "#6A9955"
ENTRY_BG = "#2D2D30"
BORDER_COLOR = "#3E3E42"

def verificar_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def validar_url(url):
    if "playlist" in url or "list=" in url:
        return "playlist"
    elif "youtube.com/watch" in url or "youtu.be/" in url:
        return "video"
    else:
        return None

def extrair_id_playlist(url):
    """Extrai o ID da playlist da URL"""
    padroes = [
        r'[&?]list=([^&]+)',
        r'youtube\.com/playlist\?list=([^&]+)',
        r'youtube\.com/watch\?.*list=([^&]+)'
    ]
    
    for padrao in padroes:
        match = re.search(padrao, url)
        if match:
            return match.group(1)
    return None

def baixar_video_individual(url, formato, DESTINO, atualizar_status=None):
    try:
        if atualizar_status:
            atualizar_status(10, "Obtendo informações do vídeo...")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join(DESTINO, '%(title)s.%(ext)s'),
            'progress_hooks': [],
        }
        
        if formato == "mp3":
            if not verificar_ffmpeg():
                messagebox.showwarning("FFmpeg não encontrado", "Instale o FFmpeg para converter para MP3. Baixando áudio no formato original.")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if not verificar_ffmpeg():
                messagebox.showwarning("FFmpeg não encontrado", "Baixando em qualidade progressiva (até 720p) avec áudio embutido.")
                ydl_opts.update({
                    'format': 'best[ext=mp4]',
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = int(float(d['_percent_str'].strip('%')))
                    if percent > 70:
                        percent = 70
                    if atualizar_status:
                        atualizar_status(percent, f"Baixando... {percent}%")
                except:
                    pass
            elif d['status'] == 'finished':
                if atualizar_status:
                    atualizar_status(75, "Processando arquivo...")
        
        ydl_opts['progress_hooks'].append(progress_hook)
        
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            titulo = info.get('title', 'Video')
            titulo_seguro = "".join([c for c in titulo if c.isalnum() or c in " -_"]).strip()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        for i in range(75, 100):
            if atualizar_status:
                atualizar_status(i, f"Finalizando... {i}%")
            import time
            time.sleep(0.02)
        
        if atualizar_status:
            atualizar_status(100, "Concluído! 100%")
        
        return True, titulo_seguro
    except Exception as e:
        return False, str(e)

def baixar_video_thread(url, formato, DESTINO, video_index=None, total_videos=None):
    def atualizar_status(percent, text):
        root.after(0, lambda: atualizar_barra_progresso(percent, text, video_index, total_videos))
    
    success, msg = baixar_video_individual(url, formato, DESTINO, atualizar_status)
    
    if success:
        if video_index is not None and total_videos is not None:
            root.after(0, lambda: status_label.config(text=f"Vídeo {video_index+1}/{total_videos} concluído: {msg}"))
        else:
            root.after(0, lambda: messagebox.showinfo("Sucesso", f"Download concluído como {formato.upper()}!"))
        root.after(0, lambda: progresso.pack_forget())
        root.after(0, lambda: status_label.config(text=""))
    else:
        root.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro: {msg}"))
        root.after(0, lambda: progresso.pack_forget())
        root.after(0, lambda: status_label.config(text=""))

def atualizar_barra_progresso(percent, text, video_index=None, total_videos=None):
    progresso["value"] = percent
    if video_index is not None and total_videos is not None:
        status_text = f"Vídeo {video_index+1}/{total_videos}: {text}"
    else:
        status_text = text
    status_label.config(text=status_text)
    root.update()

def baixar_video(formato):
    DESTINO = destino_entry.get().strip()
    if not DESTINO:
        messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino!")
        return
    
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL do YouTube!")
        return
    
    url_tipo = validar_url(url)
    if url_tipo == "video":
        progresso.pack(pady=15)
        progresso["value"] = 0
        status_label.config(text="Iniciando download...")
        root.update()
        threading.Thread(target=baixar_video_thread, args=(url, formato, DESTINO), daemon=True).start()
    elif url_tipo == "playlist":
        mostrar_janela_playlist(url, formato, DESTINO)
    else:
        messagebox.showerror("Erro", "URL inválida! Por favor, insira uma URL válida do YouTube.")

def mostrar_janela_playlist(url, formato, destino):
    try:
        playlist_window = tk.Toplevel(root)
        playlist_window.title("Selecionar Vídeos da Playlist")
        playlist_window.configure(bg=DARK_BG)
        
        largura_janela = 600
        altura_janela = 580
        largura_tela = playlist_window.winfo_screenwidth()
        altura_tela = playlist_window.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        playlist_window.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
        
        main_frame = tk.Frame(playlist_window, bg=DARKER_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = tk.Label(main_frame, text="Selecionar Vídeos da Playlist", font=("Arial", 14, "bold"), bg=DARKER_BG, fg=TEXT_COLOR)
        title_label.pack(pady=(0, 10))
        
        loading_label = tk.Label(main_frame, text="Carregando playlist...", font=("Arial", 10), bg=DARKER_BG, fg=TEXT_COLOR)
        loading_label.pack(pady=10)
        playlist_window.update()
        
        try:
            playlist_id = extrair_id_playlist(url)
            if not playlist_id:
                raise Exception("Não foi possível extrair o ID da playlist da URL.")
            
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                
                playlist_info = ydl.extract_info(url, download=False)
                
                if not playlist_info or 'entries' not in playlist_info:
                    
                    try:
                        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                        playlist_info = ydl.extract_info(playlist_url, download=False)
                    except:
                        raise Exception("Não foi possível acessar a playlist.")
                
                if not playlist_info or 'entries' not in playlist_info:
                    raise Exception("Nenhum vídeo encontrado na playlist ou playlist privada.")
                
                videos = []
                playlist_title = playlist_info.get('title', 'Playlist do YouTube')
                
                # Processar cada entrada da playlist
                for i, entry in enumerate(playlist_info['entries']):
                    if entry:
                        # Obter URL do vídeo de diferentes maneiras
                        video_url = None
                        
                        if 'url' in entry and entry['url']:
                            video_url = entry['url']
                        elif 'id' in entry and entry['id']:
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        elif 'webpage_url' in entry and entry['webpage_url']:
                            video_url = entry['webpage_url']
                        
                        # Obter título do vídeo
                        title = entry.get('title', f"Vídeo {i+1}")
                        
                        if video_url:
                            videos.append((title, video_url))
                
                if not videos:
                    raise Exception("Nenhum vídeo válido encontrado na playlist.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a playlist: {e}")
            playlist_window.destroy()
            return
        
        loading_label.destroy()
        
        if playlist_title:
            playlist_name = tk.Label(main_frame, text=f"Playlist: {playlist_title}", font=("Arial", 12), bg=DARKER_BG, fg=ACCENT_COLOR)
            playlist_name.pack(pady=(0, 10))
        
        video_count = tk.Label(main_frame, text=f"Total de vídeos: {len(videos)}", font=("Arial", 10), bg=DARKER_BG, fg=TEXT_COLOR)
        video_count.pack(pady=(0, 10))
        
        canvas_frame = tk.Frame(main_frame, bg=DARKER_BG)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg=ENTRY_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        checkbox_frame = tk.Frame(canvas, bg=ENTRY_BG)
        canvas.create_window((0, 0), window=checkbox_frame, anchor=tk.NW)
        
        video_vars = []
        for i, (title, video_url) in enumerate(videos):
            try:
                var = tk.BooleanVar(value=True)
                check_frame = tk.Frame(checkbox_frame, bg=ENTRY_BG)
                check_frame.pack(fill=tk.X, padx=5, pady=2)
                
                checkbox = tk.Checkbutton(check_frame, variable=var, bg=ENTRY_BG, fg=TEXT_COLOR, activebackground=ENTRY_BG, selectcolor=DARKER_BG)
                checkbox.pack(side=tk.LEFT)
                
                label_text = f"{i+1}. {title}"
                video_label = tk.Label(check_frame, text=label_text, bg=ENTRY_BG, fg=TEXT_COLOR, anchor=tk.W, padx=5, wraplength=500)
                video_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                video_vars.append((var, video_url, title))
            except Exception as e:
                print(f"Erro ao adicionar vídeo: {e}")
        
        checkbox_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        
        select_frame = tk.Frame(main_frame, bg=DARKER_BG)
        select_frame.pack(fill=tk.X, pady=10)
        
        def select_all():
            for var, _, _ in video_vars:
                var.set(True)
        
        def deselect_all():
            for var, _, _ in video_vars:
                var.set(False)
        
        select_all_btn = tk.Button(select_frame, text="Marcar Todos", bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 9), width=15, command=select_all)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = tk.Button(select_frame, text="Desmarcar Todos", bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 9), width=15, command=deselect_all)
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        button_frame = tk.Frame(main_frame, bg=DARKER_BG)
        button_frame.pack(fill=tk.X, pady=10)
        
        def baixar_selecionados():
            selected_videos = []
            for i, (var, url, title) in enumerate(video_vars):
                if var.get() and url:
                    selected_videos.append((i, url, title))
            
            if not selected_videos:
                messagebox.showerror("Erro", "Nenhum vídeo selecionado!")
                return
            
            playlist_window.destroy()
            baixar_playlist_selecionada(selected_videos, formato, destino)
        
        baixar_btn = tk.Button(button_frame, text=f"Baixar {formato.upper()}", bg=SUCCESS_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold"), width=15, command=baixar_selecionados)
        baixar_btn.pack(side=tk.LEFT, padx=5)
        
        cancelar_btn = tk.Button(button_frame, text="Cancelar", bg=BORDER_COLOR, fg=TEXT_COLOR, font=("Arial", 10), width=15, command=playlist_window.destroy)
        cancelar_btn.pack(side=tk.RIGHT, padx=5)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def baixar_playlist_selecionada(selected_videos, formato, destino):
    progresso.pack(pady=15)
    progresso["value"] = 0
    status_label.config(text=f"Preparando para baixar {len(selected_videos)} vídeos...")
    root.update()
    
    threading.Thread(target=baixar_videos_sequenciais, args=(selected_videos, formato, destino), daemon=True).start()

def baixar_videos_sequenciais(selected_videos, formato, destino):
    total_videos = len(selected_videos)
    videos_baixados = 0
    videos_com_erro = 0
    
    for i, (video_index, url, title) in enumerate(selected_videos):
        root.after(0, lambda idx=i, ttl=title: status_label.config(text=f"Iniciando vídeo {idx+1}/{total_videos}: {ttl[:30]}..."))
        root.after(0, lambda: progresso.config(value=0))
        root.update()
        
        def atualizar_status(percent, text):
            root.after(0, lambda: atualizar_barra_progresso(percent, text, i, total_videos))
        
        success, msg = baixar_video_individual(url, formato, destino, atualizar_status)
        
        if success:
            videos_baixados += 1
        else:
            videos_com_erro += 1
    
    root.after(0, lambda: status_label.config(text="Download concluído!"))
    root.after(0, lambda: progresso.config(value=100))
    root.after(0, lambda: messagebox.showinfo("Download Concluído", f"Playlist baixada com sucesso!\n\n"
                                          f"Total de vídeos: {total_videos}\n"
                                          f"Baixados com sucesso: {videos_baixados}\n"
                                          f"Erros: {videos_com_erro}"))
    root.after(0, lambda: progresso.pack_forget())
    root.after(0, lambda: status_label.config(text=""))

root = tk.Tk()
root.title("Baixador de Vídeos do YouTube")
root.configure(bg=DARK_BG)

style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", thickness=20, troughcolor=DARKER_BG, background=ACCENT_COLOR)

largura_janela = 500
altura_janela = 487
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
pos_x = (largura_tela - largura_janela) // 2
pos_y = (altura_tela - altura_janela) // 2
root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

outer_frame = tk.Frame(root, bg=DARK_BG, pady=2, padx=2)
outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

main_frame = tk.Frame(outer_frame, bg=DARKER_BG, padx=25, pady=25, highlightbackground=BORDER_COLOR, highlightthickness=1)
main_frame.pack(fill=tk.BOTH, expand=True)

title_frame = tk.Frame(main_frame, bg=DARKER_BG)
title_frame.pack(pady=10)

logo_label = tk.Label(title_frame, text="📥", font=("Arial", 24), bg=DARKER_BG, fg=TEXT_COLOR)
logo_label.pack(side=tk.LEFT, padx=(0, 10))

title_label = tk.Label(title_frame, text="Baixar MP4 ou MP3", font=("Arial", 18, "bold"), bg=DARKER_BG, fg=TEXT_COLOR)
title_label.pack(side=tk.LEFT)

subtitle_label = tk.Label(main_frame, text=
    "Baixe vídeos e playlists do YouTube", font=("Arial", 10), bg=DARKER_BG, fg=TEXT_COLOR)
subtitle_label.pack(pady=(0, 15))

url_frame = tk.Frame(main_frame, bg=DARKER_BG)
url_frame.pack(fill=tk.X, pady=5)

url_icon = tk.Label(url_frame, text="🔗", font=("Arial", 12), bg=DARKER_BG, fg=TEXT_COLOR)
url_icon.pack(side=tk.LEFT, padx=(0, 5))

tk.Label(url_frame, text="URL do vídeo ou playlist:", bg=DARKER_BG, fg=TEXT_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

entry_frame = tk.Frame(main_frame, bg=BORDER_COLOR, padx=1, pady=1)
entry_frame.pack(fill=tk.X, pady=10)

url_entry = tk.Entry(entry_frame, width=50, font=("Arial", 10), bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
url_entry.pack(fill=tk.X, ipady=5, padx=1, pady=1)

def copiar():
    url_entry.event_generate("<<Copy>>")

def colar():
    url_entry.event_generate("<<Paste>>")

def mostrar_menu_contexto(event):
    menu_contexto.tk_popup(event.x_root, event.y_root)

menu_contexto = tk.Menu(root, tearoff=0)
menu_contexto.add_command(label="Copiar", command=copiar)
menu_contexto.add_command(label="Colar", command=colar)

url_entry.bind("<Button-3>", mostrar_menu_contexto)

button_frame = tk.Frame(main_frame, bg=DARKER_BG)
button_frame.pack(pady=20)

def on_enter(e, btn, color):
    btn['background'] = color

def on_leave(e, btn, color):
    btn['background'] = color

mp4_frame = tk.Frame(button_frame, bg=DARKER_BG, padx=2, pady=2)
mp4_frame.pack(side=tk.LEFT, padx=10)

destino_frame = tk.Frame(main_frame, bg=DARKER_BG)
destino_frame.pack(fill=tk.X, pady=5)

tk.Label(destino_frame, text="Pasta de destino:", bg=DARKER_BG, fg=TEXT_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))

destino_entry = tk.Entry(destino_frame, width=40, font=("Arial", 10), bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
destino_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

def selecionar_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        destino_entry.delete(0, tk.END)
        destino_entry.insert(0, pasta)

btn_pasta = tk.Button(destino_frame, text="📂", bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 9, "bold"), cursor="hand2", command=selecionar_pasta, relief=tk.FLAT)
btn_pasta.pack(side=tk.RIGHT)

btn_mp4 = tk.Button(mp4_frame, text=" 📹 Baixar MP4", bg=SUCCESS_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold"), width=15, height=2, cursor="hand2", command=lambda: baixar_video("mp4"), relief=tk.FLAT)
btn_mp4.pack()
btn_mp4.bind("<Enter>", lambda e: on_enter(e, btn_mp4, "#7AB96C"))
btn_mp4.bind("<Leave>", lambda e: on_leave(e, btn_mp4, SUCCESS_COLOR))

mp3_frame = tk.Frame(button_frame, bg=DARKER_BG, padx=2, pady=2)
mp3_frame.pack(side=tk.LEFT, padx=10)

btn_mp3 = tk.Button(mp3_frame, text=" 🎵 Baixar MP3", bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold"), width=15, height=2, cursor="hand2", command=lambda: baixar_video("mp3"), relief=tk.FLAT)
btn_mp3.pack()
btn_mp3.bind("<Enter>", lambda e: on_enter(e, btn_mp3, "#1A8FE3"))
btn_mp3.bind("<Leave>", lambda e: on_leave(e, btn_mp3, ACCENT_COLOR))

progresso = ttk.Progressbar(main_frame, orient="horizontal", length=450, mode="determinate", style="TProgressbar", maximum=100)

status_label = tk.Label(main_frame, text="", bg=DARKER_BG, fg=TEXT_COLOR, font=("Arial", 9))
status_label.pack(pady=5)

footer_label = tk.Label(main_frame, text="© 2025 - Desenvolvido com ❤", font=("Arial", 8), bg=DARKER_BG, fg="#888888")
footer_label.pack(side=tk.BOTTOM, pady=(15, 0))

try:
    clipboard_text = root.clipboard_get()
    if clipboard_text and ("youtube.com/watch" in clipboard_text or "youtu.be/" in clipboard_text or "youtube.com/playlist" in clipboard_text) and len(clipboard_text) < 500:
        url_entry.insert(0, clipboard_text)
    else:
        url_entry.delete(0, tk.END)
except tk.TclError:
    pass

root.mainloop()