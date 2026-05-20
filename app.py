"""
Arc Agentic Stablecoin Companion
Powered by Google Gemini 1.5 Flash (free tier)
100% read-only, safe, and educational
"""

import streamlit as st
import google.generativeai as genai
import requests
import json
import time
from datetime import datetime

# ──────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Arc Stablecoin Companion",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS — keep the beautiful Arc UI
# ──────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Global ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1525 50%, #0a1020 100%); }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1525 0%, #111827 100%);
    border-right: 1px solid rgba(99,179,237,0.15);
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  /* ── Chat messages ── */
  [data-testid="stChatMessage"] {
    background: rgba(17,24,39,0.8) !important;
    border: 1px solid rgba(99,179,237,0.12) !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(10px);
  }

  /* ── Metric cards ── */
  [data-testid="metric-container"] {
    background: rgba(17,24,39,0.6) !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
    border-radius: 10px !important;
    padding: 12px !important;
  }

  /* ── Status badges ── */
  .status-online  { color: #68d391; font-weight: 600; }
  .status-offline { color: #fc8181; font-weight: 600; }
  .status-warn    { color: #f6e05e; font-weight: 600; }

  /* ── Tool call card ── */
  .tool-card {
    background: rgba(13,20,40,0.9);
    border: 1px solid rgba(99,179,237,0.25);
    border-left: 3px solid #63b3ed;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.85rem;
    font-family: 'Courier New', monospace;
    color: #90cdf4;
  }

  /* ── Hero header ── */
  .hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #9f7aea, #68d391);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero-sub {
    color: #718096;
    font-size: 0.95rem;
    margin-top: -8px;
  }

  /* ── Quick-action buttons ── */
  .stButton > button {
    background: rgba(99,179,237,0.08) !important;
    border: 1px solid rgba(99,179,237,0.3) !important;
    color: #90cdf4 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 6px 12px !important;
    width: 100%;
    transition: all 0.2s ease;
  }
  .stButton > button:hover {
    background: rgba(99,179,237,0.18) !important;
    border-color: #63b3ed !important;
    color: #bee3f8 !important;
  }

  /* ── Input box ── */
  [data-testid="stChatInput"] textarea {
    background: rgba(17,24,39,0.8) !important;
    border: 1px solid rgba(99,179,237,0.25) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
  }

  /* ── Dividers ── */
  hr { border-color: rgba(99,179,237,0.1) !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(99,179,237,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
ETHERSCAN_API = "https://api.etherscan.io/api"
COINGECKO_API = "https://api.coingecko.com/api/v3"
USDC_CONTRACT  = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # mainnet USDC
USDT_CONTRACT  = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # mainnet USDT
DAI_CONTRACT   = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # mainnet DAI

QUICK_ACTIONS = [
    ("⛽ Check Gas", "What are the current Ethereum gas prices?"),
    ("💰 USDC Price", "What is the current price and market cap of USDC?"),
    ("📊 Stablecoin Overview", "Give me an overview of the top stablecoins: USDC, USDT, and DAI."),
    ("🔍 Explain Yield", "How can I safely earn yield on stablecoins?"),
    ("🛡️ Risk Analysis", "What are the main risks of holding USDC vs USDT vs DAI?"),
    ("🔄 Bridge Guide", "How do I bridge USDC between Ethereum and other chains?"),
    ("📝 Prepare Transfer", "Help me prepare a USDC transfer transaction (read-only simulation)."),
    ("💻 Generate Code", "Generate Python code to check a wallet's USDC balance using web3.py."),
]

SYSTEM_PROMPT = """You are the Arc Agentic Stablecoin Companion — an expert, friendly AI assistant
specialised in stablecoins (USDC, USDT, DAI, FRAX, etc.) and DeFi on Ethereum and EVM chains.

PERSONALITY
• Precise, concise, and educational
• Always mention risk when relevant
• Never give financial advice — educate instead
• Use emojis sparingly but effectively

CAPABILITIES YOU SIMULATE (read-only, no real transactions)
1. Gas price analysis & estimation
2. Wallet balance lookups (via public APIs)
3. Stablecoin price & market data
4. Transaction preparation (simulation only — never broadcast)
5. Smart contract ABI explanations
6. Code generation (Python/JS/Solidity snippets)
7. DeFi protocol comparisons
8. Bridge & cross-chain guidance

SAFETY RULES (ABSOLUTE)
• Never ask for private keys, seed phrases, or passwords
• Mark all transaction simulations clearly as READ-ONLY / NOT BROADCAST
• Warn users to verify on-chain before any real action
• Never promise specific yields or returns

When showing a tool call or agentic step, format it like:
🔧 TOOL: <tool name>
📥 INPUT: <parameters>
📤 OUTPUT: <result>

When generating code, always add safety comments and never include real private keys.
"""

# ──────────────────────────────────────────────
# Helper: live data fetchers (read-only)
# ──────────────────────────────────────────────

@st.cache_data(ttl=30)
def fetch_gas_prices() -> dict:
    """Fetch current gas prices from Ethereum Gas Station (free, no key)."""
    try:
        r = requests.get(
            "https://api.blocknative.com/gasprices/blockprices",
            headers={"Authorization": ""},
            timeout=5,
        )
        # Fallback to ethgasstation-style endpoint
        r2 = requests.get(
            "https://ethgas.watch/api/gas",
            timeout=5,
        )
        if r2.status_code == 200:
            d = r2.json()
            return {
                "slow":   d.get("slow",  {}).get("gwei", "N/A"),
                "normal": d.get("normal",{}).get("gwei", "N/A"),
                "fast":   d.get("fast",  {}).get("gwei", "N/A"),
                "source": "ethgas.watch",
                "ok": True,
            }
    except Exception:
        pass
    # Secondary fallback
    try:
        r = requests.get(
            f"{ETHERSCAN_API}?module=gastracker&action=gasoracle",
            timeout=5,
        )
        if r.status_code == 200:
            d = r.json().get("result", {})
            return {
                "slow":   d.get("SafeGasPrice", "N/A"),
                "normal": d.get("ProposeGasPrice", "N/A"),
                "fast":   d.get("FastGasPrice", "N/A"),
                "source": "Etherscan (no key)",
                "ok": True,
            }
    except Exception:
        pass
    return {"ok": False, "slow": "N/A", "normal": "N/A", "fast": "N/A"}


@st.cache_data(ttl=60)
def fetch_stablecoin_prices() -> dict:
    """Fetch stablecoin market data from CoinGecko (free, no key)."""
    try:
        ids = "usd-coin,tether,dai,frax,true-usd"
        r = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={"ids": ids, "vs_currencies": "usd", "include_market_cap": "true", "include_24hr_change": "true"},
            timeout=6,
        )
        if r.status_code == 200:
            return {"ok": True, "data": r.json()}
    except Exception:
        pass
    return {"ok": False, "data": {}}


@st.cache_data(ttl=120)
def fetch_eth_price() -> float | None:
    try:
        r = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={"ids": "ethereum", "vs_currencies": "usd"},
            timeout=5,
        )
        if r.status_code == 200:
            return r.json().get("ethereum", {}).get("usd")
    except Exception:
        pass
    return None


def check_network_status() -> dict:
    """Quick connectivity check."""
    results = {}
    checks = {
        "CoinGecko": "https://api.coingecko.com/api/v3/ping",
        "Etherscan":  f"{ETHERSCAN_API}?module=stats&action=ethprice",
        "ETH Gas":    "https://ethgas.watch/api/gas",
    }
    for name, url in checks.items():
        try:
            r = requests.get(url, timeout=4)
            results[name] = r.status_code == 200
        except Exception:
            results[name] = False
    return results

# ──────────────────────────────────────────────
# Gemini setup
# ──────────────────────────────────────────────

def get_gemini_client():
    """Initialise Gemini with the API key from Streamlit secrets."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False


def get_or_create_chat():
    """Return a persistent Gemini chat session stored in session state."""
    if "gemini_chat" not in st.session_state:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ],
        )
        st.session_state.gemini_chat = model.start_chat(history=[])
    return st.session_state.gemini_chat


def stream_gemini_response(chat, user_message: str):
    """Stream a response from Gemini and yield text chunks."""
    response = chat.send_message(user_message, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Logo / title
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px 0;'>
          <div style='font-size:2.4rem;'>🪙</div>
          <div style='font-weight:700; font-size:1.1rem; color:#90cdf4;'>Arc Stablecoin</div>
          <div style='font-size:0.78rem; color:#718096;'>Agentic Companion</div>
          <div style='margin-top:6px; font-size:0.7rem; background:rgba(104,211,145,0.12);
               border:1px solid rgba(104,211,145,0.3); border-radius:20px; padding:2px 10px;
               color:#68d391; display:inline-block;'>✨ Gemini 1.5 Flash</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Live network status ──
        st.markdown("**🌐 Network Status**")
        if st.button("🔄 Refresh", key="refresh_net", use_container_width=True):
            st.cache_data.clear()

        with st.spinner("Checking…"):
            net = check_network_status()

        for service, online in net.items():
            badge = '<span class="status-online">● Online</span>' if online else '<span class="status-offline">● Offline</span>'
            st.markdown(f"<small>{service}: {badge}</small>", unsafe_allow_html=True)

        st.divider()

        # ── Live gas prices ──
        st.markdown("**⛽ Live Gas (Gwei)**")
        gas = fetch_gas_prices()
        if gas["ok"]:
            c1, c2, c3 = st.columns(3)
            c1.metric("Slow",   gas["slow"])
            c2.metric("Normal", gas["normal"])
            c3.metric("Fast",   gas["fast"])
            st.caption(f"Source: {gas.get('source','—')}")
        else:
            st.warning("Gas data unavailable")

        st.divider()

        # ── ETH price ──
        eth_price = fetch_eth_price()
        if eth_price:
            st.metric("Ξ ETH Price", f"${eth_price:,.2f}")
            st.divider()

        # ── Stablecoin prices ──
        st.markdown("**💵 Stablecoin Prices**")
        prices = fetch_stablecoin_prices()
        if prices["ok"]:
            name_map = {
                "usd-coin": ("USDC", "🔵"),
                "tether":   ("USDT", "🟢"),
                "dai":      ("DAI",  "🟡"),
                "frax":     ("FRAX", "⚪"),
            }
            for cg_id, (ticker, icon) in name_map.items():
                d = prices["data"].get(cg_id, {})
                price  = d.get("usd", "—")
                change = d.get("usd_24h_change", 0) or 0
                arrow  = "▲" if change >= 0 else "▼"
                color  = "#68d391" if change >= 0 else "#fc8181"
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;font-size:0.82rem;'>"
                    f"<span>{icon} {ticker}</span>"
                    f"<span>${price:.4f} <span style='color:{color};font-size:0.7rem;'>{arrow}{abs(change):.3f}%</span></span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Price data unavailable")

        st.divider()

        # ── Session info ──
        msg_count = len(st.session_state.get("messages", []))
        st.caption(f"💬 {msg_count} messages this session")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if "gemini_chat" in st.session_state:
                del st.session_state["gemini_chat"]
            st.rerun()

        st.divider()
        st.markdown(
            "<div style='font-size:0.65rem;color:#4a5568;text-align:center;'>"
            "100% Read-Only · No transactions broadcast<br>"
            "Powered by Google Gemini 1.5 Flash"
            "</div>",
            unsafe_allow_html=True,
        )

# ──────────────────────────────────────────────
# Main app
# ──────────────────────────────────────────────

def main():
    # Initialise Gemini
    gemini_ready = get_gemini_client()

    # Render sidebar
    render_sidebar()

    # ── Hero header ──
    st.markdown("""
    <div style='padding: 8px 0 4px 0;'>
      <div class='hero-title'>🪙 Arc Stablecoin Companion</div>
      <div class='hero-sub'>Your agentic AI guide to USDC, USDT, DAI & DeFi — powered by Gemini 1.5 Flash</div>
    </div>
    """, unsafe_allow_html=True)

    # ── API key warning ──
    if not gemini_ready:
        st.error(
            "⚠️ **Google API Key not found.** "
            "Add `GOOGLE_API_KEY` to your Streamlit secrets "
            "(`Settings → Secrets` on Streamlit Cloud, or `.streamlit/secrets.toml` locally)."
        )
        st.code("""# .streamlit/secrets.toml
GOOGLE_API_KEY = "AIza..."
""", language="toml")
        st.stop()

    # ── Quick-action buttons ──
    st.markdown("**⚡ Quick Actions**")
    cols = st.columns(4)
    for i, (label, prompt) in enumerate(QUICK_ACTIONS):
        if cols[i % 4].button(label, key=f"qa_{i}"):
            st.session_state.setdefault("messages", [])
            st.session_state["pending_prompt"] = prompt

    st.divider()

    # ── Chat history ──
    st.session_state.setdefault("messages", [])

    # Welcome message on first load
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🪙"):
            st.markdown(
                "👋 **Welcome to the Arc Stablecoin Companion!**\n\n"
                "I can help you with:\n"
                "- 📊 **Market data** — live stablecoin prices, gas fees, ETH price\n"
                "- 🔍 **Education** — how USDC, USDT, DAI, and DeFi protocols work\n"
                "- 🛡️ **Risk analysis** — compare stablecoins by safety, yield, and liquidity\n"
                "- 💻 **Code generation** — Python/JS/Solidity snippets for on-chain reads\n"
                "- 📝 **Transaction simulation** — prepare transfers (read-only, never broadcast)\n\n"
                "Use the **Quick Actions** above or type your question below!"
            )

    # Render existing messages
    for msg in st.session_state.messages:
        avatar = "🪙" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ── Handle pending quick-action prompt ──
    pending = st.session_state.pop("pending_prompt", None)
    user_input = pending or st.chat_input("Ask about stablecoins, gas, DeFi, code…")

    if user_input:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Enrich prompt with live context if relevant keywords found
        keywords = ["gas", "price", "usdc", "usdt", "dai", "eth", "gwei", "cost"]
        if any(kw in user_input.lower() for kw in keywords):
            gas    = fetch_gas_prices()
            prices = fetch_stablecoin_prices()
            eth_p  = fetch_eth_price()

            context_parts = ["\n\n---\n📡 LIVE DATA CONTEXT (fetched just now):"]
            if gas["ok"]:
                context_parts.append(
                    f"• Gas prices — Slow: {gas['slow']} Gwei, Normal: {gas['normal']} Gwei, Fast: {gas['fast']} Gwei"
                )
            if eth_p:
                context_parts.append(f"• ETH price: ${eth_p:,.2f}")
            if prices["ok"]:
                pd = prices["data"]
                for cg_id, ticker in [("usd-coin","USDC"),("tether","USDT"),("dai","DAI")]:
                    d = pd.get(cg_id, {})
                    if d:
                        context_parts.append(
                            f"• {ticker}: ${d.get('usd','N/A'):.4f} (24h: {d.get('usd_24h_change',0):.4f}%)"
                        )
            context_parts.append("---")
            enriched_prompt = user_input + "\n".join(context_parts)
        else:
            enriched_prompt = user_input

        # Stream Gemini response
        chat = get_or_create_chat()
        with st.chat_message("assistant", avatar="🪙"):
            placeholder = st.empty()
            full_response = ""
            try:
                for chunk in stream_gemini_response(chat, enriched_prompt):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                err = str(e)
                if "quota" in err.lower() or "429" in err:
                    placeholder.error("⏳ Rate limit hit. Please wait a moment and try again.")
                    full_response = "_(rate limited — please retry in a few seconds)_"
                elif "api_key" in err.lower() or "401" in err:
                    placeholder.error("🔑 Invalid API key. Check your `GOOGLE_API_KEY` in secrets.")
                    full_response = "_(authentication error)_"
                else:
                    placeholder.error(f"❌ Gemini error: {err}")
                    full_response = f"_(error: {err})_"

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()


if __name__ == "__main__":
    main()
