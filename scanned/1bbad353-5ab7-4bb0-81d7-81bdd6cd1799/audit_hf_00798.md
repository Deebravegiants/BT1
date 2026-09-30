# [H] H-01 | setFee Honeypot Attack

## Summary
Severity: High
Contest weight: 0.1352
Dataset id: 2534
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SuperPool owners can adjust the fee anytime instantly and no boundaries for the fee are set. This enables a honeypot attack:
• Attacker creates a SuperPool with a 1% fee
• Users deposit into the pool
• The attacker sets the fee way above 100%
• A few seconds pass and the pending interest for the attacker is >= all assets in the contract
• Attacker withdraws all funds of the SuperPool

## Recommendation
Implement min/max values and a timelock for critical parameter updates like fees.
