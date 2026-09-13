# [H] A limit order with amount_in set to 0 can be posted

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L81-L108
Type: audit-issue

## Details
# A limit order with amount_in set to 0 can be posted

## Summary
In the post_limit_order function, there is no verification to ensure that the amount_in of tokens being transferred from the user's account to the contract is a non-zero value. It is assumed that the user will provide a valid and non-zero amount_in.
## Vulnerability Detail
The vulnerability in the post_limit_order function is that it does not check whether the amount_in of tokens being transferred from the user's account to the contract is a non-zero value. As a result, a user can post a limit order with amount_in set to 0, allowing them to effectively bypass the requirement of having sufficient funds to fulfill the order.
## Impact
If the user mistakenly provides a zero amount_in, the contract will still attempt to execute the transfer, resulting in the loss of the user's funds.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L81-L108
## Tool used

Manual Review

## Recommendation
Add a check at the beginning of the function to verify that _amount_in is greater than 0. With this check in place, the contract will reject any limit order that has _amount_in set to 0, and it will ensure that users provide a valid and non-zero value for _amount_in.
https://github.com/seerether/Unstoppable/blob/8216efa744c8387e61f3f51f9dfe7fcce2ebbd69/unstoppablemitigate9#L11
