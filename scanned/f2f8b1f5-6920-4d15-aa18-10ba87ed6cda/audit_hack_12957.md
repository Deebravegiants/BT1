# [H] Liquidations will not be able to be executed if user has a very small margin and the amount_out_received from closing a position is greater than the debt_amount

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
Type: audit-issue

## Details
# Liquidations will not be able to be executed if user has a very small margin and the amount_out_received from closing a position is greater than the debt_amount

## Summary
Liquidations will not be able to be executed if user has a very small margin and the `amount_out_received` from closing a position is greater than the `debt_amount`

## Vulnerability Detail

To liquidate positions, the `liquidate` function has to be called. Essentially what it does is to close the position in the first place.

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375

After closing the position, if the swapped amount was higher than the debt from that position, a penalty is charged to the account that opened the position in the first place.

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L372

If a trader opens a position with all its available margin, so he stays will 0 margin in his balance, and when the position is liquidated the amount swapped is bigger than the debt, charging the penalty will fail if `penalty` is bigger than the `trader_pnl` added when closing the position.

```solidity
penalty: uint256 = debt_amount * self.liquidation_penalty / PERCENTAGE_BASE

trader_pnl: uint256 = amount_out_received - position_debt_amount
```


Because trader has less balance on margin that the penalty charged to his account the transaction would revert due to underflow. Therefore, traders have a pretty high change of creating un-liquidable positions while the swap when closing a position is larger than the debt:

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L259
## Impact
Positions will be un-liquidable when created with all the available margin and having a positive swap when closing the position.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
## Tool used

Manual Review

## Recommendation
Do not push to substract the penalty, otherwise liquidations will be blocked
