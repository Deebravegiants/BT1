# [C] DPCU-1 | Unliquidatable Position Due To getLiquidationValues

## Summary
Severity: Critical
Contest weight: 0.1825
Dataset id: 18492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getLiquidationValues function the values.pnlAmountForPool is reset to a new value, although
the previous value may have been used in a swap from the pnlToken to the collateralToken.
This causes mis-accounting in the market and causes a revert with the market token balance check
upon liquidation. Therefore positions can be unliquidatable, yielding a potentially catastrophic
amount of bad-debt for the market.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/8bcb69c207c13c49ac2aa540638640b6a5b84412/test/guardian/PoCs.ts#L273

## Recommendation
The solution is to account for the previous values.pnlAmountForPool in the event that this swap was
made. e.g. add:
if (wasSwapped) {
MarketUtils.applyDeltaToPoolAmount(
params.contracts.dataStore,
params.contracts.eventEmitter,
params.market.marketToken,
values.pnlTokenForPool,
values.pnlAmountForPool
);
}
to the else branch in getLiquidationValues.
