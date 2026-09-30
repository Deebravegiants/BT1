# [M] M-06 | Decrease Position Prevented

## Summary
Severity: Medium
Contest weight: 0.0721
Dataset id: 21472
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The anchor and floor positions can be disjoint, and price may be between the two positions. When a user attempts to decreasePosition, the floor reserves will be removed before the swap.
If price is between the two positions, Uniswap will revert during the swap since there is no liquidity below the anchor as the floor was removed temporarily. Consequently, the user will be unable to decreasePosition and unwind their leverage.

## Recommendation
Sliding will correct this case, monitor such situations and slide as necessary.
