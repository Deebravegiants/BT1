# [M] Kipseli incident: The Kipseli Router contract on Base was exploited via Improper Validation / Decimal Mismatch. The router blindly used the amount r

## Summary
Severity: Medium
Target: Kipseli
Loss: $ 72,350
Attack method: Smart Contract Vulnerability
Published: 2026-04-22
Source: https://x.com/TheDEFIac/status/2046973478595641435
Type: slowmist-incident

## Details
The Kipseli Router contract on Base was exploited via Improper Validation / Decimal Mismatch. The router blindly used the amount returned by an external USDC-only quoter as the raw transfer amount for tokenOut without verifying that the output token matched the quote token. The attacker used an unsupported path (e.g., WETH → cbBTC), causing the quoter to return a USDC-scaled value (6 decimals) which was then transferred as cbBTC (8 decimals), resulting in massive over-transfer. The attacker swapped only ~0.04 WETH for ~0.926 cbBTC (worth ~$72.35K). Afterward, the finder contacted the team, returned 80% of the funds as a white-hat disclosure, and kept 20% as a bug bounty.
