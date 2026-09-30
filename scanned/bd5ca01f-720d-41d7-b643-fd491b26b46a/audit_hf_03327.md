# [C] MKTU-4 | 60 Decimals Of Precision Causes Overflow

## Summary
Severity: Critical
Contest weight: 0.1882
Dataset id: 18178
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getPoolValue function, the cache.totalBorrowingFees utilizes 60 decimals of precision, therefore Precision.applyFactor(cache.totalBorrowingFees, cache.borrowingFeeReceiverFactor) will have 60 decimals of precision. Whenever an LP wants to withdraw after borrowing fees have been accumulated, the call to marketTokenAmountToUsd in WithdrawalUtils.sol would overflow since the pool value is multiplied by the market token amount which has 18 decimals of precision. Furthermore, the amount of market tokens depositors receive will be drastically reduced as the pool value is inflated.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_4.ts

## Recommendation
Do not use 60 decimals of precision for the cache.totalBorrowingFees or account for this additional precision when applying the factor.
