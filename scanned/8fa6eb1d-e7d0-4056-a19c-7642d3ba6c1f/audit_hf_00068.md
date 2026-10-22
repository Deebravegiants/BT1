# [C] ORDA-1 | Wrong amount deposited into the DegenBox

## Summary
Severity: Critical
Contest weight: 0.1717
Dataset id: 144
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the sendValueInCollateral function the amount provided as a parameter is a collateralShare amount (GM shares in the degen box), that amount is then converted to a shortToken amount via an exchange rate. The amountShortToken is then sent to the degenBox, however the amount (GM shares) is what is deposited. Therefore a GM token Shares amount will be treated as a short token amount, which may have severely different valuations depending on the exchange rate. Additionally this can often cause the liquidation to revert if the GM token is a lower value than the short token.

## Recommendation
In the sendValueInCollateral function, line 197: degenBox.deposit(IERC20(shortToken), address(degenBox), recipient, amount, 0); Should be replaced with: degenBox.deposit(IERC20(shortToken), address(degenBox), recipient, amountShortToken, 0);
