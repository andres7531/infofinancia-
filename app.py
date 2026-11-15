import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="InfoFinancias", page_icon="📈", layout="wide")

# ----------------------------------------------------------------------------
# ESTILO
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    :root { --accent:#14b8a6; --ink:#172554; --muted:#64748b; --surface:#ffffff; }
    .stApp { background: linear-gradient(145deg,#f8fafc 0%,#eff6ff 55%,#f0fdfa 100%); color: var(--ink); }
    .block-container { max-width: 1440px; padding: 2rem clamp(1rem,3vw,3rem) 3rem; }
    h1,h2,h3 { letter-spacing: -0.035em; }
    h1 { font-weight: 800; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#f1f5f9 0%,#ecfeff 100%); border-right:1px solid #dbeafe; }
    [data-testid="stMetric"] { background: var(--surface); border:1px solid #e2e8f0; border-radius:14px;
        padding:1rem 1.1rem; box-shadow:0 5px 18px rgba(15,23,42,.05); min-height:108px; }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--ink); font-weight: 750; }
    [data-testid="stDataFrame"] { border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; }
    .stButton button, [data-testid="stDownloadButton"] button { border-radius:10px; font-weight:650; }
    .noticia { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:.9rem 1.1rem;
        margin-bottom:.8rem; box-shadow:0 3px 12px rgba(15,23,42,.04); }
    .noticia a { color: var(--ink); font-weight:700; text-decoration:none; }
    .noticia a:hover { color: var(--accent); }
    .noticia small { color: var(--muted); display:block; margin-top:.3rem; }
    @media (max-width:768px) {
        .block-container { padding:1.25rem .8rem 2rem; }
        h1 { font-size:1.8rem; } h2 { font-size:1.4rem; }
        [data-testid="stHorizontalBlock"] { flex-wrap:wrap; gap:.65rem; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex:1 1 calc(50% - .65rem) !important; min-width:calc(50% - .65rem) !important; }
        [data-testid="stMetric"] { padding:.8rem; min-height:92px; }
        [data-testid="stMetricValue"] { font-size:1.25rem; }
    }
    @media (max-width:420px) {
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex-basis:100% !important; min-width:100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# TEXTOS / IDIOMAS
# ----------------------------------------------------------------------------
IDIOMAS = {"Português": "pt", "English": "en", "Español": "es", "Italiano": "it", "中文": "zh", "한국어": "ko", "日本語": "ja"}

TEXTOS = {
    "pt": ["📈 Monitor de Finanças e Bolsas Mundiais", "Configurações de Mercado", "Selecione um ativo rápido:", "Ou digite qualquer Ticker global:", "Período histórico:", "Converter valores para Reais (BRL)", "🤖 Radar quantitativo de investimentos", "Ranking dos ativos sugeridos com base em retornos recentes e volatilidade histórica. É uma triagem informativa, não uma previsão nem recomendação financeira personalizada.", "Analisando o desempenho histórico dos ativos...", "Não foi possível obter dados suficientes para montar o ranking neste momento.", "Maior pontuação no período analisado", "Baixando dados da bolsa em tempo real...", "Ativo não encontrado. Verifique o código inserido (ex: PETR4.SA, AAPL).", "Preço Atual", "Máxima no Período", "Mínima no Período", "Volume (Último pregão)", "Histórico de Preços", "Data", "Preço", "Ver dados históricos tabulados", "Ocorreu um erro ao carregar os dados", "📰 Notícias diárias do mercado internacional", "Sem notícias disponíveis no momento."],
    "en": ["📈 Global Finance and Markets Tracker", "Market Settings", "Select a suggested asset:", "Or enter any global ticker:", "Historical period:", "Convert values to Brazilian Reais (BRL)", "🤖 Quantitative Investment Radar", "Ranking of suggested assets based on recent returns and historical volatility. Informational screening only, not a forecast or personalized financial advice.", "Analyzing historical asset performance...", "Unable to retrieve enough data to build the ranking right now.", "Highest score in the analyzed period", "Loading market data...", "Asset not found. Check the ticker (e.g. PETR4.SA, AAPL).", "Current Price", "Period High", "Period Low", "Latest Session Volume", "Price History", "Date", "Price", "View historical data", "An error occurred while loading data", "📰 Daily international market news", "No news available at the moment."],
    "es": ["📈 Monitor de Finanzas y Mercados Mundiales", "Configuración del mercado", "Seleccione un activo sugerido:", "O escriba cualquier ticker global:", "Período histórico:", "Convertir valores a reales brasileños (BRL)", "🤖 Radar cuantitativo de inversiones", "Clasificación basada en rendimientos recientes y volatilidad histórica. Es informativa, no es una previsión ni recomendación financiera personalizada.", "Analizando el rendimiento histórico...", "No se pudieron obtener datos suficientes para crear la clasificación.", "Mayor puntuación del período analizado", "Cargando datos del mercado...", "Activo no encontrado. Verifique el ticker (p. ej., PETR4.SA, AAPL).", "Precio actual", "Máximo del período", "Mínimo del período", "Volumen de la última sesión", "Historial de precios", "Fecha", "Precio", "Ver datos históricos", "Se produjo un error al cargar los datos", "📰 Noticias diarias del mercado internacional", "No hay noticias disponibles en este momento."],
    "it": ["📈 Monitor della finanza e dei mercati globali", "Impostazioni di mercato", "Seleziona un asset suggerito:", "Oppure inserisci un ticker globale:", "Periodo storico:", "Converti i valori in real brasiliani (BRL)", "🤖 Radar quantitativo degli investimenti", "Classifica basata sui rendimenti recenti e sulla volatilità storica. Solo a scopo informativo, non è una previsione né una raccomandazione finanziaria personalizzata.", "Analisi della performance storica...", "Impossibile recuperare dati sufficienti per creare la classifica.", "Punteggio più alto nel periodo analizzato", "Caricamento dei dati di mercato...", "Asset non trovato. Verifica il ticker (es. PETR4.SA, AAPL).", "Prezzo attuale", "Massimo del periodo", "Minimo del periodo", "Volume dell'ultima sessione", "Storico dei prezzi", "Data", "Prezzo", "Visualizza i dati storici", "Errore durante il caricamento dei dati", "📰 Notizie giornaliere del mercato internazionale", "Nessuna notizia disponibile al momento."],
    "zh": ["📈 全球金融与市场追踪器", "市场设置", "选择推荐资产：", "或输入全球股票代码：", "历史周期：", "将数值转换为巴西雷亚尔（BRL）", "🤖 量化投资雷达", "根据近期回报和历史波动率进行排名。仅供参考，不构成预测或个性化投资建议。", "正在分析历史表现...", "目前无法获取足够数据来生成排名。", "分析期间最高分", "正在加载市场数据...", "未找到资产。请检查代码（例如 PETR4.SA、AAPL）。", "当前价格", "期间最高价", "期间最低价", "最近交易量", "价格历史", "日期", "价格", "查看历史数据", "加载数据时发生错误", "📰 国际市场每日新闻", "目前没有可用新闻。"],
    "ko": ["📈 글로벌 금융 및 시장 추적기", "시장 설정", "추천 자산 선택:", "또는 글로벌 티커 입력:", "과거 기간:", "값을 브라질 헤알(BRL)로 변환", "🤖 정량 투자 레이더", "최근 수익률과 과거 변동성을 기준으로 한 순위입니다. 정보 제공 목적이며 예측이나 맞춤형 금융 조언이 아닙니다.", "과거 자산 성과 분석 중...", "현재 순위를 작성하기에 충분한 데이터를 가져올 수 없습니다.", "분석 기간 중 최고 점수", "시장 데이터 불러오는 중...", "자산을 찾을 수 없습니다. 티커를 확인하세요(예: PETR4.SA, AAPL).", "현재 가격", "기간 최고가", "기간 최저가", "최근 거래량", "가격 기록", "날짜", "가격", "과거 데이터 보기", "데이터를 불러오는 중 오류가 발생했습니다", "📰 국제 시장 일일 뉴스", "현재 사용할 수 있는 뉴스가 없습니다."],
    "ja": ["📈 グローバル金融・市場トラッカー", "市場設定", "おすすめ資産を選択：", "または世界のティッカーを入力：", "過去の期間：", "値をブラジルレアル（BRL）に換算", "🤖 定量投資レーダー", "最近のリターンと過去のボラティリティに基づくランキングです。情報提供のみを目的とし、予測や個別の投資助言ではありません。", "過去のパフォーマンスを分析中...", "ランキング作成に十分なデータを取得できませんでした。", "分析期間中の最高スコア", "市場データを読み込み中...", "資産が見つかりません。ティッカーを確認してください（例：PETR4.SA、AAPL）。", "現在価格", "期間中の最高値", "期間中の最安値", "直近の取引量", "価格履歴", "日付", "価格", "過去データを表示", "データの読み込み中にエラーが発生しました", "📰 国際市場の毎日のニュース", "現在利用可能なニュースはありません。"],
}

# Textos novos (pt/en/es; os demais idiomas caem para inglês)
NOVOS = {
    "tab_mercado":  {"pt": "📊 Ativo", "en": "📊 Asset", "es": "📊 Activo"},
    "tab_radar":    {"pt": "🤖 Radar", "en": "🤖 Radar", "es": "🤖 Radar"},
    "tab_noticias": {"pt": "📰 Notícias", "en": "📰 News", "es": "📰 Noticias"},
    "moedas_dia":   {"pt": "Cotações de moedas do dia (em BRL)", "en": "Today's currency rates (in BRL)", "es": "Cotizaciones de divisas del día (en BRL)"},
    "moedas_erro":  {"pt": "Não foi possível carregar as cotações de moedas agora.", "en": "Could not load currency rates right now.", "es": "No se pudieron cargar las cotizaciones ahora."},
    "selecione":    {"pt": "— Selecione um resultado —", "en": "— Select a result —", "es": "— Seleccione un resultado —"},
    "ret_periodo":  {"pt": "Retorno no período", "en": "Period return", "es": "Rentabilidad del período"},
    "volat":        {"pt": "Volatilidade anualizada", "en": "Annualized volatility", "es": "Volatilidad anualizada"},
    "queda_max":    {"pt": "Queda máxima (drawdown)", "en": "Max drawdown", "es": "Caída máxima (drawdown)"},
    "baixar_csv":   {"pt": "⬇️ Baixar CSV", "en": "⬇️ Download CSV", "es": "⬇️ Descargar CSV"},
    "volume":       {"pt": "Volume", "en": "Volume", "es": "Volumen"},
    "cotacao":      {"pt": "Cotação", "en": "Quote", "es": "Cotización"},
    "cambio_ok":    {"pt": "💱 Moeda original: {m} | Taxa aplicada: 1 {m} = R$ {t:.4f}",
                     "en": "💱 Original currency: {m} | Rate applied: 1 {m} = R$ {t:.4f}",
                     "es": "💱 Moneda original: {m} | Tasa aplicada: 1 {m} = R$ {t:.4f}"},
    "cambio_falha": {"pt": "⚠️ Não foi possível obter o câmbio de {m} para BRL. Valores exibidos na moeda original.",
                     "en": "⚠️ Could not get the {m}/BRL rate. Showing values in the original currency.",
                     "es": "⚠️ No se pudo obtener el tipo de cambio {m}/BRL. Se muestran los valores en la moneda original."},
    "cambio_nota":  {"pt": "A conversão usa a cotação mais recente aplicada a todo o histórico (aproximação).",
                     "en": "Conversion uses the latest rate applied to the whole history (approximation).",
                     "es": "La conversión usa la cotización más reciente aplicada a todo el historial (aproximación)."},
}

idioma_selecionado = st.sidebar.selectbox("Idioma / Language / Idioma", list(IDIOMAS))
idioma = IDIOMAS[idioma_selecionado]


def texto(i):
    return TEXTOS[idioma][i]


def n(chave, **kw):
    d = NOVOS[chave]
    return (d.get(idioma) or d["en"]).format(**kw)


ROTULOS_BUSCA = {
    "pt": ("Buscar ação ou índice por nome/ticker:", "Resultados da busca global:"),
    "en": ("Search global stocks or indices by name/ticker:", "Global search results:"),
    "es": ("Buscar acciones o índices por nombre/ticker:", "Resultados de búsqueda global:"),
    "it": ("Cerca azioni o indici per nome/ticker:", "Risultati della ricerca globale:"),
    "zh": ("按名称/代码搜索全球股票或指数：", "全球搜索结果："),
    "ko": ("이름/티커로 전 세계 주식 또는 지수 검색:", "글로벌 검색 결과:"),
    "ja": ("名称・ティッカーで世界の株式や指数を検索：", "検索結果："),
}

# ----------------------------------------------------------------------------
# DADOS
# ----------------------------------------------------------------------------
ATIVOS_SUGERIDOS = {
    "Petrobras (Brasil - B3)": "PETR4.SA",
    "Vale (Brasil - B3)": "VALE3.SA",
    "FII KNRI11 (Brasil - B3)": "KNRI11.SA",
    "FII MXRF11 (Brasil - B3)": "MXRF11.SA",
    "FII HGLG11 (Brasil - B3)": "HGLG11.SA",
    "REIT Realty Income (EUA - NYSE)": "O",
    "REIT Prologis (EUA - NYSE)": "PLD",
    "Apple (EUA - NASDAQ)": "AAPL",
    "NVIDIA (EUA - NASDAQ)": "NVDA",
    "S&P 500 (Índice EUA)": "^GSPC",
    "Ibovespa (Índice Brasil)": "^BVSP",
    "Toyota (Japão - Tóquio)": "7203.T",
    "SAP (Alemanha - XETRA)": "SAP.DE",
    "Dólar / Real": "USDBRL=X",
    "Bitcoin (USD)": "BTC-USD", "Ethereum (USD)": "ETH-USD", "BNB (USD)": "BNB-USD",
    "XRP (USD)": "XRP-USD", "Solana (USD)": "SOL-USD", "Cardano (USD)": "ADA-USD",
    "Dogecoin (USD)": "DOGE-USD", "TRON (USD)": "TRX-USD", "Chainlink (USD)": "LINK-USD",
    "Polkadot (USD)": "DOT-USD", "Litecoin (USD)": "LTC-USD", "Bitcoin Cash (USD)": "BCH-USD",
    "Avalanche (USD)": "AVAX-USD", "Stellar (USD)": "XLM-USD", "Shiba Inu (USD)": "SHIB-USD",
    "Toncoin (USD)": "TON-USD", "Monero (USD)": "XMR-USD", "Ethereum Classic (USD)": "ETC-USD",
    "Hedera (USD)": "HBAR-USD", "Uniswap (USD)": "UNI-USD", "Cosmos (USD)": "ATOM-USD",
    "Aptos (USD)": "APT-USD", "NEAR Protocol (USD)": "NEAR-USD", "Internet Computer (USD)": "ICP-USD",
    "Filecoin (USD)": "FIL-USD", "Arbitrum (USD)": "ARB-USD", "Optimism (USD)": "OP-USD",
    "Sui (USD)": "SUI-USD", "Pepe (USD)": "PEPE-USD", "Render (USD)": "RENDER-USD",
}


@st.cache_data(ttl=900, show_spinner=False)
def buscar_ativos_globalmente(consulta):
    try:
        quotes = yf.Search(consulta, max_results=15).quotes
        return [
            (q["symbol"], q.get("shortname") or q.get("longname") or q["symbol"])
            for q in quotes if q.get("symbol")
        ]
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def carregar_dados(ticker, periodo):
    ativo = yf.Ticker(ticker)
    hist = ativo.history(period=periodo)
    try:
        info = ativo.info or {}
    except Exception:
        info = {}
    nome = info.get("shortName") or info.get("longName") or ticker
    moeda = info.get("currency")
    if not moeda:
        try:
            moeda = (ativo.get_history_metadata() or {}).get("currency")
        except Exception:
            moeda = None
    return hist, nome, moeda or "USD"


@st.cache_data(ttl=300, show_spinner=False)
def obter_taxa_cambio(moeda):
    """Retorna a taxa moeda->BRL, ou None se não for possível obter."""
    if not moeda or moeda == "BRL":
        return 1.0
    fator = 1.0
    if moeda == "GBp":          # libras em centavos (pence), comum na bolsa de Londres
        moeda, fator = "GBP", 0.01
    try:
        h = yf.Ticker(f"{moeda}BRL=X").history(period="5d")["Close"].dropna()
        if not h.empty:
            return float(h.iloc[-1]) * fator
    except Exception:
        pass
    return None


@st.cache_data(ttl=300, show_spinner=False)
def obter_cotacoes_moedas():
    cotacoes = {}
    for moeda, tk in {"USD": "USDBRL=X", "EUR": "EURBRL=X", "GBP": "GBPBRL=X", "JPY": "JPYBRL=X"}.items():
        try:
            h = yf.Ticker(tk).history(period="5d")["Close"].dropna()
            if not h.empty:
                var = (h.iloc[-1] / h.iloc[-2] - 1) * 100 if len(h) > 1 else None
                cotacoes[moeda] = (float(h.iloc[-1]), var)
        except Exception:
            continue
    return cotacoes


def _url(valor):
    if isinstance(valor, dict):
        return valor.get("url") or ""
    return valor or ""


def _normalizar_noticia(item, mercado):
    """Aceita o formato antigo e o novo (item['content']) do yfinance."""
    c = item.get("content") if isinstance(item.get("content"), dict) else item
    titulo = (c.get("title") or "").strip()
    link = _url(c.get("canonicalUrl")) or _url(c.get("clickThroughUrl")) or c.get("link") or c.get("url") or ""
    if not titulo or not link:
        return None

    fonte = c.get("provider") or c.get("publisher") or ""
    if isinstance(fonte, dict):
        fonte = fonte.get("displayName") or fonte.get("name") or ""

    ts = pd.NaT
    if c.get("pubDate"):
        ts = pd.to_datetime(c["pubDate"], utc=True, errors="coerce")
    elif item.get("providerPublishTime"):
        ts = pd.to_datetime(item["providerPublishTime"], unit="s", utc=True, errors="coerce")

    return {"titulo": titulo, "link": link, "fonte": str(fonte).strip() or "Yahoo Finance",
            "ts": ts, "mercado": mercado}


@st.cache_data(ttl=1800, show_spinner=False)
def obter_noticias_mercado(limite=12):
    mercados = {
        "EUA": ["^GSPC", "^DJI", "^IXIC", "AAPL", "MSFT", "NVDA"],
        "Japão": ["^N225", "7203.T", "6758.T"],
        "China": ["^HSI", "000001.SS", "BABA"],
        "Brasil": ["^BVSP", "PETR4.SA", "VALE3.SA"],
    }
    tarefas = [(m, tk) for m, tks in mercados.items() for tk in tks]

    def buscar(par):
        mercado, tk = par
        try:
            return [x for x in (_normalizar_noticia(i, mercado) for i in (yf.Ticker(tk).news or [])[:6]) if x]
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=8) as ex:
        listas = list(ex.map(buscar, tarefas))

    vistos, noticias = set(), []
    for lista in listas:
        for nt in lista:
            if nt["titulo"] not in vistos:
                vistos.add(nt["titulo"])
                noticias.append(nt)

    noticias.sort(key=lambda x: (pd.isna(x["ts"]), -(x["ts"].value if pd.notna(x["ts"]) else 0)))
    for nt in noticias:
        nt["tempo"] = (nt["ts"].tz_convert("America/Sao_Paulo").strftime("%d/%m/%Y %H:%M")
                       if pd.notna(nt["ts"]) else "Recente")
        nt.pop("ts")
    return noticias[:limite]


@st.cache_data(ttl=900, show_spinner=False)
def analisar_ativos():
    """Baixa todos os ativos de uma vez (bem mais rápido que um por um)."""
    tickers = list(dict.fromkeys(ATIVOS_SUGERIDOS.values()))
    try:
        dados = yf.download(tickers, period="6mo", auto_adjust=True, progress=False,
                            group_by="ticker", threads=True)
    except Exception:
        return pd.DataFrame()

    nomes = {v: k for k, v in ATIVOS_SUGERIDOS.items()}
    linhas = []
    for tk in tickers:
        try:
            close = dados[tk]["Close"].dropna()
            if len(close) < 22:
                continue
            fim = close.index[-1]
            # janelas por data de calendário (cripto negocia 7 dias; ações ~5)
            ref_1m = close.loc[:fim - pd.Timedelta(days=30)]
            ref_3m = close.loc[:fim - pd.Timedelta(days=91)]
            if ref_1m.empty or ref_3m.empty:
                continue
            r1 = (close.iloc[-1] / ref_1m.iloc[-1] - 1) * 100
            r3 = (close.iloc[-1] / ref_3m.iloc[-1] - 1) * 100
            vol = close.pct_change().dropna().std() * (252 ** 0.5) * 100
            linhas.append({
                "Ativo": nomes[tk], "Ticker": tk,
                "Retorno 1 mês (%)": r1, "Retorno 3 meses (%)": r3,
                "Volatilidade anualizada (%)": vol,
                "Pontuação": 0.4 * r1 + 0.6 * r3 - 0.15 * vol,
            })
        except Exception:
            continue
    if not linhas:
        return pd.DataFrame()
    return pd.DataFrame(linhas).sort_values("Pontuação", ascending=False).reset_index(drop=True)


# ----------------------------------------------------------------------------
# BARRA LATERAL
# ----------------------------------------------------------------------------
st.title(texto(0))

st.sidebar.header(texto(1))
escolha = st.sidebar.selectbox(texto(2), list(ATIVOS_SUGERIDOS))
rotulo_busca, rotulo_resultados = ROTULOS_BUSCA[idioma]
consulta = st.sidebar.text_input(rotulo_busca).strip()
resultados_busca = buscar_ativos_globalmente(consulta) if consulta else []
opcoes_busca = [("", n("selecione"))] + resultados_busca
resultado = st.sidebar.selectbox(
    rotulo_resultados, opcoes_busca,
    format_func=lambda it: f"{it[1]} ({it[0]})" if it[0] else it[1],
)
ticker_inicial = resultado[0] or ATIVOS_SUGERIDOS[escolha]
ticker_custom = st.sidebar.text_input(texto(3), value=ticker_inicial, key=f"ticker_{ticker_inicial}").strip().upper()
periodo = st.sidebar.selectbox(texto(4), ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
converter_brl = st.sidebar.checkbox(texto(5), value=True)
if converter_brl:
    st.sidebar.caption(n("cambio_nota"))

# ----------------------------------------------------------------------------
# CORPO
# ----------------------------------------------------------------------------
st.subheader(n("moedas_dia"))
cotacoes = obter_cotacoes_moedas()
if cotacoes:
    for col, (moeda, (valor, var)) in zip(st.columns(len(cotacoes)), cotacoes.items()):
        col.metric(f"1 {moeda}", f"R$ {valor:,.4f}", f"{var:.2f}%" if var is not None else None)
else:
    st.caption(n("moedas_erro"))

tab_ativo, tab_radar, tab_noticias = st.tabs([n("tab_mercado"), n("tab_radar"), n("tab_noticias")])

# ---- ABA: ATIVO -------------------------------------------------------------
with tab_ativo:
    if ticker_custom:
        try:
            with st.spinner(texto(11)):
                df, nome, moeda_original = carregar_dados(ticker_custom, periodo)

            if df.empty:
                st.error(texto(12))
            else:
                df = df.copy()
                moeda_exibicao = moeda_original
                taxa = 1.0
                aviso_cambio = None

                if converter_brl and moeda_original != "BRL":
                    t = obter_taxa_cambio(moeda_original)
                    if t is None:
                        aviso_cambio = n("cambio_falha", m=moeda_original)
                    else:
                        taxa, moeda_exibicao = t, "BRL"
                        for c in ["Open", "High", "Low", "Close"]:
                            df[c] = df[c] * taxa
                        aviso_cambio = n("cambio_ok", m=moeda_original, t=taxa)
                elif moeda_original == "GBp":
                    pass

                simbolo = "R$" if moeda_exibicao == "BRL" else moeda_exibicao
                fechamento = df["Close"]
                preco = fechamento.iloc[-1]
                anterior = fechamento.iloc[-2] if len(fechamento) > 1 else preco
                var_dia = (preco / anterior - 1) * 100 if anterior else 0
                ret_periodo = (preco / fechamento.iloc[0] - 1) * 100
                vol_anual = fechamento.pct_change().dropna().std() * (252 ** 0.5) * 100
                drawdown = ((fechamento / fechamento.cummax()) - 1).min() * 100

                st.subheader(f"{nome} ({ticker_custom})")
                if aviso_cambio:
                    st.caption(aviso_cambio)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric(texto(13), f"{simbolo} {preco:,.2f}", f"{var_dia:.2f}%")
                c2.metric(texto(14), f"{simbolo} {df['High'].max():,.2f}")
                c3.metric(texto(15), f"{simbolo} {df['Low'].min():,.2f}")
                vol_ultimo = df["Volume"].iloc[-1]
                c4.metric(texto(16), f"{int(vol_ultimo):,}" if pd.notna(vol_ultimo) and vol_ultimo > 0 else "—")

                c5, c6, c7, _ = st.columns(4)
                c5.metric(n("ret_periodo"), f"{ret_periodo:.2f}%")
                c6.metric(n("volat"), f"{vol_anual:.1f}%")
                c7.metric(n("queda_max"), f"{drawdown:.1f}%")

                # Gráfico: candles + médias móveis + volume
                tem_volume = df["Volume"].fillna(0).sum() > 0
                fig = make_subplots(
                    rows=2 if tem_volume else 1, cols=1, shared_xaxes=True,
                    vertical_spacing=0.03, row_heights=[0.75, 0.25] if tem_volume else [1],
                )
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                    name=n("cotacao")), row=1, col=1)
                for janela, cor in ((20, "#f59e0b"), (50, "#6366f1")):
                    if len(df) >= janela:
                        fig.add_trace(go.Scatter(
                            x=df.index, y=fechamento.rolling(janela).mean(),
                            name=f"MM{janela}", line=dict(width=1.5, color=cor)), row=1, col=1)
                if tem_volume:
                    cores = ["#16a34a" if c >= o else "#dc2626" for o, c in zip(df["Open"], df["Close"])]
                    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=cores,
                                         name=n("volume"), opacity=.6), row=2, col=1)
                fig.update_layout(
                    title=f"{texto(17)} - {ticker_custom} ({moeda_exibicao})",
                    yaxis_title=f"{texto(19)} ({moeda_exibicao})",
                    xaxis_rangeslider_visible=False, height=560, autosize=True,
                    margin=dict(l=12, r=12, t=55, b=12), template="plotly_white",
                    paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0)",
                    legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander(texto(20)):
                    tabela = df.sort_index(ascending=False)
                    st.dataframe(tabela, use_container_width=True)
                    st.download_button(
                        n("baixar_csv"), tabela.to_csv().encode("utf-8"),
                        file_name=f"{ticker_custom}_{periodo}.csv", mime="text/csv",
                    )
        except Exception as e:
            st.error(f"{texto(21)}: {e}")

