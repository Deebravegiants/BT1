# [H] H-02 | User Can Escape Cost Of Holding A Position

## Summary
Severity: High
Contest weight: 0.2346
Dataset id: 2033
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the value of the position the GmxV2PositionManager contract only takes into account the deposited collateral and the current PnL of the position. The calculation does not take Fees, discounts, funding & price impact into account. This will misprice the user's shares and can enable MEV opportunities as stepwise jumps in the share price will occur when the position is closed. Furthermore pending funding fees to be paid to the user and funding fees that have yet to be claimed but are no longer pending should be accounted for.

## Recommendation
The position should be valued as if it is incurring all fees which would be levied upon it when it is completely closed as well as any pending borrowing and funding fees. The GMX Reader contract has a function called getPositionInfo which returns the totalCostAmount. This variable includes all fees, discounts & funding charged to the user (not including any funding paid to the user) and can be used to calculate the real value of the position together with the pnlAfterPriceImpactUsd variable to include the price impact. Firstly, query the getPositionInfo function on the GMX Reader contract to retrieve the PositionInfo result. The PositionInfo has several fields which is important to us including PositionFundingFees funding and uint256 totalCostAmount. Specifically for the funding fees we need to account for: • positionInfo.fees.funding.claimableLongTokenAmount pending long token amount paid • positionInfo.fees.funding.claimableShortTokenAmount pending short token amount paid • bytes32 key = Keys.claimableFundingAmountKey(market, token, account); the already settled, but not yet claimed funding amount paid for each token
