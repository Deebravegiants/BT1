# [M] voucherIndexes is not updated when

## Summary
Severity: Medium
Contest weight: 0.0651
Dataset id: 19806
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When staker or borrower cancel the voucher, the voucherIndexes for the lastVoucher is not updated. Vulnerability Details The voucherIndexes is not updated when a voucher is cancelled. It leads to incorrect index for the last voucher, which points to another voucher with different staker. It could be a point to be exploit by malicious members.

## Recommendation
Add update voucherIndexes in the _cancelVouchInternal function, below line 604 of UToken.sol: voucherIndexes[borrower][lastVoucher.staker] = removeVoucherIndex.Idx
