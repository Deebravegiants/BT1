# [M] VF-2 | Rebalance Fees Errantly Account For Withdrawals

## Summary
Severity: Medium
Contest weight: 0.2000
Dataset id: 20512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the rebalance fees are computed with the _getVaultRebalanceFees function, the magnitude of the funds withdrawn during the epoch is added to the lockedBalanceSansUserDelta with the userPositionDelta variable. The resulting lockedBalanceSansUserDelta is ultimately the amount that is fee’d.

However this incorrectly fees the remaining assets in the vault, the issue becomes clear considering the following (unreasonable, yet demonstrative) example:
90% of the funds in the vault are withdrawn in a single epoch
10% of the funds remain, and the users holding that remaining amount are subject to a fee based upon the entire 100%.
Those who withdrew are not subject to this fee.

The remaining users are exposed to an exorbitant fee as a percentage of their holdings.

This specific example is hyperbolic and unlikely to ever arise but is used merely to demonstrate the inaccuracy of the fee logic and the smaller-scale inequality that will occur on every rebalance.

Additionally, the current fee calculations clearly misaccount these withdrawn amounts because they are treated as if they were in the system for the entire epoch. The performanceFeePercent, managementFeePercent, and timelockYieldPercent are all computed based on the percentYear of the past epoch and applied to these withdrawn amounts.

However, the withdrawn amounts by definition cannot have been present in the vault for this entire period, in the worst case they will have been withdrawn from the vault at the beginning of the epoch.

## Recommendation
Do not fee the remaining vault amounts based on the withdrawn amounts during the epoch.
