# [H] Transaction does not revert after cancellation of orders fails

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L145-L161
Type: audit-issue

## Details
# Transaction does not revert after cancellation of orders fails

## Summary
After checking that the user has enough token_in allowance (account_allowance < order.amount_in), the execute_limit_order function cancels the order (self._cancel_limit_order(_uid)) but does not revert the transaction
## Vulnerability Detail
In the execute_limit_order function, after checking that the user has enough token_in allowance, the code tries to cancel the order by calling the internal function _cancel_limit_order(_uid). However, if the cancellation fails, the execution of the function continues without reverting the transaction.
The consequence of this vulnerability is that even if the cancellation fails, the rest of the code will execute as if the order was successfully canceled. This can lead to unexpected behavior and potentially allow an attacker to exploit the contract
## Impact
If a token transfer fails during the cancellation process, the order may not be properly cleaned up, and the user will lose funds associated with the order
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L145-L161
## Tool used

Manual Review

## Recommendation
By adding the revert statements after the self._cancel_limit_order(_uid) calls, the contract will revert the entire transaction if the cancellation fails, preventing any further execution and keeping the contract state consistent
https://github.com/seerether/Unstoppable/blob/50efe24c97fe282c39d47231c55a4a634f6cd63c/unstoppablemitigate7#L4-L12
