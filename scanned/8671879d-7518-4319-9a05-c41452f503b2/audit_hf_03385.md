# [C] DPCU-2 | Mis-Accounting When Swap Fails

## Summary
Severity: Critical
Contest weight: 0.2781
Dataset id: 18493
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Positions in profit with unpaid borrowing/funding fees that are greater than the position’s collateral
open the exchange up to several high-impact issues when the swapProfitToCollateralToken swap
fails. These positions are able to exist since the isPositionLiquidatable check factors positive PnL as
collateral that would purportedly always be able to cover these fees.
However swapProfitToCollateralToken will commonly fail whenever the validatePoolAmount,
validateReserve, or validateMaxPnl checks fail as a result of the swap, causing the following issues:
Positions in large profit would be un-ADL-able since the ADL order would revert on line 224 as
the collateral is not sufficient to cover the fees alone.
Liquidations for these positions result in the user losing all of their profit since the execution
enters getLiquidationValues.
Liquidations for these positions result in the protocol having to cover a potentially large deficit
between the position’s collateral and the unpaid funding fees.
The pool value for market depositors sees a stepwise jump down from the potentially large
unpaid borrowing fees.
Decrease orders expecting to be able to use their profit to pay fees will be cancelled/frozen

## Recommendation
Do not allow positions to exist when their fees are greater than the actual collateral backing the
position. Allow positions to be liquidated when their fees negate the collateral backing amount.
