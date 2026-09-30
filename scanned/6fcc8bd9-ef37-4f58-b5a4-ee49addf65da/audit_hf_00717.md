# [H] H-03 | Accounts Can Be Liquidated Upon Order Settlement

## Summary
Severity: High
Contest weight: 0.1965
Dataset id: 2268
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An account can be put into a liquidatable state immediately upon settling an order. This would cause the immediate loss to a user of all funds that they could have instead withdrawn through modifyColatteral. This is made possible by the lack of a check for isLiquidatable at the end of the settleOrder function. Even if the advice is followed in ﬁnding H-XX to ensure there is enough margin to cover the settlement fees, the account can still be liquidated upon settlement if the market were to move unfavorably.

## Proof of Concept
https://github.com/GuardianAudits/snx-bfp-1/blob/devtooligan-pocs/markets/bfp-market/test/integration/modules/guardian/poc/realizePnlTest.test.ts#L18-L127

## Recommendation
Consider adding logic to the validateTrade function which will revert in case the new position including fees causes account to become liquidatable.
