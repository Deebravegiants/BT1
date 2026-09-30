# [H] Partial Mints May Freeze Bridged BTC

## Summary
Severity: High
Contest weight: 0.1717
Dataset id: 15134
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A single call to mint() can contain multiple peg-in proofs. This is supported in case that a user bridges BTC multiple times in a single BTC block. In such cases the user must provide all their peg-in proofs from that block in one call to mint(), if they do not do so, peginBitcoinBlockHeight is incremented and they will forever lose access to the other peg-in proofs for that block.
The issue opens up a grieving attack where a malicious front runner can extract a single proof and submit it before the user. The user’s peginBitcoinBlockHeight will be incremented, invalidating their other proofs, and permanently freezing their bridged BTC.

## Recommendation
Implement a more granular replay-protection mechanism than peginBitcoinBlockHeight.
