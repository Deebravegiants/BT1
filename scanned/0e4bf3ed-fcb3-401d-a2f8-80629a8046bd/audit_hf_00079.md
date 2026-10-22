# [M] M-19 | Init Close Of A Liquidatable Pos Permitted

## Summary
Severity: Medium
Contest weight: 0.1072
Dataset id: 155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a recent price is given to any init or validate function the _applyPnlAndFundingAndLiquidate flow is executed and if too many ticks are liquidatable, some are left over and the flow breaks early as liquidations are pending.
In this case, a user can initiate a close of a position that sits on such a liquidatable tick that was not liquidated yet by providing a price that is less recent than the current lastPrice and therefore skipping the _applyPnlAndFundingAndLiquidate flow.
As the init close pos function only checks if the version of the positions tick changed but not if the lastPrice is above its liquidation price the call will pass.

## Recommendation
Consider not allowing any actions to be initiated or validated in the event that any liquidations are pending at the lastPrice, even if the currentPrice timestamp is not recent.
