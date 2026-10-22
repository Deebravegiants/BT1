# [M] DIEM-9 | Fees Apply To Insolvent Liquidations

## Summary
Severity: Medium
Contest weight: 0.0650
Dataset id: 105
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In cases where a portfolio is insolvently liquidated the fees are still distributed at their original value. This can lead to positions being unable to get liquidated in the event that the portfolioDollarMargin is less than the totalFee. Though this case may be rare, it is possible with high borrowing fees across many positions and should be handled.

## Recommendation
Cap the fees to what is payable in the event of an insolvent liquidation, otherwise consider ignoring them entirely for insolvent liquidations.
