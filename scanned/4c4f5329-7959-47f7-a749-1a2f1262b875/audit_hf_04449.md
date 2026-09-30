# [C] C-04 | Users Avoid Losses From GMX

## Summary
Severity: Critical
Contest weight: 0.1755
Dataset id: 21940
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the perpetual vault when withdrawing value from the vault there is no accounting for the negative
PnL that a GMX perpetual position may have.
Instead the user’s decrease order contains the collateralDeltaAmount and sizeDeltaInUsd amounts
that are proportional to the shares the user holds.
The sizeDeltaInUsd value will indeed realize the proportion of the negative PnL that the user owns,
however this negative PnL amount will be deducted from the position’s collateral that remains, and
not from the collateralDeltaAmount which will be rewarded to the withdrawer.
As a result withdrawers avoid losses and disburse them onto other vault holders.

## Recommendation
Account for the PnL of a position that will be realized when computing the collateralDeltaAmount for
a withdrawal.
