# [M] M-06 | Account Can Be Made Liquidatable By Cancelling

## Summary
Severity: Medium
Contest weight: 0.1266
Dataset id: 2263
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An account can be put into a liquidatable state when they are canceled. This would cause the immediate loss to a user of all funds that they could have instead withdrawn through modifyColatteral. This is made possible by the lack of a check for isLiquidatable at the end of the cancelOrder function. As mentioned in ﬁnding M-03, an order’s cancel-ability can be controlled by manipulating the skew. In addition to the fee for cancellation, the liquidation fees provide an added incentive to cancel the order which could even cover the costs of the skew manipulation.

## Proof of Concept
https://github.com/GuardianAudits/snx-bfp-1/blob/devtooligan-pocs/markets/bfp-market/test/integration/modules/guardian/poc/realizePnlTest.test.ts#L422-L546

## Recommendation
This may be greatly mitigated by the recommendation in H-02 of adding logic to validateTrade which reverts if the new position, including fees, would cause account to become liquidatable.
