import streamlit as str
import yt_dlp
import google.generativeai as genai
import os

# Configuração da página para celular
str.set_page_config(page_title="Transcritor Inteligente", page_icon="🎙️", layout="centered")

str.title("🎙️ Transcritor de Vídeos e YouTube")
str.write("Cole um link do YouTube ou faça o upload de um vídeo para obter a transcrição.")

# Configuração da API do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    str.error("Chave de API do Gemini não configurada nas variáveis de ambiente.")

# Função atualizada para burlar o bloqueio do YouTube (Erro 403)
def baixar_audio_youtube(url):
    ydl_opts = {
        'format': 'ba/b',  # Escolhe o melhor áudio disponível rapidamente
        'outtmpl': 'audio_temporario.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128', # Reduzido para processar mais rápido no servidor
        }],
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        str.info("Conectando ao YouTube e baixando o áudio...")
        ydl.download([url])
    return "audio_temporario.mp3"

# --- INTERFACE DO USUÁRIO ---

# Opção 1: Link do YouTube
url_youtube = str.text_input("🔗 Cole o link do YouTube aqui:")

# Opção 2: Upload de arquivo local
arquivo_video = str.file_uploader("📂 Ou envie um arquivo de vídeo/áudio do seu aparelho:", type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"])

botao_transcrever = str.button("✨ Começar Transcrição", use_container_width=True)

# Lógica de funcionamento
if botao_transcrever:
    arquivo_para_processar = None
    
    try:
        if url_youtube:
            arquivo_para_processar = baixar_audio_youtube(url_youtube)
        elif arquivo_video is not None:
            arquivo_para_processar = arquivo_video.name
            with open(arquivo_para_processar, "wb") as f:
                f.write(arquivo_video.getbuffer())
        
        if arquivo_para_processar and os.path.exists(arquivo_para_processar):
            str.info("Enviando áudio para a Inteligência Artificial... Isso pode levar um minutinho dependendo do tamanho.")
            
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
            os.remove(arquivo_para_processar)
        else:
            str.error("Não foi possível gerar ou encontrar o arquivo de áudio para processamento. Certifique-se de que o link é válido.")
            
    except Exception as e:
        str.error(f"Ops, ocorreu um erro: {e}")
