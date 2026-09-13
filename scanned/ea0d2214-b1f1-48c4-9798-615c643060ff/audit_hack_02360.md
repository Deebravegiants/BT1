# [H] \[H01\] Incorrect social loss

## Summary
Severity: High
Source: https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Position.sol#L290
Type: audit-issue

## Details
When a bankrupt position is liquidated and the insurance fund is empty, the [opponent position holders should cover the loss](https://mcdex.io/references/#/en/perpetual?id=auto-liquidation). In this way, the profits on one side are garnished to fund the loss on the other side. This ensures the system as a whole cannot become insolvent. However, the loss is [actually attributed to positions on the same side](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Position.sol#L290). In the worst case, none of the positions on the same side will be able to cover the loss, which means the contract will be underfunded and some profits will not be redeemable. Consider updating the code to assign losses to the opposite side of the liquidation.

**Update:** _Fixed._
