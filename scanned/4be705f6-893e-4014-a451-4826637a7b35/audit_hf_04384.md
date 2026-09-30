# [M] M-12 | getRemainingBalance Should Round Up

## Summary
Severity: Medium
Contest weight: 0.0892
Dataset id: 21600
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Vestings are linearly unlocked after a cliff period during the release duration. Claimable balance of a vesting is calculated by subtracting the remaining balance from the total balance.
However, remaining balance of a vesting is calculated using the mulDiv formula from Math Library and this formula rounds down by default. Rounding down the remaining balance means rounding up the claimable balance.
Total claimable amounts will not be affected from this but intermediary claims will give users slightly more tokens than it should.

## Recommendation
Roundings should be in favour of the protocol. Use the mulDiv function with selective rounding option from the same library.
