# [M] GMI-2 | Deposit Prevented By Double Counting GM Deposits

## Summary
Severity: Medium
Contest weight: 0.1284
Dataset id: 20514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the deposit function, the previewMint function is called with the shares that are to be minted to the caller for their deposited GM amounts.

The previewMint function contains the _validateMintableAmounts validation at the end of the function which accounts for the share value being deposited into the GMX V2 system and reverts if the additional deposit tokens would put the GM market over the deposit cap.

However, during a deposit, these GM tokens have already been minted and there are no additional long or short tokens that will be deposited into the GM market.

Therefore, this validation erroneously accounts for long/short tokens being deposited when they will not be, and as a result, causes unnecessary reverts when these phantom long/short token amounts exceed the deposit cap in GMX V2, ultimately causing DoS attacks on deposits.

## Recommendation
Do not perform the _validateMintableAmounts validation when depositing already minted GM tokens into GMI.
