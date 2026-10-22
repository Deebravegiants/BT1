# [H] Wrong implementation to re-imburse keepers

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237
Type: audit-issue

## Details
# Wrong implementation to re-imburse keepers

## Summary
Wrong implementation to re-imburse keepers

## Vulnerability Detail
Currently in `Dca` and `LimitOrders` a keeper is the one that will execute the order when the parameters are met. 
The timestamp to execute the `dca` and the price to execute the `limitOrder` are met.

A user does not pay `executionFee` in advance to the keepers. The keepers are going to execute the order in hopes it goes forward and they don't lose funds executing it.

This has some problems that allows the user to penalize keepers by willingly posting orders that won't be able to be executed in the future.

Example 1:

- Bad user posts an order calling `post_dca_order` or `post_limit_order` . The orders require the user to actually have the funds and have approved the respective contract to use them when executing the order.

- After posting the order, user revokes approval of the funds, or simply transfers them to another account or swaps them.
 
- When execution happens because the params are met, execution will fail because keepers can't pull the funds from the user, and the order will be canceled:

```solidity
account_balance: uint256 = ERC20(order.token_in).balanceOf(order.account)
 if account_balance < order.amount_in:
        log LimitOrderFailed(_uid, order.account, "insufficient balance")
        self._cancel_limit_order(_uid)
        return
```

Example 2:

- Re-imbursement of the keepers is not done according to their spending, either refunding too much or to low depending on the order

```solidity
profit: uint256 = amount_out - order.min_amount_out
self._safe_transfer(order.token_out, msg.sender, profit/2)
```
Currently half of the profit swapping is re-imbursed to the keepers. This will not return a fair amount for any of both parties.


## Impact
- Keepers will lose funds if executing the order fails and it is canceled.
- The fee that is re-imbursed when it does not fail is not accurate at all

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L101-L143
## Tool used

Manual Review

## Recommendation
Consider implementing the gasLeft() pattern before and after the transaction to pay for an execution fee for the keeper before hand. If the keeper does not use all the executionFee, it should be re-imbursed to the user.
