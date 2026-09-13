# [M] erc777s should not be supported. Malicious trader can just grief keepers to not execute their orders.

## Summary
Severity: Medium
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L158
Type: audit-issue

## Details
# erc777s should not be supported. Malicious trader can just grief keepers to not execute their orders.

## Summary
erc777s should not be supported. Malicious trader can just grief keepers to not execute their orders.

## Vulnerability Detail
It was very explicit from the sponsors that he wanted to know if erc777s were actually supported by at least the spot module. 

In the spot module, erc777s should not be supported. The usage of those tokens with the current implementation allows to continuously grief keepers out of gas.

When a keeper executes an order, in this case for whatever erc777. The `_safe_transfer_from` is triggered after cleaning up the order. Therefore the trader can implement on the callback that `_safe_transfer_from` has before sending the tokens another call again to `execute_limit_order` , as it does not have a non-reentrant modifier. In the callback the user can also spend as much gas as they want to the expense of the keeper. After calling `execute_limit_order` on the callback again, the transaction will fail due to the order already being deleted one line before: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L158

Therefore, the keeper will have lost all the gas with no fee paid. 

## Impact
Loss of gas for keepers

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161
## Tool used

Manual Review

## Recommendation
Do not support erc777 or add a non-reentrant.
