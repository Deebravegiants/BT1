# [M] Usual Protocol incident: According to monitoring by SlowMist, Usual Protocol suffered a sophisticated arbitrage attack. The attacker exploited a price disc

## Summary
Severity: Medium
Target: Usual Protocol
Loss: $ 42,800
Attack method: Contract Vulnerability
Published: 2025-05-27
Source: https://x.com/SlowMist_Team/status/1927627465717055574
Type: slowmist-incident

## Details
According to monitoring by SlowMist, Usual Protocol suffered a sophisticated arbitrage attack. The attacker exploited a price discrepancy between the protocol’s internal mechanisms and external markets. The core issue lay in the Vault system, which allowed a fixed 1:1 exchange between USD0++ and USD0—despite the two tokens trading at different prices on decentralized exchanges.

The attacker strategically created a custom liquidity pool and manipulated the transaction path to trick the Vault into releasing USD0 tokens without receiving the expected sUSDS collateral. These USD0 tokens were then sold on external markets at prices higher than the internal rate, allowing the attacker to profit through arbitrage.
