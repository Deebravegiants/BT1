# [M] Four.Meme incident: The memecoin platform Four.Meme was attacked. According to an analysis by the SlowMist security team, the attacker was able to exe

## Summary
Severity: Medium
Target: Four.Meme
Loss: $ 183,000
Attack method: Business Logic Flaw
Published: 2025-02-11
Source: https://x.com/SlowMist_Team/status/1889206331644789244
Type: slowmist-incident

## Details
The memecoin platform Four.Meme was attacked. According to an analysis by the SlowMist security team, the attacker was able to execute a frontrunning attack by pre-creating a liquidity pool on PancakeSwap v3 with an extremely high token price. When the token was integrated into PancakeSwap v3, liquidity was added based on the unbalanced pool set up by the attacker. Since the project team did not verify the pool's price, the added liquidity followed the maliciously set price. As a result, the attacker was able to exploit this mechanism to drain assets from the pool.
