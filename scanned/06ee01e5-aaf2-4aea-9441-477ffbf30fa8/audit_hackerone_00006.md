# [H] Wallet RPC Restricted-Mode Policy Bypass

## Summary
Severity: High (CVSS 7.6)
Program: Monero
Weakness: Improper Authentication - Generic
Reporter: usagirabbit
State: resolved
Disclosed: 2026-08-17T09:16:13.887Z
Source: https://hackerone.com/reports/3620006

## Details
## Summary

`monero-wallet-rpc` documents `--restricted-rpc` as view-only, but multiple non-view-only handlers do not enforce `m_restricted`.

As a result, a restricted wallet-RPC client can perform state-changing or policy-sensitive operations that should be denied.

Validated locally:

1. `create_wallet` succeeds in restricted mode.
2. `close_wallet` succeeds in restricted mode.
3. `open_wallet` succeeds in restricted mode.
4. `create_address` succeeds in restricted mode.
5. `export_key_images` reaches a success path instead of returning restricted-mode denial.
6. `get_tx_key` and `get_reserve_proof` reach proof/key-handling logic instead of being denied.

For contrast, once a wallet is loaded, a correctly gated method such as `transfer` returns `Command unavailable in restricted mode.`

## Severity

Suggested CVSS v3.1: `7.6` with `AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L`.

Rationale:

1. The issue is network reachable over wallet RPC.
2. Restricted mode is explicitly meant to reduce a client to view-only access.
3. A restricted client can create wallets, close wallets, open wallets, and mutate wallet state.
4. The current PoC demonstrates unauthorized access to proof/key-related handlers, but it does not claim extraction of secret material from those endpoints.
5. I validated the bypass with normal digest-auth restricted credentials, so this score does not depend on disabled authentication.
6. `close_wallet` causes a real low-grade availability impact by breaking subsequent operations on the active wallet instance until an operator reloads or recreates the wallet state.

Deployment note:

1. Wallet RPC binds to loopback by default, and authentication remains enabled unless the operator disables it.
2. The `AV:N/PR:L` framing assumes an operator intentionally exposes wallet RPC to a remote restricted client, not the out-of-the-box local-only posture.

## AI Usage Disclosure

AI assistance was used for code review, draft organization, and local validation planning.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3620006_
