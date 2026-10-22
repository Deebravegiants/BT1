# [M] M-4 A ﬂashloan will be broken if the USDT fee is more than zero

## Summary
Severity: Medium
Contest weight: 0.0739
Dataset id: 9233
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Let's take a look at the ﬂashloan ﬂow. After doTransferOut a receiver gets amount - fee.
CCollateralCapErc20.sol#L217
Then a receiver's onFlashLoan function will be called with an incorrect amount.
CCollateralCapErc20.sol#L224
Then doTransferIn will transfer the repayment amount but the contract will receive the repayment amount - fee
CCollateralCapErc20.sol#L231 and the require check will cause a revert.
CCollateralCapErc20.sol#L235

## Recommendation
The ﬂashloan() function should be rewritten taking into consideration the USDT fee value.
