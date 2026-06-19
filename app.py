import streamlit as str
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os
import time

str.set_page_config(page_title="Transcritor de Audiências", page_icon="⚖️", layout="centered")
str.title("⚖️ Transcritor Jurídico e WhatsApp")
str.write("Insira mídias de audiências judiciais ou áudios do WhatsApp.")

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

url_youtube = str.text_input("🔗 Link da audiência (YouTube se houver):")

arquivo_video = str.file_uploader(
    "📂 Enviar arquivo (Vídeo de Audiência ou Áudio .ogg do WhatsApp):", 
    type=["mp4", "mkv", "mov", "mp3", "wav", "m4a", "ogg"]
)

botao_transcrever = str.button("⚖️ Iniciar Degravação Inteligente", use_container_width=True)

if botao_transcrever:
    try:
        if url_youtube:
            str.info("Extraindo dados iniciais da mídia...")
            texto_bruto = extrair_texto_youtube(url_youtube)
            
            str.info("Formatando depoimentos em padrão jurídico...")
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                "Você é um assistente jurídico de alto nível, especialista em degravações e audiências trabalhistas. Pegue o texto a seguir, identifique pela dinâmica do diálogo quem é o Juiz, o Advogado e o Depoente (Reclamante/Testemunha). Formate o texto como um diálogo formal de termo de audiência, mantendo a marcação de tempo [MM:SS] no início de cada fala relevante. Corrija gagueiras e erros crassos, mas mantém a literalidade dos fatos narrados pelo depoente para uso em peças processuais.",
                texto_bruto
            ])
            
            str.success("🎉 Degravação Concluída!")
            str.write(response.text)
            str.download_button(label="📥 Baixar Termo de Degravação (.txt)", data=response.text, file_name="degravacao_audiencia.txt", mime="text/plain")
            
        elif arquivo_video is not None:
            # CORREÇÃO AQUI: Remove os espaços em branco do nome do arquivo para não quebrar o sistema
            nome_original = arquivo_video.name
            nome_arquivo = nome_original.replace(" ", "_")
            extensao = os.path.splitext(nome_arquivo)[1].lower()
            
            # IDENTIFICAÇÃO AUTOMÁTICA DO TIPO DE ARQUIVO
            if extensao == '.ogg':
                tipo_midia = "WHATSAPP"
                prompt_juridico = (
                    "Você é um assistente jurídico especialista em degravação de provas e mídias sociais. "
                    "O arquivo anexo é uma mensagem de voz do WhatsApp que será usada como prova em um processo jurídico. "
                    "Sua missão é transcrever o áudio na íntegra, organizando o texto em parágrafos lógicos e fluidos. "
                    "Pontue corretamente e corrija erros de fala/gagueiras para que a leitura fique limpa e inteligível. "
                    "ATENÇÃO: Não resuma e não mude NENHUMA palavra importante. Mantenha a literalidade exata do que foi dito pelo interlocutor, "
                    "pois o texto servirá de transcrição oficial de prova em petição.\n\n"
                    "Siga este modelo de saída:\n"
                    "[TRANSCRIÇÃO DA MENSAGEM DE ÁUDIO DO WHATSAPP]\n"
                    "\"Texto formatado aqui...\""
                )
            else:
                tipo_midia = "AUDIENCIA"
                prompt_juridico = (
                    "Você é um secretário de audiência focado em degravação para fins judiciais. Transcreva o áudio anexo separando estritamente as vozes dos interlocutores. "
                    "Identifique quem está falando com base no contexto (ex: Juiz, Advogado do Reclamante, Advogado da Reclamada, Depoente/Testemunha). "
                    "Insira a marcação de tempo exata no formato [MM:SS] toda vez que a palavra mudar de pessoa. "
                    "O texto deve ser fiel para fundamentar razões finais e recursos, sem omitir respostas pertinentes."
                )
            
            str.info(f"📱 Enviando mídia de {tipo_midia} para o servidor do Google...")
            
            # Salva usando o nome limpo (sem espaços)
            with open(nome_arquivo, "wb") as f:
                f.write(arquivo_video.getbuffer())
                
            audio_file = genai.upload_file(path=nome_arquivo)
            
            str.info("Analisando o áudio... Isso leva alguns segundos.")
            while audio_file.state.name == "PROCESSING":
                time.sleep(3)
                audio_file = genai.get_file(audio_file.name)
                
            if audio_file.state.name == "FAILED":
                raise Exception("Não foi possível processar este formato de arquivo.")
                
            str.info("Processando a transcrição e aplicando formatação jurídica...")
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            response = model.generate_content([prompt_juridico, audio_file])
            
            str.success("🎉 Processo Concluído!")
            str.write(response.text)
            
            nome_baixar = f"degravacao_{tipo_midia.lower()}.txt"
            str.download_button(label="📥 Baixar Transcrição (.txt)", data=response.text, file_name=nome_baixar, mime="text/plain")
            
            os.remove(nome_arquivo)
            genai.delete_file(audio_file.name)
            
    except Exception as e:
        str.error(f"Erro no processamento: {e}")
