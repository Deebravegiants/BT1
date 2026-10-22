# [M] Little Boy Plus incident: On June 17, 2026, Little Boy Plus — a fully decentralized DeFi mining protocol on BSC claiming “no team, no admin keys” — was expl

## Summary
Severity: Medium
Target: Little Boy Plus
Loss: $ 367,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-17
Source: https://x.com/SlowMist_Team/status/2067424733747122259
Type: slowmist-incident

## Details
On June 17, 2026, Little Boy Plus — a fully decentralized DeFi mining protocol on BSC claiming “no team, no admin keys” — was exploited. An attacker exploited a logic vulnerability in the LBPHashrate contract’s _update() function. By triggering it with a zero-value transferFrom call (bypassing OpenZeppelin authorization), the attacker unauthorizedly called _harvest and minted LBP tokens directly to the PancakeSwap LBP/USDT pair via mintReward. This inflated the pair’s balance without updating reserves, allowing the attacker to drain ~377,642 USDT (~$367k–$378k) through PancakePair.swap(). The funds were later sent to Tornado Cash.
