# [H] H-03 | previewAddLiquidity Incorrect quoteBalance

## Summary
Severity: High
Contest weight: 0.1133
Dataset id: 20850
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the previewAddLiquidity function the quoteBalance is intended to account for the current balance of the quote tokens in the LP as well as the new quote tokens which will be added to the LP. However the quoteBalance is the balance of quote tokens + the baseInAmount: uint256 quoteBalance = IMagicLP(lp)._QUOTE_TOKEN_().balanceOf(address(lp)) + baseInAmount;

## Recommendation
Correct the quoteBalance to be: uint256 quoteBalance = IMagicLP(lp)._QUOTE_TOKEN_().balanceOf(address(lp)) + quoteInAmount;
