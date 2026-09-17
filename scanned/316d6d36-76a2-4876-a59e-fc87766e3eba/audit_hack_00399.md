# [M] Lixir Finance incident: Lixir Finance's vault tokens (lv_* wrappers over Uniswap V3 LP positions) were exploited due to a broken EIP-2612 permit signature

## Summary
Severity: Medium
Target: Lixir Finance
Loss: $ 12,300
Attack method: Smart Contract Vulnerability
Published: 2026-06-25
Source: https://x.com/DefimonAlerts/status/2070362661691207935
Type: slowmist-incident

## Details
Lixir Finance's vault tokens (lv_* wrappers over Uniswap V3 LP positions) were exploited due to a broken EIP-2612 permit signature verification. The attacker reused a single dummy signature to bypass checks, granting approval to their contract over dozens of holders' tokens, then drained underlying assets (WETH, USDC, USDT, LIX) via withdrawFrom/withdrawETHFrom, resulting in ~$12,300 loss.
