"""
Arc Agentic Stablecoin Companion
Competition entry: Ignyte Stablecoins Commerce Stack Challenge — Agentic Economy track
"""

import streamlit as st
import requests
import json
import time
import re
from datetime import datetime
from anthropic import Anthropic

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
ARC_RPC = "https://rpc.testnet.arc.network"
CHAIN_ID = 5042002
EXPLORER = "https://testnet.arcscan.app"
GAS_TRACKER = "https://testnet.arcscan.app/gas-tracker"
FAUCET = "https://faucet.circle.com"

USDC_CONTRACT = "0x3600000000000000000000000000000000000000"
EURC_CONTRACT = "0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a"
USYC_CONTRACT = "0xe9185F0c5F296Ed1797AaE4238D26CCaBEadb86C"
MULTICALL3    = "0xcA11bde05977b3631167028862bE2a173976CA11"

USDC_ABI_BALANCEOF = "0x70a08231"  # balanceOf(address)
ERC20_DECIMALS_SIG = "0x313ce567"  # decimals()

MODEL = "claude-sonnet-4-20250514"

# ─────────────────────────────────────────────
# Streamlit page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Arc Agentic Stablecoin Companion",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Dark-mode professional CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* Base */
  :root {
    --arc-blue: #3B82F6;
    --arc-cyan: #06B6D4;
    --arc-green: #10B981;
    --arc-yellow: #F59E0B;
    --arc-red: #EF4444;
    --bg-deep: #0A0F1E;
    --bg-card: #111827;
    --bg-input: #1F2937;
    --border: #374151;
    --text-primary: #F9FAFB;
    --text-muted: #9CA3AF;
  }

  .stApp { background-color: var(--bg-deep); color: var(--text-primary); }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #111827 100%);
    border-right: 1px solid var(--border);
  }

  /* Metric cards */
  .metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
  }
  .metric-label { color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
  .metric-value { color: var(--text-primary); font-size: 18px; font-weight: 700; font-family: 'SF Mono', monospace; }
  .metric-sub   { color: var(--text-muted); font-size: 11px; margin-top: 2px; }

  /* Status badge */
  .status-online  { background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.3); border-radius: 20px; padding: 3px 10px; font-size: 12px; font-weight: 600; display: inline-block; }
  .status-offline { background: rgba(239,68,68,0.15); color: #EF4444; border: 1px solid rgba(239,68,68,0.3); border-radius: 20px; padding: 3px 10px; font-size: 12px; font-weight: 600; display: inline-block; }

  /* Chat bubbles */
  .chat-user {
    background: linear-gradient(135deg, #1E3A5F, #1E40AF);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 8px 0 8px 20%;
    color: #F9FAFB;
    font-size: 14px;
    line-height: 1.6;
  }
  .chat-assistant {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 14px 18px;
    margin: 8px 20% 8px 0;
    color: #F9FAFB;
    font-size: 14px;
    line-height: 1.6;
  }
  .chat-role { font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px; }
  .chat-role-user { color: #93C5FD; }
  .chat-role-ai   { color: #6EE7B7; }

  /* Code blocks inside chat */
  .chat-assistant pre, .chat-assistant code {
    background: #0D1117;
    border: 1px solid #30363D;
    border-radius: 8px;
    font-size: 13px;
    color: #E2E8F0;
  }

  /* Alert boxes */
  .alert-info    { background: rgba(59,130,246,0.1); border-left: 3px solid #3B82F6; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
  .alert-success { background: rgba(16,185,129,0.1); border-left: 3px solid #10B981; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
  .alert-warning { background: rgba(245,158,11,0.1); border-left: 3px solid #F59E0B; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
  .alert-danger  { background: rgba(239,68,68,0.1); border-left: 3px solid #EF4444; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }

  /* Title banner */
  .arc-banner {
    background: linear-gradient(135deg, #0D1B3E 0%, #1E3A5F 50%, #0D1B3E 100%);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    text-align: center;
  }
  .arc-banner h1 { font-size: 28px; font-weight: 800; color: #F9FAFB; margin: 0 0 6px; }
  .arc-banner p  { color: #93C5FD; margin: 0; font-size: 14px; }

  /* Tag chips */
  .tag { display: inline-block; background: rgba(59,130,246,0.15); color: #93C5FD; border: 1px solid rgba(59,130,246,0.3); border-radius: 12px; padding: 2px 10px; font-size: 11px; font-weight: 600; margin: 2px; }

  /* Suggestion buttons */
  div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-input) !important;
    color: var(--text-primary) !important;
    font-size: 13px !important;
    transition: all 0.15s;
  }
  div[data-testid="stButton"] > button:hover {
    border-color: var(--arc-blue) !important;
    background: rgba(59,130,246,0.1) !important;
  }

  /* Scrollable chat */
  .chat-container { max-height: 520px; overflow-y: auto; padding-right: 4px; }

  /* Section headers */
  .section-header {
    color: var(--text-muted);
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 16px 0 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
  }

  /* Confirmation box */
  .confirm-box {
    background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(245,158,11,0.04));
    border: 1px solid rgba(245,158,11,0.35);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RPC helpers
# ─────────────────────────────────────────────
def rpc_call(method: str, params: list = None, timeout: int = 6):
    """Send a JSON-RPC call to Arc Testnet."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
    try:
        r = requests.post(ARC_RPC, json=payload, timeout=timeout)
        data = r.json()
        return data.get("result"), None
    except Exception as e:
        return None, str(e)


def hex_to_int(h) -> int | None:
    if h is None:
        return None
    try:
        return int(h, 16)
    except Exception:
        return None


def gwei_to_usdc(gwei: int) -> float:
    """Convert Gwei (18-decimal) to human USDC cents."""
    return gwei / 1e9 / 1e9  # 1 Gwei = 1e-9 USDC (18-dec)


def fetch_network_status() -> dict:
    """Fetch live network metrics from Arc RPC."""
    block_hex, e1 = rpc_call("eth_blockNumber")
    gas_hex, e2   = rpc_call("eth_gasPrice")
    chain_hex, _  = rpc_call("eth_chainId")

    block  = hex_to_int(block_hex) if block_hex else None
    gas_gw = hex_to_int(gas_hex)  if gas_hex  else None
    chain  = hex_to_int(chain_hex) if chain_hex else None

    online = block is not None

    gas_gwei_val = gas_gw / 1e9 if gas_gw else None
    gas_usd = gas_gw * 21000 / 1e18 if gas_gw else None  # simple transfer cost

    return {
        "online": online,
        "block": block,
        "chain_id": chain,
        "gas_price_raw": gas_gw,
        "gas_gwei": gas_gwei_val,
        "gas_usd_transfer": gas_usd,
        "rpc": ARC_RPC,
        "error": e1 or e2,
    }


def pad_address(addr: str) -> str:
    """Pad an Ethereum address to 32-byte ABI encoding."""
    return addr.lower().replace("0x", "").zfill(64)


def erc20_balance(token: str, wallet: str) -> tuple[float | None, str | None]:
    """
    Read ERC-20 balanceOf for a token on Arc.
    Returns (human_balance, error).
    """
    data = USDC_ABI_BALANCEOF + pad_address(wallet)
    result, err = rpc_call("eth_call", [{"to": token, "data": data}, "latest"])
    if err:
        return None, err
    if not result or result == "0x":
        return 0.0, None
    raw = int(result, 16)
    # All stablecoins on Arc ERC-20 interface use 6 decimals
    return raw / 1e6, None


def native_balance(wallet: str) -> tuple[float | None, str | None]:
    """
    Read native USDC balance (18-dec gas accounting).
    Returns (human_balance, error).
    """
    result, err = rpc_call("eth_getBalance", [wallet, "latest"])
    if err:
        return None, err
    if not result:
        return 0.0, None
    raw = int(result, 16)
    return raw / 1e18, None


def fetch_wallet_balances(wallet: str) -> dict:
    """Fetch USDC, EURC, USYC balances for a wallet."""
    wallet = wallet.strip()
    usdc_erc20, e1 = erc20_balance(USDC_CONTRACT, wallet)
    eurc, e2 = erc20_balance(EURC_CONTRACT, wallet)
    usyc, e3 = erc20_balance(USYC_CONTRACT, wallet)
    native, e4 = native_balance(wallet)

    return {
        "wallet": wallet,
        "usdc_erc20": usdc_erc20,
        "eurc": eurc,
        "usyc": usyc,
        "native_usdc": native,
        "errors": [e for e in [e1, e2, e3, e4] if e],
    }


def estimate_transfer_gas(from_addr: str, to_addr: str, amount_usdc: float) -> dict:
    """Estimate gas for a USDC ERC-20 transfer."""
    amount_raw = int(amount_usdc * 1e6)
    # ERC-20 transfer(address,uint256) = 0xa9059cbb
    data = "0xa9059cbb" + pad_address(to_addr) + hex(amount_raw)[2:].zfill(64)
    result, err = rpc_call("eth_estimateGas", [{"from": from_addr, "to": USDC_CONTRACT, "data": data}])
    gas_price_raw, _ = rpc_call("eth_gasPrice", [])

    gas_limit = hex_to_int(result) if result else 65000
    gas_price  = hex_to_int(gas_price_raw) if gas_price_raw else int(20e9)
    fee_usdc   = gas_limit * gas_price / 1e18

    return {
        "gas_limit": gas_limit,
        "gas_price_gwei": gas_price / 1e9,
        "fee_usdc": fee_usdc,
        "error": err,
    }


def fetch_recent_blocks(count: int = 5) -> list[dict]:
    """Fetch the last N block headers."""
    block_hex, _ = rpc_call("eth_blockNumber")
    if not block_hex:
        return []
    latest = hex_to_int(block_hex)
    blocks = []
    for i in range(count):
        num = latest - i
        result, _ = rpc_call("eth_getBlockByNumber", [hex(num), False])
        if result:
            ts  = hex_to_int(result.get("timestamp", "0x0"))
            gas = hex_to_int(result.get("gasUsed", "0x0"))
            blocks.append({
                "number": num,
                "timestamp": datetime.fromtimestamp(ts).strftime("%H:%M:%S") if ts else "?",
                "txs": len(result.get("transactions", [])),
                "gas_used": gas,
            })
    return blocks


# ─────────────────────────────────────────────
# System prompt for the AI agent
# ─────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are the Arc Agentic Stablecoin Companion — an expert autonomous AI agent for the Arc Testnet, purpose-built for the Ignyte Stablecoins Commerce Stack Challenge (Agentic Economy track).

## Your identity
You help developers, merchants, and autonomous agents work with stablecoins on Arc Testnet. You reason autonomously, fetch live data, and generate production-ready code.

## Arc Testnet facts you know
- **RPC**: {ARC_RPC}
- **Chain ID**: {CHAIN_ID}
- **Explorer**: {EXPLORER}
- **Gas tracker**: {GAS_TRACKER}
- **USDC ERC-20**: `{USDC_CONTRACT}` (6 decimals) — also native gas token (18 decimals)
- **EURC**: `{EURC_CONTRACT}` (6 decimals)
- **USYC**: `{USYC_CONTRACT}` (6 decimals)
- **Gas model**: EIP-1559 + EWMA smoothing. Base fee ≈ $0.01/tx. Min base fee = 20 Gwei.
- **Simple transfer cost**: ~$0.0001–0.001 USDC
- **Finality**: sub-second deterministic
- **Faucet**: {FAUCET}

## Capabilities
1. **Balance checks** — when asked for a wallet's balance, call the `check_wallet` tool with the address.
2. **Gas analysis** — call `check_gas` to get current gas price and advise if it's good for sending.
3. **Transfer preparation** — when a user wants to send USDC, use `prepare_transfer` to build and validate the transaction details. NEVER execute transactions or ask for private keys.
4. **Code generation** — generate ethers.js / web3.py / viem code for stablecoin operations on Arc.
5. **Autonomous monitoring** — proactively assess conditions (gas, balance sufficiency, network health).

## Rules
- You are FULLY READ-ONLY. Never ask for or accept private keys, seed phrases, or signing authority.
- Always surface gas costs in USDC dollars, not raw Gwei.
- When generating transfer code, always include the 20 Gwei minimum maxFeePerGas.
- Format all addresses as checksummed lowercase with `0x` prefix.
- Be concise and agentic — show your reasoning, then act.
- When you detect issues (low balance, high gas, wrong network), proactively warn the user.
- Use markdown formatting with code blocks for code snippets.
- For the Agentic Economy: emphasize how autonomous agents can use Arc for machine-to-machine payments, programmatic settlements, and zero-human-intervention commerce.

## Tool usage
The app calls specific Python functions based on keywords you include in your response. Signal tool calls by including one of:
- `[TOOL:check_wallet:0x...]` — to trigger a balance check
- `[TOOL:check_gas]` — to trigger a gas check
- `[TOOL:prepare_transfer:from_addr:to_addr:amount]` — to prepare a transfer
- `[TOOL:check_blocks]` — to fetch recent blocks

Always reason out loud before using a tool. After tool results are injected, analyze them and give the user a clear, actionable answer.
"""


# ─────────────────────────────────────────────
# AI agent + tool dispatch
# ─────────────────────────────────────────────
client = Anthropic()


def parse_and_execute_tools(text: str) -> tuple[str, list[dict]]:
    """
    Scan assistant response for [TOOL:...] markers, execute them,
    and return (augmented_text, tool_results).
    """
    tool_results = []

    # check_wallet
    for m in re.finditer(r"\[TOOL:check_wallet:(0x[0-9a-fA-F]{40})\]", text):
        addr = m.group(1)
        data = fetch_wallet_balances(addr)
        tool_results.append({"type": "wallet", "data": data})
        text = text.replace(m.group(0), f"[✓ Fetched balances for {addr[:10]}…]")

    # check_gas
    if "[TOOL:check_gas]" in text:
        ns = fetch_network_status()
        tool_results.append({"type": "gas", "data": ns})
        text = text.replace("[TOOL:check_gas]", "[✓ Fetched live gas data]")

    # prepare_transfer
    for m in re.finditer(r"\[TOOL:prepare_transfer:(0x[0-9a-fA-F]{40}):(0x[0-9a-fA-F]{40}):(\d+(?:\.\d+)?)\]", text):
        from_a, to_a, amt = m.group(1), m.group(2), float(m.group(3))
        est = estimate_transfer_gas(from_a, to_a, amt)
        tool_results.append({"type": "transfer", "data": {"from": from_a, "to": to_a, "amount": amt, **est}})
        text = text.replace(m.group(0), "[✓ Transfer prepared]")

    # check_blocks
    if "[TOOL:check_blocks]" in text:
        blocks = fetch_recent_blocks(5)
        tool_results.append({"type": "blocks", "data": blocks})
        text = text.replace("[TOOL:check_blocks]", "[✓ Fetched recent blocks]")

    return text, tool_results


def run_agent(messages: list[dict]) -> tuple[str, list[dict]]:
    """Run the AI agent and return (response_text, tool_results)."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    raw_text = response.content[0].text
    processed_text, tool_results = parse_and_execute_tools(raw_text)
    return processed_text, tool_results


# ─────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────
def render_tool_result(tr: dict):
    t = tr["type"]
    d = tr["data"]

    if t == "wallet":
        w = d["wallet"]
        st.markdown(f"""
        <div class='alert-info'>
          <div style='font-size:11px;color:#93C5FD;font-weight:700;margin-bottom:6px;'>💼 WALLET BALANCES — {w[:16]}…{w[-6:]}</div>
          <table style='width:100%;font-size:13px;'>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>USDC (ERC-20)</td><td style='color:#F9FAFB;font-weight:600;font-family:monospace;'>{f"{d['usdc_erc20']:,.4f}" if d['usdc_erc20'] is not None else "—"} USDC</td></tr>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>EURC</td><td style='color:#F9FAFB;font-weight:600;font-family:monospace;'>{f"{d['eurc']:,.4f}" if d['eurc'] is not None else "—"} EURC</td></tr>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>USYC</td><td style='color:#F9FAFB;font-weight:600;font-family:monospace;'>{f"{d['usyc']:,.4f}" if d['usyc'] is not None else "—"} USYC</td></tr>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>Native USDC (gas)</td><td style='color:#F9FAFB;font-weight:600;font-family:monospace;'>{f"{d['native_usdc']:,.6f}" if d['native_usdc'] is not None else "—"} USDC</td></tr>
          </table>
          <div style='margin-top:6px;'><a href='{EXPLORER}/address/{w}' target='_blank' style='color:#60A5FA;font-size:11px;'>View on ArcScan ↗</a></div>
        </div>
        """, unsafe_allow_html=True)

    elif t == "gas":
        ok = d["online"]
        gw = d.get("gas_gwei")
        usd = d.get("gas_usd_transfer")
        color = "#10B981" if (gw or 0) < 50 else "#F59E0B"
        st.markdown(f"""
        <div class='alert-{"success" if ok else "danger"}'>
          <div style='font-size:11px;color:#6EE7B7;font-weight:700;margin-bottom:6px;'>⛽ LIVE GAS STATUS</div>
          <table style='width:100%;font-size:13px;'>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>Network</td><td><span class='{"status-online" if ok else "status-offline"}'>{"● ONLINE" if ok else "● OFFLINE"}</span></td></tr>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>Gas Price</td><td style='color:{color};font-weight:700;font-family:monospace;'>{f"{gw:.2f} Gwei" if gw else "—"}</td></tr>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>Transfer Cost</td><td style='color:#F9FAFB;font-weight:600;font-family:monospace;'>{f"~${usd:.6f} USDC" if usd else "—"}</td></tr>
            <tr><td style='color:#9CA3AF;padding:3px 8px 3px 0;'>Block</td><td style='color:#F9FAFB;font-family:monospace;'>{d.get("block", "—")}</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    elif t == "transfer":
        st.markdown(f"""
        <div class='confirm-box'>
          <div style='font-size:11px;color:#FCD34D;font-weight:700;margin-bottom:8px;'>📋 TRANSFER PREPARATION — REVIEW BEFORE SIGNING</div>
          <table style='width:100%;font-size:13px;'>
            <tr><td style='color:#9CA3AF;padding:4px 8px 4px 0;'>From</td><td style='color:#F9FAFB;font-family:monospace;font-size:12px;'>{d['from']}</td></tr>
            <tr><td style='color:#9CA3AF;padding:4px 8px 4px 0;'>To</td><td style='color:#F9FAFB;font-family:monospace;font-size:12px;'>{d['to']}</td></tr>
            <tr><td style='color:#9CA3AF;padding:4px 8px 4px 0;'>Amount</td><td style='color:#10B981;font-weight:700;'>{d['amount']:,.2f} USDC</td></tr>
            <tr><td style='color:#9CA3AF;padding:4px 8px 4px 0;'>Est. Gas</td><td style='color:#F9FAFB;font-family:monospace;'>{d.get("gas_limit","—")} units @ {d.get("gas_price_gwei",0):.1f} Gwei</td></tr>
            <tr><td style='color:#9CA3AF;padding:4px 8px 4px 0;'>Est. Fee</td><td style='color:#F59E0B;font-weight:600;'>~${d.get("fee_usdc",0):.6f} USDC</td></tr>
            <tr><td style='color:#9CA3AF;padding:4px 8px 4px 0;'>Contract</td><td style='color:#60A5FA;font-family:monospace;font-size:11px;'>{USDC_CONTRACT}</td></tr>
          </table>
          <div style='margin-top:10px;font-size:12px;color:#FCD34D;'>⚠️ This app is read-only. To execute, use the generated code with your own wallet/signer.</div>
        </div>
        """, unsafe_allow_html=True)

    elif t == "blocks":
        rows = "".join([
            f"<tr><td style='font-family:monospace;color:#93C5FD;'>{b['number']}</td>"
            f"<td style='color:#9CA3AF;'>{b['timestamp']}</td>"
            f"<td style='color:#F9FAFB;'>{b['txs']}</td>"
            f"<td style='color:#9CA3AF;font-size:11px;'>{b['gas_used']:,}</td></tr>"
            for b in d
        ])
        st.markdown(f"""
        <div class='alert-info'>
          <div style='font-size:11px;color:#93C5FD;font-weight:700;margin-bottom:6px;'>🧱 RECENT BLOCKS</div>
          <table style='width:100%;font-size:12px;border-collapse:collapse;'>
            <tr style='color:#6B7280;font-size:10px;'><th style='text-align:left;padding:2px 8px 6px 0;'>BLOCK</th><th style='text-align:left;padding:2px 8px 6px 0;'>TIME</th><th style='text-align:left;padding:2px 8px 6px 0;'>TXS</th><th style='text-align:left;'>GAS USED</th></tr>
            {rows}
          </table>
        </div>
        """, unsafe_allow_html=True)


def render_chat_message(role: str, content: str, tool_results: list = None):
    if role == "user":
        st.markdown(f"""
        <div class='chat-user'>
          <div class='chat-role chat-role-user'>You</div>
          {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='chat-assistant'>
          <div class='chat-role chat-role-ai'>🔵 Arc AI Agent</div>
          {content}
        </div>
        """, unsafe_allow_html=True)
        if tool_results:
            for tr in tool_results:
                render_tool_result(tr)


# ─────────────────────────────────────────────
# Sidebar — Live Network Status
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:8px 0 16px;'>
          <div style='font-size:22px;font-weight:800;color:#F9FAFB;'>🔵 Arc Network</div>
          <div style='font-size:11px;color:#6B7280;margin-top:2px;'>Testnet · Live Status</div>
        </div>
        """, unsafe_allow_html=True)

        # Refresh button
        if st.button("⟳  Refresh", use_container_width=True):
            st.session_state.pop("network_status", None)
            st.session_state.pop("status_ts", None)

        # Cache status for 15 seconds
        now = time.time()
        if "network_status" not in st.session_state or (now - st.session_state.get("status_ts", 0)) > 15:
            with st.spinner("Fetching…"):
                st.session_state.network_status = fetch_network_status()
                st.session_state.status_ts = now

        ns = st.session_state.network_status
        st.markdown("<div class='section-header'>Network</div>", unsafe_allow_html=True)

        badge = "status-online" if ns["online"] else "status-offline"
        label = "● ONLINE" if ns["online"] else "● OFFLINE"
        st.markdown(f"<span class='{badge}'>{label}</span>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='metric-card' style='margin-top:10px;'>
          <div class='metric-label'>Latest Block</div>
          <div class='metric-value'>{ns["block"]:,}</div>
          <div class='metric-sub'>Sub-second deterministic finality</div>
        </div>
        <div class='metric-card'>
          <div class='metric-label'>Gas Price</div>
          <div class='metric-value'>{f"{ns['gas_gwei']:.2f} Gwei" if ns['gas_gwei'] else "—"}</div>
          <div class='metric-sub'>~${f"{ns['gas_usd_transfer']:.6f}" if ns['gas_usd_transfer'] else "—"} per transfer</div>
        </div>
        <div class='metric-card'>
          <div class='metric-label'>Chain ID</div>
          <div class='metric-value'>{ns["chain_id"] or CHAIN_ID}</div>
          <div class='metric-sub'>Arc Testnet</div>
        </div>
        <div class='metric-card'>
          <div class='metric-label'>RPC Endpoint</div>
          <div class='metric-value' style='font-size:11px;word-break:break-all;'>{ns["rpc"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-header'>Stablecoins</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='metric-card'>
          <div style='font-size:12px;font-weight:700;color:#10B981;margin-bottom:4px;'>USDC (Native Gas)</div>
          <div style='font-size:10px;font-family:monospace;color:#9CA3AF;word-break:break-all;'>{USDC_CONTRACT}</div>
          <div style='margin-top:4px;'><span class='tag'>6 dec ERC-20</span><span class='tag'>18 dec native</span></div>
        </div>
        <div class='metric-card'>
          <div style='font-size:12px;font-weight:700;color:#3B82F6;margin-bottom:4px;'>EURC</div>
          <div style='font-size:10px;font-family:monospace;color:#9CA3AF;word-break:break-all;'>{EURC_CONTRACT}</div>
          <div style='margin-top:4px;'><span class='tag'>6 dec</span><span class='tag'>Circle</span></div>
        </div>
        <div class='metric-card'>
          <div style='font-size:12px;font-weight:700;color:#F59E0B;margin-bottom:4px;'>USYC</div>
          <div style='font-size:10px;font-family:monospace;color:#9CA3AF;word-break:break-all;'>{USYC_CONTRACT}</div>
          <div style='margin-top:4px;'><span class='tag'>6 dec</span><span class='tag'>Yield-bearing</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-header'>Resources</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-size:12px;line-height:2;'>
          <a href='{EXPLORER}' target='_blank' style='color:#60A5FA;'>🔍 ArcScan Explorer ↗</a><br>
          <a href='{GAS_TRACKER}' target='_blank' style='color:#60A5FA;'>⛽ Gas Tracker ↗</a><br>
          <a href='{FAUCET}' target='_blank' style='color:#60A5FA;'>🚰 Circle Faucet ↗</a><br>
          <a href='https://docs.arc.io' target='_blank' style='color:#60A5FA;'>📚 Arc Docs ↗</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='margin-top:20px;font-size:10px;color:#4B5563;text-align:center;'>
          Last updated: {datetime.fromtimestamp(st.session_state.get("status_ts",time.time())).strftime("%H:%M:%S")}<br>
          Ignyte Challenge · Agentic Economy
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main layout
# ─────────────────────────────────────────────
render_sidebar()

# Banner
st.markdown("""
<div class='arc-banner'>
  <h1>🔵 Arc Agentic Stablecoin Companion</h1>
  <p>Autonomous AI agent for stablecoin commerce on Arc Testnet · Ignyte Challenge — Agentic Economy Track</p>
  <div style='margin-top:10px;'>
    <span class='tag'>💸 USDC Payments</span>
    <span class='tag'>🤖 Autonomous Agents</span>
    <span class='tag'>⚡ Sub-second Finality</span>
    <span class='tag'>🔒 Read-only Safe</span>
    <span class='tag'>📡 Live Arc MCP</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_results_map" not in st.session_state:
    st.session_state.tool_results_map = {}  # index → list[dict]
if "pending_confirmation" not in st.session_state:
    st.session_state.pending_confirmation = None

# Quick-action suggestions
st.markdown("<div class='section-header'>Quick Actions</div>", unsafe_allow_html=True)
cols = st.columns(4)
suggestions = [
    ("⛽ Check Gas", "Is the current gas price good for sending USDC? Run an autonomous check."),
    ("💼 Check Wallet", "Check balances for wallet 0x742d35Cc6634C0532925a3b8D4C9C5e2a8c7b0a4"),
    ("🚀 Agentic Payment", "Show me how an autonomous AI agent would prepare a $10 USDC payment on Arc, including gas estimation and confirmation flow."),
    ("🧱 Recent Blocks", "Fetch the last 5 blocks and tell me about network activity."),
]
for i, (label, prompt) in enumerate(suggestions):
    with cols[i]:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Agent thinking…"):
                response_text, tool_results = run_agent(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.session_state.tool_results_map[len(st.session_state.messages) - 1] = tool_results
            st.rerun()

st.markdown("---")

# Chat history
st.markdown("<div class='section-header'>AI Agent Chat</div>", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class='alert-info' style='text-align:center;padding:24px;'>
      <div style='font-size:28px;margin-bottom:8px;'>🤖</div>
      <div style='font-size:15px;font-weight:600;color:#F9FAFB;margin-bottom:6px;'>Arc AI Agent Ready</div>
      <div style='color:#9CA3AF;font-size:13px;'>Ask me to check wallet balances, analyze gas, prepare USDC transfers,<br>or generate code for agentic stablecoin commerce on Arc Testnet.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, msg in enumerate(st.session_state.messages):
        tool_results = st.session_state.tool_results_map.get(idx, []) if msg["role"] == "assistant" else []
        render_chat_message(msg["role"], msg["content"], tool_results)

# Chat input
st.markdown("---")
with st.container():
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message the Arc AI Agent",
            placeholder="e.g. Check balance for 0x... | Is gas good now? | How do autonomous agents pay each other on Arc?",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_btn:
        send_clicked = st.button("Send ▶", use_container_width=True)

if send_clicked and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.spinner("Agent reasoning…"):
        response_text, tool_results = run_agent(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.session_state.tool_results_map[len(st.session_state.messages) - 1] = tool_results
    st.rerun()

# Clear chat
if st.session_state.messages:
    if st.button("🗑  Clear chat", use_container_width=False):
        st.session_state.messages = []
        st.session_state.tool_results_map = {}
        st.rerun()

# Footer
st.markdown("""
<div style='text-align:center;margin-top:32px;padding:16px;border-top:1px solid #1F2937;'>
  <div style='color:#4B5563;font-size:12px;'>
    Arc Agentic Stablecoin Companion · Built for the Ignyte Stablecoins Commerce Stack Challenge<br>
    Agentic Economy Track · Powered by Arc Testnet + Anthropic Claude · Read-only &amp; Safe
  </div>
</div>
""", unsafe_allow_html=True)
