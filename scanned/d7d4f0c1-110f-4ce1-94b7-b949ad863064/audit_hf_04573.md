# [M] M-05 | Flash Loan Repayments Fail During addLeverage

## Summary
Severity: Medium
Contest weight: 0.1282
Dataset id: 22176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When adding leverage, the user provides pod tokens, and the corresponding pairedLpTokens are flash loaned. At the end of the transaction, this flash loan is repaid by borrowing pairedLpTokens from Fraxlend. However, the flash loan fee is not accounted for when borrowing from Fraxlend. The borrow amount from Fraxlend equals the flash loan amount unless users provide a greater overrideBorrowAmt. The Natspec comments regarding this variable is: "Override amount to borrow from the lending pair, only matters if max LTV is >50% on the lending pair". Since providing overrideBorrowAmt is not mandatory and there are no restrictions, the borrow amount from Fraxlend will usually be equal to _props.pairedLpDesired in most cases. However, this amount is equal to _d.amount, which is smaller than _flashPaybackAmt, causing the transaction to revert.

## Recommendation
The minimum borrow amount from Fraxlend to repay the flash loan should be _props.pairedLpDesired + _d.fee.
