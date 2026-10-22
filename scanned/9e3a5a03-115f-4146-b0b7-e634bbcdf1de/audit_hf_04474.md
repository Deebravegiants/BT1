# [H] H-13 | cancelDeposit Misses swapProgressData

## Summary
Severity: High
Contest weight: 0.2441
Dataset id: 21972
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the cancelDeposit function there is no accounting for the swapProgressData, this causes several issues when a deposit is cancelled after a composite swap through Paraswap and GMX where the GMX swap failed. Firstly the transfer of collateral tokens is likely to fail as part of the deposited collateral tokens will have been swapped to the index token and are recorded in the swapProgressData.swapped value. safeTransfer is not used for this transfer and therefore depending on the collateralToken used, users could lose their funds as a result. Secondly the swapProgressData.swapped value is not cleared when the deposit occurs, therefore the next deposit will be credited with receiving these swapped tokens. Therefore if the vault did have enough collateral tokens to pay out the user, this swapped value would then be double counted and awarded to the next depositor at the expense of previous vault shareholders.

## Recommendation
Account for the swapProgressData.swapped value in the cancelDeposit function such that if the swapProgressData.swapped value is nonzero that amount of index tokens is transferred to the user and deducted from the amount of collateral tokens transferred. Then clear the swapProgressData at the end of the function. Additionally, use safeTransfer in the cancelDeposit function.
