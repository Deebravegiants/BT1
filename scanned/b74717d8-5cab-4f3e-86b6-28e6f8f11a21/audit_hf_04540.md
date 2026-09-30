# [M] M-20 | Unsafe Collateral Amount Because Of Fees

## Summary
Severity: Medium
Contest weight: 0.1597
Dataset id: 22104
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an order is settled, the account the order is committed for is charged orderFees. There are
validations in [AsyncOrder.validateRequest](https://github.com/GuardianAudits/perps-v3-1/blob/fd4c562868761bdcafb1a3dc080c3465e4e4de76/markets/perps-market/contracts/storage/AsyncOrder.sol#L333-L347) that the collateral value will not drop below the needed
margin after paying the fees.
The following must be true: currentAvailableMargin = [getRequiredMarginWithNewPosition](https://github.com/GuardianAudits/perps-v3-1/blob/fd4c562868761bdcafb1a3dc080c3465e4e4de76/markets/perps-market/contracts/storage/AsyncOrder.sol#L529-L583)() +
orderFees.
However, getRequiredMarginWithNewPosition returns 0 when a position is being reduced.
This makes the above expression equivalent to:
currentAvailableMargin = orderFees
This check is not sufficient. In the following scenario:
• required margin = $500
• currentAvailableMargin = $550
• orderFees = 100
The currentAvailableMargin = orderFees will pass, but after the account is charged the fees, its
margin will fall below the required margin and their positions will instantly become liquidatable.

## Recommendation
Validate the user is not liquidatable after settlement
