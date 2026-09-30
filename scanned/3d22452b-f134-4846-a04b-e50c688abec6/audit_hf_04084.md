# [M] GLOBAL-4 | Sequencer May Experience Outages

## Summary
Severity: Medium
Contest weight: 0.0998
Dataset id: 20537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While the Arbitrum sequencer is down it is possible for a users position to go from healthy to
undercollateralized. During this time the average user will not be able to rescue their position as they
will not be able to submit orders directly through Arbitrum.
However, most liquidators will be automated and would be sophisticated enough to submit
liquidation transactions through the delayed inbox on L1. When the sequencer is back online the
transactions submitted through the delayed box will be executed ﬁrst, meaning the position will be
liquidated before the users have a chance to rescue their position.

## Recommendation
Consider adding a grace period after outages to allow users some time to save their position when
the sequencer is back online.
