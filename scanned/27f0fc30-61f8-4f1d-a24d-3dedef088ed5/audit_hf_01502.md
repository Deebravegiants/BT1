# [M] M-10 An unsafe transfer

## Summary
Severity: Medium
Contest weight: 0.0495
Dataset id: 7986
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some of the tokens do not revert on failed transferFrom. Also, there are some tokens with a fee on transfer, so the real transferred balance should be checked via balanceOf(), otherwise it could lead to funds insolvency.
FantiumClaimingV1.sol#L277-L281

## Recommendation
We recommend using the safeTransfer library and also adding a check that an exact amount of tokens was transferred to the contract.
