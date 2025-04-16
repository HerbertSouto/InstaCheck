
import streamlit as st
import instaloader
import pandas as pd
import requests
import re

def calcular_alcance(formato, audiencia):
    if not audiencia:
        return 0
    if formato == "INSTAGRAM REELS":
        return audiencia * (0.2168 if audiencia <= 100_000 else 0.121 if audiencia <= 2_000_000 else 0.0709 if audiencia <= 5_000_000 else 0.0549 if audiencia <= 10_000_000 else 0.068)
    elif formato == "INSTAGRAM FEED":
        return audiencia * (0.1462 if audiencia <= 100_000 else 0.1015 if audiencia <= 2_000_000 else 0.0702 if audiencia <= 5_000_000 else 0.0875 if audiencia <= 10_000_000 else 0.0771)
    elif formato == "VÍDEO NO TIKTOK":
        return audiencia * (0.0369 if audiencia <= 100_000 else 0.0163 if audiencia <= 2_000_000 else 0.0204 if audiencia <= 5_000_000 else 0.0216 if audiencia <= 10_000_000 else 0.0123)
    return 0

def calcular_impressoes_feed(formato, audiencia):
    if not audiencia:
        return 0
    if formato == "INSTAGRAM REELS":
        return audiencia * (0.2421 if audiencia <= 100_000 else 0.1383 if audiencia <= 2_000_000 else 0.0735 if audiencia <= 5_000_000 else 0.0557 if audiencia <= 10_000_000 else 0.0702)
    elif formato == "INSTAGRAM FEED":
        return audiencia * (0.1588 if audiencia <= 100_000 else 0.1015 if audiencia <= 2_000_000 else 0.0736 if audiencia <= 5_000_000 else 0.0919 if audiencia <= 10_000_000 else 0.0863)
    elif formato == "VÍDEO NO TIKTOK":
        return audiencia * (0.04 if audiencia <= 100_000 else 0.02 if audiencia <= 2_000_000 else 0.0221 if audiencia <= 5_000_000 else 0.0276 if audiencia <= 10_000_000 else 0.0158)
    return 0

def calcular_alcance_stories(audiencia):
    if not audiencia: return 0
    return audiencia * (0.0279 if audiencia <= 100_000 else 0.023 if audiencia <= 2_000_000 else 0.0155 if audiencia <= 5_000_000 else 0.0131 if audiencia <= 10_000_000 else 0.018)

def calcular_impressoes_stories(audiencia):
    if not audiencia: return 0
    return audiencia * (0.0285 if audiencia <= 100_000 else 0.0238 if audiencia <= 2_000_000 else 0.0158 if audiencia <= 5_000_000 else 0.0131 if audiencia <= 10_000_000 else 0.0184)

def get_instagram_followers(username):
    loader = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(loader.context, username.strip().replace("@", ""))
        return profile.followers
    except Exception as e:
        st.error(f"Erro ao buscar perfil do Instagram: {e}")
        return None

def get_tiktok_followers(username):
    url = f"https://www.tiktok.com/@{username}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            match = re.search(r'"followerCount":(\d+)', response.text)
            if match:
                return int(match.group(1))
        return None
    except Exception as e:
        st.error(f"Erro ao buscar perfil do TikTok: {e}")
        return None

if "registros" not in st.session_state:
    st.session_state.registros = []

st.title("📱 Estimador de Alcance de Influenciadores")

rede = st.selectbox("Rede:", ["INSTAGRAM", "TIKTOK", "TWITTER", "YOUTUBE"])
formatos = st.multiselect("Formato(s):", ["INSTAGRAM REELS", "INSTAGRAM FEED", "VÍDEO NO TIKTOK", "TWITTER", "YOUTUBE"])
username = st.text_input("Nome do influenciador (ex: @exemplo)")

quantidade_feeds_dict = {}
quantidade_stories_dict = {}

if formatos:
    st.markdown("### Quantidades por Formato")
    for formato in formatos:
        quantidade_feeds_dict[formato] = st.number_input(f"{formato} - QUANTIDADE DE FEEDS - C1", min_value=0, value=1, key=f"feeds_{formato}")
        quantidade_stories_dict[formato] = st.number_input(f"{formato} - QUANTIDADE DE COMBOS DE STORIES - C1", min_value=0, value=0, key=f"stories_{formato}")

if st.button("Adicionar Influenciador"):
    usuario_limpo = username.strip().replace("@", "")
    if rede == "INSTAGRAM":
        audiencia = get_instagram_followers(usuario_limpo)
    elif rede == "TIKTOK":
        audiencia = get_tiktok_followers(usuario_limpo)
    else:
        audiencia = 0

    if audiencia is not None:
        for formato in formatos:
            qtd_feeds = quantidade_feeds_dict.get(formato, 0)
            qtd_stories = quantidade_stories_dict.get(formato, 0)

            alcance_feed = round(calcular_alcance(formato, audiencia) * qtd_feeds)
            alcance_reels = round(calcular_alcance("INSTAGRAM REELS", audiencia) * qtd_feeds) if formato == "INSTAGRAM REELS" else 0
            alcance_stories = round(calcular_alcance_stories(audiencia) * qtd_stories) if rede == "INSTAGRAM" else 0

            impressoes_feed = round(calcular_impressoes_feed(formato, audiencia) * qtd_feeds)
            impressoes_stories = round(calcular_impressoes_stories(audiencia) * qtd_stories) if rede == "INSTAGRAM" else 0

            novo_registro = {
                "REDE": rede,
                "FORMATO": formato,
                "INFLUENCIADOR": username,
                "PLATAFORMA": rede,
                "AUDIÊNCIA": round(audiencia),
                "ALCANCE ESTIMADO (FEED)": alcance_feed,
                "ALCANCE ESTIMADO (REELS)": alcance_reels,
                "ALCANCE ESTIMADO (STORIES)": alcance_stories,
                "IMPRESSÕES ESTIMADAS (FEED)": impressoes_feed,
                "IMPRESSÕES ESTIMADAS (STORIES)": impressoes_stories,
                "QUANTIDADE DE FEEDS - C1": qtd_feeds,
                "QUANTIDADE DE COMBOS DE STORIES - C1": qtd_stories
            }

            st.session_state.registros.append(novo_registro)
        st.success("Influenciador adicionado com sucesso!")

colunas_finais = [
    "REDE", "FORMATO", "INFLUENCIADOR", "PLATAFORMA", "AUDIÊNCIA",
    "ALCANCE ESTIMADO (FEED)", "ALCANCE ESTIMADO (REELS)", "ALCANCE ESTIMADO (STORIES)",
    "IMPRESSÕES ESTIMADAS (FEED)", "IMPRESSÕES ESTIMADAS (STORIES)",
    "QUANTIDADE DE FEEDS - C1", "QUANTIDADE DE COMBOS DE STORIES - C1"
]

if st.session_state.registros:
    df = pd.DataFrame(st.session_state.registros)[colunas_finais]
    st.subheader("📋 Tabela de Influenciadores")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="influenciadores.csv", mime="text/csv")
