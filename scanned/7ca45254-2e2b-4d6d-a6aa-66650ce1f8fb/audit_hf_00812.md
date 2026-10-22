# [H] H-05 | DoS On Setting The LTV Of a Token To Zero

## Summary
Severity: High
Contest weight: 0.2295
Dataset id: 2548
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• The owner of a BasePool can set the LTV of a token to zero.
• The isPositionHealthy function will revert if a position holds a token in the asset list and this token has an LTV of zero.
Therefore if the owner updates the LTV of a token to zero and any position holds this token any interaction with it through the PositionManager will revert.
This has multiple bad consequences:
• Borrowers debt increases but they are not able to repay
• Borrowers can not be liquidated
• Borrowers are not able to get their collateral back
• The owner of a base pool can create unliquidatable positions
Unliquidatable positions:
• Owner sets the LTV of a token above 0
• The owner creates a position adds this token as collateral, borrows funds, and does something risky with them
• The owner sets the LTV for this token to 0
• Now the position is not liquidatable till the owner sets the LTV back to a value above 0

## Recommendation
Do not allow to set the LTV of a token to zero.
