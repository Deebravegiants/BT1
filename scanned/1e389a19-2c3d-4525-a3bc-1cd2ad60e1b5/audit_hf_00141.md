# [M] `maxSumOfPrices` check is broken

## Summary
Severity: Medium
Contest weight: 0.1685
Dataset id: 536
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`rentAllCards()` requires the sender to specify a `_maxSumOfPrices` parameter which specifies “limit to the sum of the bids to place” as specified in the Natspec @param comment. This is apparently for front-run protection.

However, this function parameter constraint for `_maxSumOfPrices` is broken in the function implementation which leads to the total number of bids placed greater than the `_maxSumOfPrices` specified.

The impact of this is that the user may not have sufficient deposited, be foreclosed upon and/or impacted on other bids/markets.

Scenario: Assume two cards for a market with current winning rentals of 50 each. `_maxSumofPrices` = 101 passes check on L643 but then the forced 10% increase on L650 (assuming sender is not the owner of either card) causes `newRentals` to be called with 55 for each card thus totalling to 110 which is > 101 as requested by the user.

Recommend modifing the max sum of prices check logic to consider the 10% increase scenarios. Document and suggest the max sum of prices for the user in the UI based on the card prices and 10% requirement depending on card ownership.

fixed [here](https://github.com/RealityCards/RealityCards-Contracts/commit/10dfc77977f19fd4c233eb294ebc566526be9546)

## Recommendation
No recommendation
