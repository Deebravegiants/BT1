# [M] Cozy Finance incident: DeFi protection protocol Cozy Finance on Optimism was exploited for about $160,000. The attacker first bought PTokens in the Aave

## Summary
Severity: Medium
Target: Cozy Finance
Loss: $ 160,000
Attack method: Smart Contract Vulnerability
Published: 2026-09-07
Source: https://x.com/SlowMist_Team/status/2096881310237426062
Type: slowmist-incident

## Details
DeFi protection protocol Cozy Finance on Optimism was exploited for about $160,000. The attacker first bought PTokens in the Aave v2 and Curve protection markets, then submitted undisputed YES answers to the UMA Optimistic Oracle. The trigger did not independently verify a real Aave/Curve hack, and PToken payout eligibility was not tied to a pre-proposal holder snapshot. After the markets moved to TRIGGERED, the attacker burned PTokens and claimed USDC.
