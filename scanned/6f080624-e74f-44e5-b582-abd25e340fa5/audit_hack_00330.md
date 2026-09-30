# [H] Notional Finance incident: Notional Finance’s legacy V1 Escrow contract was exploited. The attacker abused an unsafe uint128 cast in free-collateral valuatio

## Summary
Severity: High
Target: Notional Finance
Loss: $ 1,730,000
Attack method: Smart Contract Vulnerability
Published: 2026-09-04
Source: https://x.com/NotionalFinance/status/2095905726094856391
Type: slowmist-incident

## Details
Notional Finance’s legacy V1 Escrow contract was exploited. The attacker abused an unsafe uint128 cast in free-collateral valuation so that a fabricated liability of about 2^128 truncated to zero, bypassing solvency checks, minting fake fCash claims, and withdrawing about 69,257.37 DAI and 1,658,524.86 USDC (~$1.73M). The funds were swapped into roughly 689.2 ETH and deposited into Tornado Cash. The team paused the affected contract, said other user assets were not at risk, and is pursuing recovery.
