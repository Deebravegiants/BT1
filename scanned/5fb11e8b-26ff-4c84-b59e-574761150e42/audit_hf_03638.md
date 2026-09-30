# [H] hedgeDelta() calculates collateralDelta inac-

## Summary
Severity: High
Contest weight: 0.3094
Dataset id: 19707
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMXFuturesPoolHedger does not calculate the collateralDelta correctly when the
hedge position has a negative PNL. A price change in either direction that creates a
big enough collateralDelta could create a scenario where the system can not be
hedged anymore, and calls to hedgeDelta() will always fail.
The scenario can be reproduced by setting the price change in the if spot price
decreases, hedger needs to long less test case to 1200 instead of 1300 in
IntegrationTestsGMX.ts on line 553. The following output below contains the
position when the price is updated and hedgeDelta() is called, as well as relevant
output from GMX Vault when position execution calls decreasePosition() and
subsequently _reduceCollateral() where the call fails at Vault.sol#L1039.
--- current position ---
pos.size 14548
pos.collateral 13512
pos.averagePrice 1614
pos.entryFundingRate 0
pos.unrealisedPnl -3738
pos.isLong true
-- Call Vault.decreasePosition ---
sizeDelta 11847
collateralDelta 10811
--- Reducing position.collateral ---
old position.collateral 13512
adjustedDelta 3044
new position.collateral 10468
--- Adjusting pnl
old pnl -3044
new pnl 0
--- Trying to subtract _collateralDelta from position.collateral ---
position.collateral 10468
_collateralDelta 10811
!!!FAIL!!!
The system can not hedge its position anymore if the negative PNL is too big in
proportion to its size. This could lead to increased financial losses for Lyra LPs.

## Recommendation
collateralDelta needs to account for a negative PNL position and subtract the
adjusted delta in the same way that collateral is adjusted downwards in GMX
Vault._reduceCollateral().
