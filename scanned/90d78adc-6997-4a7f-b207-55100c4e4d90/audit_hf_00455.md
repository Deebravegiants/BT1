# [M] User can save part of the interest

## Summary
Severity: Medium
Contest weight: 0.0921
Dataset id: 1881
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user opens a position, it starts accruing interest which is paid to vault depositors based on their shares out of the total supply.
There is a possible attack vector where an exploiter can recoup a big portion of the interest repaid. If he uses flashloan of the principal asset to deposit it the vault, then close his position and repay it afterwards in one transaction, he will manipulate vault shares so he can claim almost the full interest. There are free flash loan providers such as Morpho, where users can borrow millions.
Almost interest-free positions.

## Recommendation
Create deposit/withdraw window on the vault, so user cannot use flash-loan and exploit that.
