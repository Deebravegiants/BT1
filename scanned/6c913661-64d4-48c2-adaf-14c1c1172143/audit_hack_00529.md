# [M] Revert Lend incident: Revert Finance’s newly launched Aerodrome Lend vault on Base was exploited for $50,101. The attacker used a flash loan from Morpho

## Summary
Severity: Medium
Target: Revert Lend
Loss: $ 50,101
Attack method: Smart Contract Vulnerability
Published: 2026-01-29
Source: https://x.com/revertfinance/status/2017087480772600157
Type: slowmist-incident

## Details
Revert Finance’s newly launched Aerodrome Lend vault on Base was exploited for $50,101. The attacker used a flash loan from Morpho to mint an Aerodrome concentrated liquidity NFT, deposited it as collateral, borrowed USDC, and then exploited a missing safety check in the GaugeManager contract. This allowed unstaking and withdrawing all liquidity from the debt-backed position, leaving the vault with a worthless NFT shell. A second attacker replicated it shortly after. User funds were safe; losses were mostly from Revert’s own seeded USDC. The team disabled deposits and published a post-mortem.
