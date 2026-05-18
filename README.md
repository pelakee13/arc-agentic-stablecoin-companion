# 🔵 Arc Agentic Stablecoin Companion

> **Ignyte Stablecoins Commerce Stack Challenge — Agentic Economy Track**

An autonomous AI agent for stablecoin commerce on **Arc Testnet**. Demonstrates real-time wallet intelligence, gas analysis, transfer preparation, and code generation — all powered by live Arc network data and Claude AI.

---

## 🎯 Competition Alignment

| Challenge Requirement | How We Deliver |
|---|---|
| Stablecoin-native commerce | USDC as gas + payment token; EURC, USYC supported |
| Agentic Economy | AI agent that reasons, fetches data, and prepares autonomous transactions |
| Arc Testnet integration | Direct JSON-RPC calls to `rpc.testnet.arc.network` |
| Real-time data | Live block number, gas price, wallet balances every refresh |
| Safe & production-ready | 100% read-only; no private keys in app |

---

## ✨ Features

### Live Sidebar
- **Network status** (online/offline badge)
- **Latest block number** (auto-refreshes every 15s)
- **Current gas price** in Gwei and USD
- **Chain ID** confirmation (5042002)
- **Contract addresses** for USDC, EURC, USYC
- Links to ArcScan, Gas Tracker, Circle Faucet

### AI Agent Chat
The Claude-powered agent can:

- **Check any wallet balance** — USDC (ERC-20), EURC, USYC, and native USDC gas balance
- **Analyze gas conditions** — fetches live gas price, advises if it's safe to transact
- **Prepare USDC transfers** — full breakdown (amount, gas estimate, fee in USD, contract address) — ready for user to execute with their own wallet
- **Generate production code** — ethers.js, web3.py, and viem snippets with Arc-correct parameters
- **Monitor recent blocks** — last 5 blocks with timestamps, tx counts, gas usage
- **Explain agentic commerce** — how AI agents can autonomously coordinate stablecoin payments on Arc

### Quick Actions
One-click prompts for the most common agentic use cases:
- Gas check
- Wallet balance lookup
- Agentic payment demo
- Recent block monitor

---

## 🚀 Deploy on Streamlit Cloud

### 1. Clone & configure

```bash
git clone https://github.com/your-org/arc-agentic-companion
cd arc-agentic-companion
```

### 2. Set your Anthropic API key

In Streamlit Cloud, go to **App settings → Secrets** and add:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Or locally, copy `.streamlit/secrets.toml.template` → `.streamlit/secrets.toml` and fill in your key.

### 3. Deploy

Push to GitHub and connect to [share.streamlit.io](https://share.streamlit.io). Set:
- **Main file**: `app.py`
- **Python version**: 3.11+

### 4. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🏗️ Architecture

```
arc-companion/
├── app.py                    # Full Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml           # Dark theme + server config
│   └── secrets.toml.template # API key template
└── README.md
```

### Data flow

```
User input → Claude AI Agent
                ↓
         [TOOL:check_wallet:0x...]
         [TOOL:check_gas]
         [TOOL:prepare_transfer:...]
         [TOOL:check_blocks]
                ↓
         Arc Testnet JSON-RPC
         (rpc.testnet.arc.network)
                ↓
         eth_getBalance / eth_call / eth_gasPrice / eth_blockNumber
                ↓
         Rendered in Streamlit UI
```

---

## 🔗 Arc Testnet Reference

| Parameter | Value |
|---|---|
| RPC URL | `https://rpc.testnet.arc.network` |
| Chain ID | `5042002` |
| USDC | `0x3600000000000000000000000000000000000000` |
| EURC | `0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a` |
| USYC | `0xe9185F0c5F296Ed1797AaE4238D26CCaBEadb86C` |
| Explorer | `https://testnet.arcscan.app` |
| Faucet | `https://faucet.circle.com` |

---

## 🤖 Agentic Economy Use Cases

This app demonstrates the core patterns for autonomous stablecoin commerce:

1. **Agent balance monitoring** — AI continuously checks if an agent wallet has enough USDC to operate
2. **Gas-aware transaction preparation** — agent evaluates gas before committing to a payment
3. **Machine-to-machine settlement** — shows how agents can prepare and batch USDC transfers without human involvement
4. **Code generation** — AI produces ready-to-deploy agent code for Arc

---

## 🔒 Security

- **No private keys** — the app never requests, stores, or handles signing keys
- **Read-only RPC** — only `eth_call`, `eth_getBalance`, `eth_blockNumber`, `eth_gasPrice`, `eth_estimateGas` are used
- **No transactions** — the app cannot submit transactions to the network
- **User confirmation required** — transfer preparation is surfaced for human review before any off-app execution

---

*Built for the Ignyte Stablecoins Commerce Stack Challenge · Agentic Economy Track*
