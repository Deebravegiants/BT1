# [H] encumberedCollateralBalances Not Updated

## Summary
Severity: High
Contest weight: 0.1359
Dataset id: 14665
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
auctionLockCollateral() and auctionUnlockCollateral() do not modify encumberedCollateralBalances array,
resulting in collateral locked or unlocked by the auction process not being tracked.
This may result in an invalid accounting, causing unexpected issues further down in the execution flow.

## Recommendation
Ensure the ledgers are correctly updated from within
auctionLockCollateral() and
auctionUnlockCollateral()
functions, for example:
// for locking
lockedCollateralLedger[borrower][collateralToken] += amount;
encumberedCollateralBalances[collateralToken] += amount;
Alternatively, call _lockCollateral() and _unlockCollateral functions from within auctionLockCollateral() and
auctionUnlockCollateral() respectively (the same way as it is currently implemented for externalLockCollateral()
and externalUnlockCollateral()).
