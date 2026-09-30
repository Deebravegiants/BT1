# [M] USM incident: The USM protocol suffered an exploit due to a pricing logic flaw in the ethFromDefund() function within defund(). It uses the arit

## Summary
Severity: Medium
Target: USM
Loss: $ 136,000
Attack method: Smart Contract Vulnerability
Published: 2026-08-10
Source: https://x.com/SlowMist_Team/status/2086644725143183639
Type: slowmist-incident

## Details
The USM protocol suffered an exploit due to a pricing logic flaw in the ethFromDefund() function within defund(). It uses the arithmetic mean of the current and estimated final FUM sell prices for a single redemption but lacks “split invariance.” Combined with the per-redemption state contraction (adjShrinkFactor) and integer rounding, an attacker used a flash loan to call fund() to manipulate internal pricing, then split the same FUM amount into 64 small defund() calls, extracting more ETH than a single large call and causing a loss of ~70.83 ETH.
