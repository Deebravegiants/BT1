# [M] Four.Meme incident: BNB-based memecoin launchpad Four.Meme was attacked. According to the SlowMist security team’s analysis, the attacker purchased a

## Summary
Severity: Medium
Target: Four.Meme
Loss: $ 19,500
Attack method: Price Manipulation
Published: 2025-03-18
Source: https://x.com/SlowMist_Team/status/1901845958767657072
Type: slowmist-incident

## Details
BNB-based memecoin launchpad Four.Meme was attacked. According to the SlowMist security team’s analysis, the attacker purchased a small amount of tokens before launch through the 0x7f79f6df function of Four.Meme, and used this feature to send tokens to a specified PancakeSwap Pair address that had not yet been created. This allowed the attacker to create the Pair and add liquidity without needing to transfer the yet-to-be-launched tokens to the Pair, bypassing the transfer restrictions (MODE_TRANSFER_RESTRICTED) that applied before the Four.Meme Token launch. Ultimately, the attacker was able to add liquidity at an unintended price to steal pool liquidity.
