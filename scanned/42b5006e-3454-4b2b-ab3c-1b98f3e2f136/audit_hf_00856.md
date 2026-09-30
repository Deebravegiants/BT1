# [M] M-16 | LegacyMarket Does Not Lock Collateral

## Summary
Severity: Medium
Contest weight: 0.2000
Dataset id: 2593
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LegacyMarket implementation of the minimumCredit function is hardcoded to return 0, therefore collateral is never locked on behalf of the LegacyMarket. However the creditCapacity of the LegacyMarket is crucial for the migration of V2 sUsd to V3 snxUsd. The convertUsd function uses the withdrawMarketUsd function which reduces the market’s creditCapacity by the withdrawn amount. If the Legacy Market’s creditCapacity is less than the value of debt which has been migrated, then the full debt cannot be migrated to the V3 system. In the most explicative case, a single staker migrates $1,000 of SNX and $200 of debt and undelegates their collateral as there is no minimumCredit requirement. The immediate debt has been correctly accounted for and the staker is only able to withdraw a net value of $800. However there remain 2 concerns: 1. The debtShares are now unbacked and further fluctuations in the debt value will not be covered by any collateral 2. The entire existing debt value cannot be migrated with the convertUsd function, as the creditCapacity has been reduced to $200. Both of these issues raise concerns over the backing value and therefore the price peg for synths in the V2 system. Additionally, the second issue directly prevents the migration from being fully carried out.

## Recommendation
Consider setting the minimumCredit to a nonzero value to ensure that sufficient collateral is present in the V3 pool to safely carry out the migration. Currently the creditCapacity of a market does not reduce as new totalDebt is added as mentioned in H-10. With this behavior it may make sense to assign the minimumCredit to the reportedDebt as this is the value of debt which must be convertible with the convertUsd function. However, this current behavior is possibly flawed, in which case another solution for the minimumCredit will have to be constructed, depending on the resolution of H-10.
