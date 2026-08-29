# [C] Critical Deadlock Vulnerability in Monero RPC Leading to Complete Node Paralysis

## Summary
Severity: Critical (CVSS 10.0)
Program: Monero
Weakness: Uncontrolled Resource Consumption
Reporter: rorkh
State: resolved
Disclosed: 2026-05-06T17:13:37.828Z
Source: https://hackerone.com/reports/3307874

## Details
## Summary:
A deadlock vulnerability in Monero's JSON-RPC interface allows a remote, unauthenticated attacker to completely paralyze any Monero node with a single HTTP request containing specific batch methods, leading to permanent denial of service.

## Releases Affected:
- Monero 'Fluorine Fermi' (v0.18.4.2-2987b7200)
- Likely all previous versions
- All operating systems (Linux, Windows, macOS)
- All run modes (mainnet, testnet, offline, restricted-rpc)

Severity:
CVSS 3.0: 10.0 – Critical:
- CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
Rationale:
- Remote, network-based attack
- No privileges required
- Immediate node paralysis

Affects availability, integrity, and potentially confidentiality

## Steps To Reproduce:
1. Start Monero node with any configuration:
   ./monerod \                              ─╯
  --testnet \
  --data-dir ~/monero-testnet/blockchain \
  --rpc-bind-port 28081 \
  --p2p-bind-port 28080 \
  --restricted-rpc \
  --confirm-external-bind \
  --add-exclusive-node 127.0.0.1:28080 \
  --log-level 4 \

2. Run the script
python3 exploit/PoC.py http://localhost:28081/json_rpc 50 500

3. Observe:
- Node becomes completely unresponsive (RPC, P2P, admin)
- Standard termination signals (SIGTERM/SIGINT) do not work
- Only kill -9 can terminate the process

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3307874_