# ---- ABA: RADAR -------------------------------------------------------------
with tab_radar:
    st.header(texto(6))
    st.caption(texto(7))
    with st.spinner(texto(8)):
        ranking = analisar_ativos()
    if ranking.empty:
        st.info(texto(9))
    else:
        top = ranking.iloc[0]
        st.success(f"{texto(10)}: **{top['Ativo']} ({top['Ticker']})**")
        st.dataframe(
            ranking.style.format({
                "Retorno 1 mês (%)": "{:.2f}%", "Retorno 3 meses (%)": "{:.2f}%",
                "Volatilidade anualizada (%)": "{:.2f}%", "Pontuação": "{:.2f}",
            }).background_gradient(subset=["Pontuação"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True,
        )

# ---- ABA: NOTÍCIAS ----------------------------------------------------------
with tab_noticias:
    st.subheader(texto(22))
    with st.spinner("..."):
        noticias = obter_noticias_mercado()
    if noticias:
        cols = st.columns(2)
        for i, nt in enumerate(noticias):
            with cols[i % 2]:
                st.markdown(
                    f"<div class='noticia'><a href='{nt['link']}' target='_blank'>{nt['titulo']}</a>"
                    f"<small>📍 {nt['mercado']} • {nt['fonte']} • {nt['tempo']}</small></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption(texto(23))
