# [M] Zentra Finance incident: On September 9, 2026, an attacker used a single transaction on Citrea mainnet and ~200,000 USDC.e of flash liquidity as temporary

## Summary
Severity: Medium
Target: Zentra Finance
Loss: $ 140,030
Attack method: Smart Contract Vulnerability
Published: 2026-09-09
Source: https://x.com/ZentraFinance/status/2098415552293195831
Type: slowmist-incident

## Details
On September 9, 2026, an attacker used a single transaction on Citrea mainnet and ~200,000 USDC.e of flash liquidity as temporary collateral to drain 140,000 ctUSD and 30 USDC.e from Zentra’s lending pool. The root cause was an accounting edge case in repayWithATokens: the debt path could complete while the matching aToken burn was reduced to zero. The operations multisig paused all markets about 17 minutes later; no second exploit occurred.
