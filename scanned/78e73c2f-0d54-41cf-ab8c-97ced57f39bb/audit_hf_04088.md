# [H] AIMUTI-1 | Severely Undercollateralized Positions Cannot Be Liquidated

## Summary
Severity: High
Contest weight: 0.2339
Dataset id: 20543
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation, an issue appears when the total available user amount to liquidate is equal to the
input liquidation amount. The input liquidation amount is passed to the liquidate function from the
LiquidatorProxyV4WithGenericTrader contract when liquidating a position.
Liquidation always creates a second set of call and sell actions. When the amounts are equal, the
second call and sell action will be executed with 0 as input. This results in execution failing because
the first set of actions clears the withdrawal position.
It is also worth mentioning that the account is not vaporizable in this state since it still holds a
positive balance in the GM market.

## Recommendation
In the createActionsForUnwrapping function from AsyncIsolationModeUnwrapperTraderImpl do not
create a second call and sell action if the difference between the input amount and available amount
is zero.
If the mentioned solution is implemented, 2 dummy actions that do not have any side-effects should
be created as a workaround. This is needed to maintain compatibility with the liquidation proxy,
which at this point already creates an action array using the length 4 for the liquidation unwrapping.
A different solution can be modifying the LiquidatorProxyV4WithGenericTrader to determine if this
would be a 2 or 4 step liquidation.
