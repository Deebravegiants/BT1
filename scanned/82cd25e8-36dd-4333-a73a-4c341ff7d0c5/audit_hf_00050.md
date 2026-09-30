# [M] ORDA-3 | Anyone May Withdraw From Order After Close

## Summary
Severity: Medium
Contest weight: 0.0674
Dataset id: 126
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a user were to ever close their Order but still have some funds remaining in the Order, anyone would be able to ACTION_CALL the withdrawFromOrder function from the Cauldron and take those funds. This can occur if a user were to call withdrawFromOrder without their entire amount and set closeOrder = True.

## Recommendation
Consider forcing a user to retrieve their entire shortToken and WETH balance prior to closing an order with the withdrawFromOrder function. Otherwise, clearly document that users should not leave their funds in an Order after closing it, as it becomes unblacklisted and accessible for all.
