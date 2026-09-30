# [M] M-15 | getLeverageFactor DoS

## Summary
Severity: Medium
Contest weight: 0.0823
Dataset id: 21503
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getLeverageFactor function the resulting leverageFactor is computed by dividing the totalCollateral by the _bAssetsCirculating - totalCollateral. However it is possible for the totalCollateral to be the entirety of the circulating supply in the event that every holder borrows against their bAssets. In this scenario the getLeverageFactor will revert with a divide by 0 panic. This results in a DoS for any call to the sweep or slide functions.

## Recommendation
Add a case to handle the scenario where all circulating assets are being used as collateral in the getLeverageFactor function. If (_bAssetsCirculating - totalCollateral == 0) return maxLeverageFactor
