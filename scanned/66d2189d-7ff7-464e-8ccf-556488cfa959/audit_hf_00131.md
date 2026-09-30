# [M] Manager can grief with fees

## Summary
Severity: Medium
Contest weight: 0.0707
Dataset id: 392
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fees in `NFTXVaultUpgradeable` can be set arbitrarily high (no restriction in `setFees`).

The manager can front-run mints and set a huge fee (for example `fee = base`) which transfers user’s NFTs to the vault but doesn’t mint any pool share tokens in return for the user.

Similar griefing attacks are also possible with other functions besides `mint`.

Recommend checking for a max fee as a percentage of `base` (like 10%) whenever setting fees.

## Recommendation
No recommendation
