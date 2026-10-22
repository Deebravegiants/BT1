# [M] PPU-4 | borrowingFeeAmountForFeeReceiver Double Counted

## Summary
Severity: Medium
Contest weight: 0.0676
Dataset id: 18190
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fees.totalNetCostAmount includes both the fees.feeReceiverAmount and the fees.borrowingFeeAmount. The borrowingFeeAmount is comprised of both the borrowing fees for the pool and for the feeReceiver. The fees.feeReceiverAmount also includes the borrowing fees for the feeReceiver, therefore the borrowingFeeAmountForFeeReceiver amount is accounted for twice in the fees.totalNetCostAmount.

## Recommendation
Only account for the borrowingFeeAmountForFeeReceiver once in the fees.totalNetCostAmount.
