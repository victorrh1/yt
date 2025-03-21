import tkinter as tk
from tkinter import messagebox, ttk
from pytubefix import YouTube
import os
import sys

DARK_BG = "#1E1E1E"
DARKER_BG = "#252526"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#007ACC"
SUCCESS_COLOR = "#6A9955"
ENTRY_BG = "#2D2D30"
BORDER_COLOR = "#3E3E42"

DESTINO = r"C:\Users\Administrador\Desktop\System\Downloads YT"

def baixar_video(formato):
    url = url_entry.get()
    
    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL do YouTube!")
        return

    try:
        progresso.pack(pady=15)
        progresso["value"] = 0
        status_label.config(text="Iniciando download...")
        root.update()
        
        yt = YouTube(url)
        titulo = yt.title
        titulo_seguro = "".join([c for c in titulo if c.isalnum() or c in " -_"]).strip()
        status_label.config(text=f"Baixando: {titulo_seguro[:30]}...")
        root.update()
        
        if formato == "mp4":
            stream = yt.streams.get_highest_resolution()
            arquivo_saida = os.path.join(DESTINO, f"{titulo_seguro}.mp4")
        else:
            stream = yt.streams.filter(only_audio=True).first()
            arquivo_saida = os.path.join(DESTINO, f"{titulo_seguro}.mp3")
        
        progresso["value"] = 30
        root.update()
        
        if formato == "mp4":
            arquivo_baixado = stream.download(DESTINO, filename=f"{titulo_seguro}.mp4")
        else:
            temp_file = os.path.join(DESTINO, f"{titulo_seguro}.tmp")
            arquivo_baixado = stream.download(DESTINO, filename=f"{titulo_seguro}.tmp")
        
        progresso["value"] = 70
        root.update()

        if formato == "mp3":
            status_label.config(text="Convertendo para MP3...")
            root.update()
            mp3_path = os.path.join(DESTINO, f"{titulo_seguro}.mp3")
            
            try:
                if os.path.exists(mp3_path):
                    os.remove(mp3_path)
                os.rename(arquivo_baixado, mp3_path)
                arquivo_baixado = mp3_path
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível finalizar o arquivo MP3: {e}")

        progresso["value"] = 100
        status_label.config(text="Download concluído!")
        root.update()
        messagebox.showinfo("Sucesso", f"Download concluído como {formato.upper()}!")
        
        progresso.pack_forget()
        status_label.config(text="")
    
    except Exception as e:
        progresso.pack_forget()
        status_label.config(text="")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

root = tk.Tk()
root.title("Baixador de Vídeos do YouTube")
root.configure(bg=DARK_BG)

style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", 
                thickness=20, 
                troughcolor=DARKER_BG,
                background=ACCENT_COLOR)

largura_janela = 500
altura_janela = 450

largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()

pos_x = (largura_tela - largura_janela) // 2
pos_y = (altura_tela - altura_janela) // 2

root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

outer_frame = tk.Frame(root, bg=DARK_BG, pady=2, padx=2)
outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

main_frame = tk.Frame(outer_frame, bg=DARKER_BG, padx=25, pady=25, 
                      highlightbackground=BORDER_COLOR, highlightthickness=1)
main_frame.pack(fill=tk.BOTH, expand=True)

title_frame = tk.Frame(main_frame, bg=DARKER_BG)
title_frame.pack(pady=10)

logo_label = tk.Label(title_frame, text="📥", font=("Arial", 24), bg=DARKER_BG, fg=TEXT_COLOR)
logo_label.pack(side=tk.LEFT, padx=(0, 10))

title_label = tk.Label(title_frame, text="Baixar MP4 ou MP3", 
                      font=("Arial", 18, "bold"), bg=DARKER_BG, fg=TEXT_COLOR)
title_label.pack(side=tk.LEFT)

subtitle_label = tk.Label(main_frame, text= "Baixe vídeos e músicas do YouTube", 
                         font=("Arial", 10), bg=DARKER_BG, fg=TEXT_COLOR)
subtitle_label.pack(pady=(0, 15))

url_frame = tk.Frame(main_frame, bg=DARKER_BG)
url_frame.pack(fill=tk.X, pady=5)

url_icon = tk.Label(url_frame, text="🔗", font=("Arial", 12), bg=DARKER_BG, fg=TEXT_COLOR)
url_icon.pack(side=tk.LEFT, padx=(0, 5))

tk.Label(url_frame, text="URL do vídeo:", bg=DARKER_BG, fg=TEXT_COLOR, 
        font=("Arial", 10, "bold")).pack(side=tk.LEFT)

entry_frame = tk.Frame(main_frame, bg=BORDER_COLOR, padx=1, pady=1)
entry_frame.pack(fill=tk.X, pady=10)

url_entry = tk.Entry(entry_frame, width=50, font=("Arial", 10), 
                    bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
url_entry.pack(fill=tk.X, ipady=5, padx=1, pady=1)

button_frame = tk.Frame(main_frame, bg=DARKER_BG)
button_frame.pack(pady=20)

def on_enter(e, btn, color):
    btn['background'] = color

def on_leave(e, btn, color):
    btn['background'] = color

mp4_frame = tk.Frame(button_frame, bg=DARKER_BG, padx=2, pady=2)
mp4_frame.pack(side=tk.LEFT, padx=10)

btn_mp4 = tk.Button(mp4_frame, text=" 📹 Baixar MP4", bg=SUCCESS_COLOR, fg=TEXT_COLOR, 
                   font=("Arial", 10, "bold"), width=15, height=2, cursor="hand2",
                   command=lambda: baixar_video("mp4"), relief=tk.FLAT)
btn_mp4.pack()
btn_mp4.bind("<Enter>", lambda e: on_enter(e, btn_mp4, "#7AB96C"))
btn_mp4.bind("<Leave>", lambda e: on_leave(e, btn_mp4, SUCCESS_COLOR))

mp3_frame = tk.Frame(button_frame, bg=DARKER_BG, padx=2, pady=2)
mp3_frame.pack(side=tk.LEFT, padx=10)

btn_mp3 = tk.Button(mp3_frame, text=" 🎵 Baixar MP3", bg=ACCENT_COLOR, fg=TEXT_COLOR, 
                   font=("Arial", 10, "bold"), width=15, height=2, cursor="hand2",
                   command=lambda: baixar_video("mp3"), relief=tk.FLAT)
btn_mp3.pack()
btn_mp3.bind("<Enter>", lambda e: on_enter(e, btn_mp3, "#1A8FE3"))
btn_mp3.bind("<Leave>", lambda e: on_leave(e, btn_mp3, ACCENT_COLOR))

progresso = ttk.Progressbar(main_frame, orient="horizontal", length=450, mode="determinate", style="TProgressbar")

status_label = tk.Label(main_frame, text="", bg=DARKER_BG, fg=TEXT_COLOR, font=("Arial", 9))
status_label.pack(pady=5)

footer_label = tk.Label(main_frame, text="© 2025 - Desenvolvido com ❤", 
                      font=("Arial", 8), bg=DARKER_BG, fg="#888888")
footer_label.pack(side=tk.BOTTOM, pady=(15, 0))

try:
    clipboard_text = root.clipboard_get()
    if "youtube.com/watch" in clipboard_text or "youtu.be/" in clipboard_text:
        url_entry.insert(0, clipboard_text)
except:
    pass

root.mainloop()