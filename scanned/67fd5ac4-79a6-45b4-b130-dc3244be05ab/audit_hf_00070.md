# [H] GMXC-2 | amountToAdd Not Valued At The Collaterization Rate

## Summary
Severity: High
Contest weight: 0.1638
Dataset id: 146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When validating whether a borrow position is solvent, the COLLATERIZATION_RATE is used to verify that the amount borrowed does not exceed the maximum percentage borrowable with the current collateral. However, the COLLATERIZATION_RATE is not applied to amountToAdd, which is the amount of GM tokens expected to be obtained from a pending deposit. For example, assume MIM and GM have a 1-1 price and the COLLATERIZATION_RATE is 75%. 10 GM tokens would allow borrowing 10 MIM rather than 7.5. As a result, the amount of MIM able to be borrowed is calculated to be larger than allowed, and the position is deemed solvent.

## Recommendation
Value the amountToAdd at the COLLATERIZATION_RATE.
