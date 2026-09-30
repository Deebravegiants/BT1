# [M] ADAP-1 | Incorrect Liquidatable Reading

## Summary
Severity: Medium
Contest weight: 0.0577
Dataset id: 20566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function getLiquidationNetPNLInCollateral calculates whether the position is liquidatable using canLiquidate = netProfitOrLoss > liquidationThreshold; However, it does not take into account whether it is indeed profit or loss. A user may be in a large profit and now be considered liquidatable from the Adapter’s perspective.

## Recommendation
Take into consideration whether the position is in profit prior to setting canLiquidate.
