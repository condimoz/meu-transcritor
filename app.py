import streamlit as str
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os
import time

str.set_page_config(page_title="Transcritor de Audiências", page_icon="⚖️", layout="centered")
str.title("⚖️ Transcritor e Degravador Trabalhista")
str.write("Faça o upload do vídeo da audiência ou cole o link do YouTube.")

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
        linhas_com_tempo = []
        for item in lista_legendas:
            inicio = item['start']
            minutos = int(inicio // 60)
            segundos = int(inicio % 60)
            tempo_formatado = f"[{minutos:02d}:{segundos:02d}]"
            linhas_com_tempo.append(f"{tempo_formatado} {item['text']}")
            
        return "\n".join(linhas_com_tempo)
    except Exception as e:
        raise Exception(f"Não foi possível obter as legendas automáticas deste vídeo. Erro: {e}")

url_youtube = str.text_input("🔗 Link da audiência (YouTube/PJe Mídias se houver):")
arquivo_video = str.file_uploader("📂 Enviar arquivo de vídeo da audiência:", type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"])
botao_transcrever = str.button("⚖️ Iniciar Degravação Jurídica", use_container_width=True)

if botao_transcrever:
    try:
        if url_youtube:
            str.info("Extraindo dados iniciais da mídia...")
            texto_bruto = extrair_texto_youtube(url_youtube)
            
            str.info("Formatando depoimentos em padrão jurídico...")
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                "Você é um assistente jurídico especializado em degravação de audiências trabalhistas. Pegue o texto a seguir, identifique pela dinâmica do diálogo quem é o Juiz, o Advogado e o Depoente (Reclamante/Testemunha). Formate o texto como um diálogo formal de termo de audiência, mantendo a marcação de tempo [MM:SS] no início de cada fala relevante. Corrija gagueiras e erros crassos, mas mantenha a literalidade dos fatos narrados pelo depoente para uso em peças processuais.",
                texto_bruto
            ])
            
            str.success("🎉 Degravação Concluída!")
            str.write(response.text)
            str.download_button(label="📥 Baixar Termo de Degravação (.txt)", data=response.text, file_name="degravacao_audiencia.txt", mime="text/plain")
            
        elif arquivo_video is not None:
            nome_arquivo = arquivo_video.name
            with open(nome_arquivo, "wb") as f:
                f.write(arquivo_video.getbuffer())
            
            str.info("Enviando mídia da audiência para processamento...")
            audio_file = genai.upload_file(path=nome_arquivo)
            
            str.info("Analisando depoimentos e separando vozes... Isso leva alguns segundos.")
            while audio_file.state.name == "PROCESSING":
                time.sleep(3)
                audio_file = genai.get_file(audio_file.name)
                
            if audio_file.state.name == "FAILED":
                raise Exception("Não foi possível processar este formato de vídeo.")
                
            str.info("Identificando falas e gerando ata de transcrição...")
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Comando especializado para identificar a dinâmica clássica: Juiz -> Advogado -> Depoente
            response = model.generate_content([
                "Você é um secretário de audiência focado em degravação para fins judiciais. Transcreva o áudio anexo separando estritamente as vozes dos interlocutores. Identifique quem está falando com base no contexto (ex: Juiz, Advogado do Reclamante, Advogado da Reclamada, Depoente/Testemunha). Insira a marcação de tempo exata no formato [MM:SS] toda vez que a palavra mudar de pessoa. O texto deve ser fiel para fundamentar razões finais e recursos, sem omitir respostas pertinentes.",
                audio_file
            ])
            str.success("🎉 Degravação Concluída!")
            str.write(response.text)
            str.download_button(label="📥 Baixar Termo de Degravação (.txt)", data=response.text, file_name="degravacao_audiencia.txt", mime="text/plain")
            
            os.remove(nome_arquivo)
            genai.delete_file(audio_file.name)
            
    except Exception as e:
        str.error(f"Erro no processamento: {e}")
