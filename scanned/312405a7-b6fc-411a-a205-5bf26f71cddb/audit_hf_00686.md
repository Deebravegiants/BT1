# [M] M-07 | Depositing Minimum Amount Leads To Position Closure

## Summary
Severity: Medium
Contest weight: 0.1875
Dataset id: 2237
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user deposits the MINIMUM_MINT_AMOUNT into an empty LT a position will be created and most likely closed right after. This punishes the user with paying for order fees twice without any beneﬁt:
• User deposits the MINIMUM_MINT_AMOUNT (100 sUSD) into an empty LT
• The _validateMintAmount check is executed and it passes as the given amount is not less than the MINIMUM_MINT_AMOUNT of 100 sUSD
• The given amount of 100 sUSD is deposited as margin
• The _canRebalance check is executed and it passes as the remainingMargin (100 sUSD) in the position is not less than the MINIMUM_MARGIN_BALANCE (100 sUSD) it is equal and the position is heavily under leveraged as it has no size yet
• Therefore _rebalance will be executed and a delayed order to open a position in perps v2 is created
• The delayed order is executed:
• To open the position order fees and price impact must be paid and therefore the position's remainingMargin is probably < 100 sUSD now
• This will trigger the rebalancer:
• The _canRebalance check is executed and it will pass as the remainingMargin after paying for order fees is less than the MINIMUM_MARGIN_BALANCE now while the notional value of the position is > 0
• Therefore _rebalance will be executed and a delayed order to close the position in perps v2 is created
• The delayed order is executed:
• The position is closed and more order fees are paid

## Recommendation
The MINIMUM_MINT_AMOUNT should be signiﬁcantly more than the MINIMUM_MARGIN_BALANCE.
