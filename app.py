import streamlit as str
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

str.set_page_config(page_title="Transcritor Inteligente", page_icon="🎙️", layout="centered")/
str.title("🎙️ Transcritor de Vídeos e YouTube")
str.write("Cole o link do YouTube para extrair o texto ou faça upload de um arquivo.")

# Configuração da API do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Função para extrair a legenda do YouTube
def extrair_texto_youtube(url):
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    else:
        video_id = url
        
    try:
        lista_legendas = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        texto_completo = " ".join([item['text'] for item in lista_legendas])
        return texto_completo
    except Exception as e:
        raise Exception(f"Não foi possível obter as legendas deste vídeo. Erro: {e}")

url_youtube = str.text_input("🔗 Cole o link do YouTube aqui:")
arquivo_video = str.file_uploader("📂 Ou envie um arquivo do seu aparelho:", type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"])
botao_transcrever = str.button("✨ Começar Transcrição", use_container_width=True)

if botao_transcrever:
    try:
        if url_youtube:
            str.info("Extraindo o texto do YouTube...")
            texto_bruto = extrair_texto_youtube(url_youtube)
            
            str.info("Formatando o texto com Inteligência Artificial...")
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                "Você é um editor de texto profissional. Pegue a transcrição a seguir (que veio sem pontuação), organize em parágrafos lógicos, corrija erros gramaticais óbvios e pontue adequadamente para que a leitura fique natural e profissional. Não resuma, mantenha o conteúdo integral.",
                texto_bruto
            ])
            
            str.success("🎉 Concluído!")
            str.write(response.text)
            str.download_button(label="📥 Baixar Transcrição (.txt)", data=response.text, file_name="transcricao.txt", mime="text/plain")
            
        elif arquivo_video is not None:
            nome_arquivo = arquivo_video.name
            with open(nome_arquivo, "wb") as f:
                f.write(arquivo_video.getbuffer())
            
            str.info("Analisando o arquivo enviado...")
            audio_file = genai.upload_file(path=nome_arquivo)
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                "Transcreva o áudio a seguir na íntegra, organizando em parágrafos lógicos.",
                audio_file
            ])
            str.success("🎉 Concluído!")
            str.write(response.text)
            os.remove(nome_arquivo)
            
    except Exception as e:
        str.error(f"Ops: {e}")
