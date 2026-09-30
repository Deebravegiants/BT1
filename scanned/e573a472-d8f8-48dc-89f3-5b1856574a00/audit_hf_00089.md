# [M] M-08 | removeBlockedPendingAction Extractable Value

## Summary
Severity: Medium
Contest weight: 0.1549
Dataset id: 165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _removeBlockedPendingAction function when a ValidateClosePosition pending action is removed the entire closeBoundedPositionValue amount is added to the vault.
This means the trader loses their entire position value in the event that their close position action is stuck, even if they were nowhere near close to liquidation. This could cause significant loss for a trader which has a large position.
Furthermore, this creates a potentially large arbitrage opportunity. If a removal of a ValidateClosePosition pending action for a large position close is sitting in the mempool it would be potentially significantly profitable for an actor to front-run this transaction and initiate a deposit into the vault right before the removal takes place.
Because vault deposits only vary based on price action between initiation and validation the malicious actor would realize their corresponding value of the immediate vault balance increase from the removal of the pending close position action.

## Recommendation
Instead of giving the entire position value to the vault upon removal of a close pending action, consider sending the position value to the specified to address. The protocol can then manually decide how much should be refunded to the trader versus donated to the vault via a new donate function.
