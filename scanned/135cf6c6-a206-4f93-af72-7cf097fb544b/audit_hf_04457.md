# [H] H-08 | Disproportional Share Allocation

## Summary
Severity: High
Contest weight: 0.2634
Dataset id: 21948
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the afterOrderExecution function the amount of shares minted to a depositor is dependent on the
sizeDeltaUsd of the order. However this method ignores price impact which the vault position
experiences due to the increase order.
This allows depositors to receive more shares of the vault than they ought to when their order is
negatively impacted.
For example:
• Vault is 2x long on GMX with $100,000 sizeInUsd
• PnL is currently 0 and the vault position is worth $50,000
• User A deposits with $5,000 and the sizeInUsd for their order is $10,000
• User A’s order is negatively impacted such that it experiences a $1,000 loss relative to the current
market price
• Ignoring fees, User A is credited with their 5,000 collateralToken deposit for share calculations
• The vault worth excluding the trader’s collateral is $49,000 as the negative price impact is
attributed
• The trader receives $5,000/$49,000 ~= 20.41% of the share supply
• Instead the trader should have received $4,000/$50,000 ~= 18% of the share supply by rightfully
charging the impact to the depositor

## Recommendation
Compute the amount of price impact that the depositor experienced by comparing the sizeInUsd of
the order to the sizeInTokens increase of the position with respect to the current market prices in
GMX. Then deduct this amount from the user’s credited deposit value when calling the _mint
function.
