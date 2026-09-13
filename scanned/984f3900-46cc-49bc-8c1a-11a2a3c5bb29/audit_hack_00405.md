# [M] Namada Shielded Pools incident: On June 19, 2026, approximately $600,000 in assets (ATOM, USDC, OSMO, TIA, NYM, etc.) were drained from Namada’s Multi-Asset Shiel

## Summary
Severity: Medium
Target: Namada Shielded Pools
Loss: $ 600,000
Attack method: Protocol Vulnerability
Published: 2026-06-19
Source: https://x.com/f12sec/status/2068065239187218505?s=46&amp;t=DLwbX9Nw4QECiyZQ0av-fg
Type: slowmist-incident

## Details
On June 19, 2026, approximately $600,000 in assets (ATOM, USDC, OSMO, TIA, NYM, etc.) were drained from Namada’s Multi-Asset Shielded Pool (MASP) through an IBC Transfer Logic Exploit. The loss initially went unnoticed because a stale indexer continued displaying funds as available, while live RPC queries showed zero balances on the chain. The attacker swept shielded IBC assets cross-chain. Namada confirmed the exploit and is investigating.
