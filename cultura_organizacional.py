import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe
# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6" # Cor da logo Wedja
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Inventário Organizacional — Cultura e Prática",
    layout="wide"
)

# --- CSS CUSTOMIZADO PARA A INTERFACE ---
st.markdown(f"""
    <style>
        /* Remoção de elementos do Streamlit Cloud */
        div[data-testid="stHeader"], div[data-testid="stDecoration"] {{
            visibility: hidden; height: 0%; position: fixed;
        }}
        footer {{ visibility: hidden; height: 0%; }}
        /* Estilos gerais */
        .stApp {{ background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT_DARK}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT_DARK}; }}
        /* Cabeçalho customizado */
        .stApp > header {{
            background-color: {COLOR_PRIMARY}; padding: 1rem;
            border-bottom: 5px solid {COLOR_TEXT_DARK};
        }}
        /* Card de container */
        div.st-emotion-cache-1r4qj8v {{
             background-color: #f0f2f6; border-left: 5px solid {COLOR_PRIMARY};
             border-radius: 5px; padding: 1.5rem; margin-top: 1rem;
             margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        /* Labels dos Inputs */
        div[data-testid="textInputRootElement"] > label,
        div[data-testid="stTextArea"] > label,
        div[data-testid="stRadioGroup"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        /* Bordas dos campos de input */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {{
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: #FFFFFF;
        }}
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: {COLOR_PRIMARY}; color: white; font-size: 1.2rem;
            font-weight: bold; border-radius: 8px; margin-top: 1rem;
            padding: 0.75rem 1rem; border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .streamlit-expanderHeader:hover {{ background-color: {COLOR_TEXT_DARK}; }}
        .streamlit-expanderContent {{
            background-color: #f9f9f9; border-left: 3px solid {COLOR_PRIMARY}; padding: 1rem;
            border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; margin-bottom: 1rem;
        }}
        /* Botões de rádio (Likert) responsivos */
        div[data-testid="stRadio"] > div {{
            display: flex; flex-wrap: wrap; justify-content: flex-start;
        }}
        div[data-testid="stRadio"] label {{
            margin-right: 1.2rem; margin-bottom: 0.5rem; color: {COLOR_TEXT_DARK};
        }}
        /* Botão de Finalizar */
        .stButton button {{
            background-color: {COLOR_PRIMARY}; color: white; font-weight: bold;
            padding: 0.75rem 1.5rem; border-radius: 8px; border: none;
        }}
        .stButton button:hover {{
            background-color: {COLOR_TEXT_DARK}; color: white;
        }}
    </style>
""", unsafe_allow_html=True)

try:
    # Cria uma cópia editável das credenciais
    creds_dict = dict(st.secrets["google_credentials"])
    # Corrige a formatação da chave privada
    creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
    
    # Autentica no Google
    gc = gspread.service_account_from_dict(creds_dict)
    
    # Abre a planilha pelo nome exato
    spreadsheet = gc.open("Respostas Formularios")
    
    # Seleciona a primeira aba
    worksheet = spreadsheet.sheet1

except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    st.stop()

# Seleciona as abas fora da função de cache
ws_respostas = spreadsheet.worksheet("Cultura")

# --- CABEÇALHO DA APLICAÇÃO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo_wedja.jpg", width=120)
    except FileNotFoundError:
        st.warning("Logo 'logo_wedja.jpg' não encontrada.")
