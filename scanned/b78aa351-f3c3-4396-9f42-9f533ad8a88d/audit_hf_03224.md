# [M] Unsafe ERC20 methods

## Summary
Severity: Medium
Contest weight: 0.0992
Dataset id: 17841
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Using unsafe ERC20 methods can revert the transaction for certain tokens. There are many Weird ERC20 Tokens that won't work correctly using the standard IERC20 interface. For example, IERC20(token).transferFrom() and IERC20(token).transfer() will fail for some tokens as they may not conform to the standard IERC20 interface. And if _aggregator does not always consume all the allowance given at L72, the transaction will also revert on the next call, because there are certain tokens that do not allow approval of a non-zero number when the current allowance is not zero (eg, USDT). The contract will malfunction for certain tokens.

## Recommendation
Consider using SafeERC20 for transferFrom, transfer and approve.
