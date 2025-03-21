import tkinter as tk
from tkinter import messagebox, ttk
from pytubefix import YouTube
import os
import subprocess
import shutil
import sys

DESTINO = r"C:\Users\Administrador\Desktop\System\Downloads YT"

def baixar_video(formato):
    url = url_entry.get()
    
    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL do YouTube!")
        return

    try:
        progresso.pack(pady=10)
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
root.title("Baixar Vídeos e Musicas do YouTube")
root.configure(bg="#f0f0f0")

largura_janela = 450
altura_janela = 350

largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()

pos_x = (largura_tela - largura_janela) // 2
pos_y = (altura_tela - altura_janela) // 2

root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(main_frame, text="Baixar MP4 ou MP3", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

tk.Label(main_frame, text="Insira a URL do vídeo:", bg="#f0f0f0", font=("Arial", 10)).pack(pady=5)
url_entry = tk.Entry(main_frame, width=50, font=("Arial", 10))
url_entry.pack(pady=5)

button_frame = tk.Frame(main_frame, bg="#f0f0f0")
button_frame.pack(pady=15)

btn_style = {"font": ("Arial", 10, "bold"), "width": 12, "height": 2, "cursor": "hand2"}

btn_mp4 = tk.Button(button_frame, text="Baixar MP4", bg="#4CAF50", fg="white", 
                   command=lambda: baixar_video("mp4"), **btn_style)
btn_mp4.pack(side=tk.LEFT, padx=10)

btn_mp3 = tk.Button(button_frame, text="Baixar MP3", bg="#2196F3", fg="white", 
                   command=lambda: baixar_video("mp3"), **btn_style)
btn_mp3.pack(side=tk.LEFT, padx=10)

progresso = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")

status_label = tk.Label(main_frame, text="", bg="#f0f0f0", font=("Arial", 9))
status_label.pack(pady=5)

root.mainloop()