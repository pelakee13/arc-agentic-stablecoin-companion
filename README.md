# 🪙 Arc Agentic Stablecoin Companion

> Your agentic AI guide to USDC, USDT, DAI & DeFi  
> Powered by **Google Gemini 1.5 Flash** — fast, free, and production-ready

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## ✨ Features

| Feature | Description |
|---|---|
| ⛽ **Live Gas Prices** | Real-time Ethereum gas (Slow / Normal / Fast) in the sidebar |
| 💵 **Stablecoin Prices** | Live USDC, USDT, DAI, FRAX prices via CoinGecko |
| 🌐 **Network Status** | Live health checks for CoinGecko, Etherscan, and ETH Gas APIs |
| 🤖 **Gemini 1.5 Flash Chat** | Streaming AI responses with live data context injection |
| ⚡ **Quick Actions** | 8 one-click prompts: gas check, risk analysis, code gen, transfer prep, etc. |
| 📝 **Transaction Simulation** | READ-ONLY transfer preparation — nothing is ever broadcast |
| 💻 **Code Generation** | Python / JavaScript / Solidity snippets for on-chain reads |
| 🛡️ **100% Safe** | No private keys, no write operations, no real transactions |

---

## 🚀 Quick Start

### 1 — Get a free Google API key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API key"**
4. Copy the key (`AIza…`)

> **Free tier limits (as of 2024):** 15 RPM · 1 million tokens/day · no credit card needed

---

### 2 — Deploy to Streamlit Cloud (recommended)

1. **Fork** this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **"New app"**
3. Select your forked repo, branch `main`, file `app.py`
4. Click **"Advanced settings"** → **"Secrets"** and paste:

```toml
GOOGLE_API_KEY = "AIza..."
```

5. Click **"Deploy"** — done! 🎉

---

### 3 — Run locally

```bash
# Clone
git clone https://github.com/your-username/arc-stablecoin-companion
cd arc-stablecoin-companion

# Install dependencies
pip install -r requirements.txt

# Add your secret
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml and paste your GOOGLE_API_KEY

# Run
streamlit run app.py
```

---

## 🗂️ Project Structure

```
arc-stablecoin-companion/
├── app.py                          # Main Streamlit app (Gemini-powered)
├── requirements.txt                # Python dependencies
├── .gitignore                      # Keeps secrets out of git
├── .streamlit/
│   ├── config.toml                 # Arc dark theme
│   └── secrets.toml.example        # Template — copy to secrets.toml
└── README.md
```

---

## 🔧 Migration from Anthropic Claude

This project was migrated from `anthropic` SDK to `google-generativeai`. Here's what changed:

| Before (Anthropic) | After (Google Gemini) |
|---|---|
| `import anthropic` | `import google.generativeai as genai` |
| `ANTHROPIC_API_KEY` secret | `GOOGLE_API_KEY` secret |
| `claude-3-5-haiku-20241022` | `gemini-1.5-flash` |
| `client.messages.create(stream=True)` | `model.start_chat().send_message(stream=True)` |
| System prompt in `system=` param | `system_instruction=` in `GenerativeModel()` |
| Token-level streaming | Chunk-level streaming (same UX) |
| Paid API | **Free tier available** |

---

## 🛡️ Safety & Disclaimer

- **Read-only**: This app never signs or broadcasts any blockchain transaction.
- **No key storage**: Your wallet private keys are never requested or stored.
- **Educational**: Nothing here constitutes financial advice.
- **Verify independently**: Always confirm data on-chain before taking any action.

---

## 📦 Dependencies

```
streamlit>=1.35.0
google-generativeai>=0.7.2
requests>=2.31.0
```

No heavy dependencies — deploys in seconds on Streamlit Cloud.

---

## 🤝 Contributing

PRs welcome! Please open an issue first for major changes.

---

## 📄 License

MIT — free to use, modify, and distribute.
