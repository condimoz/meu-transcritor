import streamlit as str
import yt_dlp
import google.generativeai as genai
import os

# Configuração da página para celular
str.set_page_config(page_title="Transcritor Inteligente", page_icon="🎙️", layout="centered")

str.title("🎙️ Transcritor de Vídeos e YouTube")
str.write("Cole um link do YouTube ou faça o upload de um vídeo para obter a transcrição.")

# Configuração da API do Gemini (Pegará das configurações seguras do servidor)
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    str.error("Chave de API do Gemini não configurada nas variáveis de ambiente.")

# Função para baixar apenas o áudio do YouTube
def baixar_audio_youtube(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio_temporario.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        str.info("Baixando e processando o áudio do YouTube...")
        ydl.download([url])
    return "audio_temporario.mp3"

# --- INTERFACE DO USUÁRIO (O que aparece no celular) ---

# Opção 1: Link do YouTube
url_youtube = str.text_input("🔗 Cole o link do YouTube aqui:")

# Opção 2: Upload de arquivo local
arquivo_video = str.file_uploader("📂 Ou envie um arquivo de vídeo/áudio:", type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"])

botao_transcrever = str.button("✨ Começar Transcrição", use_container_width=True)

# Lógica de funcionamento
if botao_transcrever:
    arquivo_para_processar = None
    
    try:
        if url_youtube:
            arquivo_para_processar = baixar_audio_youtube(url_youtube)
        elif arquivo_video is not None:
            # Salva o arquivo que o usuário subiu
            arquivo_para_processar = arquivo_video.name
            with open(arquivo_para_processar, "wb") as f:
                f.write(arquivo_video.getbuffer())
        
        if arquivo_para_processar:
            str.info("Enviando áudio para a Inteligência Artificial analisar... Isso pode levar um minutinho.")
            
            # Carrega o arquivo na API do Gemini
            audio_file = genai.upload_file(path=arquivo_para_processar)
            
            # Chama o modelo para transcrever
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([
                "Você é um transcritor profissional. Transcreva o áudio a seguir na íntegra, mantendo a fidelidade das palavras, organizando em parágrafos lógicos e corrigindo apenas gagueiras ou repetições excessivas para melhorar a leitura.",
                audio_file
            ])
            
            # Exibe o resultado na tela
            str.success("🎉 Transcrição Concluída!")
            str.subheader("📝 Texto Transcrito:")
            str.write(response.text)
            
            # Botão para baixar o texto
            str.download_button(label="📥 Baixar Transcrição (.txt)", data=response.text, file_name="transcricao.txt", mime="text/plain")
            
            # Limpeza do arquivo temporário
            if os.path.exists(arquivo_para_processar):
                os.remove(arquivo_para_processar)
        else:
            str.warning("Por favor, cole um link ou envie um arquivo antes de clicar em Transcrever.")
            
    except Exception as e:
        str.error(f"Ops, ocorreu um erro: {e}")
