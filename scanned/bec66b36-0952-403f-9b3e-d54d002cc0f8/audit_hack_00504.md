# [M] Cyrus Finance incident: The DeFi yield protocol Cyrus Finance (CyrusTreasury contract) on BNB Chain was exploited. The attacker used a flash loan to manip

## Summary
Severity: Medium
Target: Cyrus Finance
Loss: $ 516,840
Attack method: Flash Loan Attack
Published: 2026-03-22
Source: https://certik.medium.com/cyrus-finance-incident-analysis-91f1754a058f
Type: slowmist-incident

## Details
The DeFi yield protocol Cyrus Finance (CyrusTreasury contract) on BNB Chain was exploited. The attacker used a flash loan to manipulate the PancakeSwap V3 ETH/USDT pool spot price, triggering a vulnerability in the withdrawUSDTFromAny function to over-extract liquidity from an LP position, profiting approximately $516,840 before laundering the funds via Tornado Cash in 9 batches.
