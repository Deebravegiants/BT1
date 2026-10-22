# [M] M-01 | Last User Cannot Fully Redeem If LT Position Is Still Open

## Summary
Severity: Medium
Contest weight: 0.1522
Dataset id: 2253
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LeveragedToken contract, when a user calls redeemFor to withdraw all the remaining margin, Synthetix will revert because removing that margin, IPerpsV2MarketConsolidated(marketAddress).transferMargin(-int256(amount)), would cause the position to be liquidatable. Synthetix enforces that a margin withdrawal can not put the account under the liquidation threshold. The last user would be unable to fully close out his position in a single transaction. He would have to do multiple smaller partial redemptions to avoid the liquidation check. First, the user would have to call redeemFor (possibly multiple times) until the LeveragedToken’s margin would fall below MINIMUM_MARGIN_BALANCE so a delayed close position order would be created. Then, wait for the execution of the delayed order that closes the position. And ﬁnally call redeemFor with the remaining amount of leveraged tokens. All these steps, trusting that no other user would front-run his ﬁnal redeemFor call reopening the LeveragedToken’s position.

## Recommendation
If the user is redeeming all the remaining tokens, forcibly do a submitCloseOffchainDelayedOrderWithTracking instead of a partial margin withdrawal that triggers liquidation checks.
