import streamlit as str
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

str.set_page_config(page_title="Transcritor Inteligente", page_icon="🎙️", layout="centered")
str.title("🎙️ Transcritor de Vídeos e YouTube")
str.write("Cole o link do YouTube para extrair o texto ou faça upload de um arquivo.")

# Configuração da API do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Função rápida que extrai a legenda sem baixar o vídeo inteiro
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
        raise Exception(f"Não foi possível obter as legendas automáticas deste vídeo. Erro: {e}")

url_youtube = str.text_input("🔗 Cole o link do YouTube aqui:")
arquivo_video = str.file_uploader("📂 Ou envie um arquivo do seu aparelho:", type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"])
botao_transcrever = str.button("✨ Começar Transcrição", use_container_width=True)

if botao_transcrever:
    try:
        if url_youtube:
            str.info("Extraindo o texto do YouTube...")
            texto_bruto = extrair_texto_youtube(url_youtube)
            
            str.info("Formatando o texto com Inteligência Artificial...")
            
            # FORÇA O SISTEMA A USAR O MODELO ATUALIZADO DIRETAMENTE
            response = genai.generate_text(
                model="models/text-embedding-004", # Apenas para garantir a rota estável
                prompt="Ignorar"
            )
            
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
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
            
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content([
                "Transcreva o áudio a seguir na íntegra, organizando em parágrafos lógicos.",
                audio_file
            ])
            str.success("🎉 Concluído!")
            str.write(response.text)
            os.remove(nome_arquivo)
            
    except Exception as e:
        # Se a biblioteca ainda teimar com a versão v1beta, usamos a chamada direta via API simplificada:
        try:
            if url_youtube and 'texto_bruto' in locals():
                model_antigo = genai.GenerativeModel('gemini-pro')
                response = model_antigo.generate_content(["Organize e pontue este texto:", texto_bruto])
                str.success("🎉 Concluído (Rota alternativa)!")
                str.write(response.text)
            else:
                str.error(f"Ops: {e}")
        except Exception as erro_fatal:
            str.error(f"Erro de comunicação com o Google: {erro_fatal}")
