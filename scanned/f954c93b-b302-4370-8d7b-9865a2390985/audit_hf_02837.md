# [M] Fee-on-Transfer Tokens Can Cause Accounting Errors in Swappee Contract

## Summary
Severity: Medium
Contest weight: 0.1473
Dataset id: 15788
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Swappee contract contains a vulnerability in its handling of Fee-on-Transfer (FOT) tokens. The issue manifests in the swappee function, where the contract assumes the actual received amount of tokens will equal the transferred amount, without accounting for potential transfer fees. Specifically, when processing token transfers via IERC20(inputToken).transferFrom(), the contract uses the pre-transfer amount (amountsClaimedPerWallet[inputToken][msg.sender]) for all subsequent calculations and approvals, rather than checking the actual received balance. This assumption breaks for FOT tokens, where the received amount may be less than the transferred amount due to built-in transfer fees. When users attempt to swap FOT tokens, the contract will: incorrectly calculate fees based on the pre-fee amount, potentially approve more tokens than necessary to the aggregator, and may trigger reverts when attempting to swap the full pre-fee amount that isn’t actually available.

## Recommendation
The contract should implement proper FOT token handling by: measuring actual received balances before and after transfers, using the delta as the effective amount for swaps.