with col2:
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
        <h1 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>Inventário Organizacional</h1>
        <h3 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>Cultura e Prática</h3>
    </div>
    """, unsafe_allow_html=True)


# --- SEÇÃO DE IDENTIFICAÇÃO ---
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação</h3>", unsafe_allow_html=True)
    col1_form, col2_form = st.columns(2)
    with col1_form:
        respondente = st.text_input("Respondente:", key="input_respondente")
        data = st.text_input("Data:", datetime.now().strftime('%d/%m/%Y'))
    with col2_form:
        organizacao_coletora = st.text_input("Organização Coletora:", "Instituto Wedja de Socionomia", disabled=True)


# --- INSTRUÇÕES ---
with st.expander("Ver Orientações aos Respondentes", expanded=True):
    st.info(
        """
        - **Objetivo:** Avaliar dimensões da organização como regras, normas, reputação, valores e práticas.
        - **Escala Likert 1–5:** 1=Discordo totalmente, 2=Discordo parcialmente, 3=Neutro, 4=Concordo parcialmente, 5=Concordo totalmente.
        - **Confidencialidade:** Responda de forma individual e espontânea. Suas respostas são confidenciais e contribuem para um ambiente de trabalho mais saudável.
        """
    )


# --- LÓGICA DO QUESTIONÁRIO (BACK-END) ---
@st.cache_data
def carregar_itens():
    data = [
        ('Regras e Normas', 'RN01', 'As regras da empresa são claras e bem comunicadas a todos os colaboradores.', 'NÃO'),
        ('Regras e Normas', 'RN02', 'As normas são aplicadas de forma justa e consistente entre os diferentes setores.', 'NÃO'),
        ('Regras e Normas', 'RN03', 'As políticas internas são seguidas na prática, e não apenas no papel.', 'NÃO'),
        ('Regras e Normas', 'RN04', 'A empresa revisa e atualiza suas normas de acordo com mudanças no mercado ou legislação.', 'NÃO'),
        ('Reputação e Imagem', 'RI01', 'A empresa é reconhecida externamente como uma organização ética.', 'NÃO'),
        ('Reputação e Imagem', 'RI02', 'Os clientes e parceiros confiam na imagem da empresa.', 'NÃO'),
        ('Reputação e Imagem', 'RI03', 'A reputação da empresa influencia positivamente a motivação dos colaboradores.', 'NÃO'),
        ('Reputação e Imagem', 'RI04', 'A organização é vista como inovadora e de credibilidade no seu setor.', 'NÃO'),
        ('Valores Organizacionais', 'VO01', 'Os valores da empresa são conhecidos e compreendidos pelos colaboradores.', 'NÃO'),
        ('Valores Organizacionais', 'VO02', 'Os líderes praticam os valores que divulgam.', 'NÃO'),
        ('Valores Organizacionais', 'VO03', 'Os valores da empresa orientam decisões estratégicas.', 'NÃO'),
        ('Valores Organizacionais', 'VO04', 'Existe coerência entre discurso e prática em relação aos valores da organização.', 'NÃO'),
        ('Práticas Formais', 'PF01', 'Os processos de gestão são padronizados e documentados.', 'NÃO'),
        ('Práticas Formais', 'PF02', 'Existem rituais e práticas formais que reforçam a cultura organizacional (ex.: reuniões, relatórios, treinamentos).', 'NÃO'),
        ('Práticas Formais', 'PF03', 'Há critérios claros e formais para promoção e reconhecimento de colaboradores.', 'NÃO'),
        ('Práticas Formais', 'PF04', 'A empresa oferece programas estruturados de desenvolvimento de pessoas.', 'NÃO'),
        ('Práticas Informais', 'PI01', 'A troca de informações ocorre de maneira espontânea e colaborativa.', 'NÃO'),
        ('Práticas Informais', 'PI02', 'A cultura do “jeitinho” (soluções improvisadas) é comum na empresa.', 'NÃO'),
        ('Práticas Informais', 'PI03', 'Os relacionamentos pessoais influenciam fortemente decisões internas.', 'NÃO'),
        ('Práticas Informais', 'PI04', 'Existem redes de apoio informais entre os colaboradores (amizades, grupos, trocas).', 'NÃO'),
    ]
    df = pd.DataFrame(data, columns=["Bloco", "ID", "Item", "Reverso"])
    return df

# --- INICIALIZAÇÃO E FORMULÁRIO DINÂMICO ---
df_itens = carregar_itens()
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}

st.subheader("Questionário")
blocos = df_itens["Bloco"].unique().tolist()
def registrar_resposta(item_id, key):
    st.session_state.respostas[item_id] = st.session_state[key]

for bloco in blocos:
    df_bloco = df_itens[df_itens["Bloco"] == bloco]
    # Extrai o prefixo (sigla) a partir do ID do primeiro item do bloco
    prefixo_bloco = df_bloco['ID'].iloc[0][:2] if not df_bloco.empty else bloco
    
    # Usa a sigla como título do expander
    with st.expander(f"{prefixo_bloco}", expanded=True):
        df_bloco = df_itens[df_itens["Bloco"] == bloco]
        for _, row in df_bloco.iterrows():
            item_id = row["ID"]
            label = f'({item_id}) {row["Item"]}'
            widget_key = f"radio_{item_id}"
            st.radio(
                label, options=["N/A", 1, 2, 3, 4, 5],
                horizontal=True, key=widget_key,
                on_change=registrar_resposta, args=(item_id, widget_key)
            )

# --- BOTÃO DE FINALIZAR E LÓGICA DE RESULTADOS/EXPORTAÇÃO ---
if st.button("Finalizar e Gerar Relatório", type="primary"):
    if not st.session_state.respostas:
        st.warning("Nenhuma resposta foi preenchida.")
    else:
        st.subheader("Resultados e Exportação")

        # --- LÓGICA DE CÁLCULO ---
        respostas_list = []
        for index, row in df_itens.iterrows():
            item_id = row['ID']
            resposta_usuario = st.session_state.respostas.get(item_id)
            respostas_list.append({
                "Bloco": row["Bloco"], "Item": row["Item"],
                "Resposta": resposta_usuario, "Reverso": row["Reverso"]
            })
        dfr = pd.DataFrame(respostas_list)

        dfr_numerico = dfr[pd.to_numeric(dfr['Resposta'], errors='coerce').notna()].copy()
        if not dfr_numerico.empty:
            dfr_numerico['Resposta'] = dfr_numerico['Resposta'].astype(int)
            def ajustar_reverso(row):
                return (6 - row["Resposta"]) if row["Reverso"] == "SIM" else row["Resposta"]
            dfr_numerico["Pontuação"] = dfr_numerico.apply(ajustar_reverso, axis=1)
            media_geral = dfr_numerico["Pontuação"].mean()
            resumo_blocos = dfr_numerico.groupby("Bloco")["Pontuação"].mean().round(2).reset_index(name="Média").sort_values("Média")
        else:
            media_geral = 0
            resumo_blocos = pd.DataFrame(columns=["Bloco", "Média"])

        st.metric("Pontuação Média Geral (somente itens de 1 a 5)", f"{media_geral:.2f}")

        if not resumo_blocos.empty:
            st.subheader("Média por Dimensão")
            st.dataframe(resumo_blocos.rename(columns={"Bloco": "Dimensão"}), use_container_width=True, hide_index=True)
            
            st.subheader("Gráfico Comparativo por Dimensão")
            
            # Criação do gráfico de pizza com Matplotlib
            fig, ax = plt.subplots()
            ax.pie(resumo_blocos["Média"], labels=resumo_blocos["Bloco"], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Garante que a pizza seja um círculo.
            
            # Exibe o gráfico no Streamlit
            st.pyplot(fig)
     # --- ADICIONAR ESTE TRECHO PARA ENVIO AO GOOGLE SHEETS ---
        with st.spinner("Enviando dados para a planilha..."):
            try:
                # 1. Preparar dados para o envio
                timestamp_str = datetime.now().isoformat(timespec="seconds")
                respostas_para_enviar = []
                
                # O DataFrame 'dfr' já foi criado na seção de cálculo
                for _, row in dfr.iterrows():
                    respostas_para_enviar.append([
                        timestamp_str,
                        respondente,
                        data,
                        organizacao_coletora,
                        row["Bloco"],
                        row["Item"],
                        row["Resposta"] if pd.notna(row["Resposta"]) else "N/A",
                        #observacoes # Adiciona as observações em cada linha
                    ])
                
                # 2. Enviar para a aba "Cultura e Pratica"
                ws_respostas.append_rows(respostas_para_enviar, value_input_option='USER_ENTERED')
                
                st.success("Suas respostas foram enviadas com sucesso para a planilha!")

            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")

                with st.container():
                    st.markdown('<div id="autoclick-div">', unsafe_allow_html=True)
                    if st.button("Ping Button", key="autoclick_button"):
                    # A ação aqui pode ser um simples print no log do Streamlit
                      print("Ping button clicked by automation.")
                    st.markdown('</div>', unsafe_allow_html=True)