# [H] DCA order can be cancelled even when the token transfers have not been successfully completed

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L284-L292
Type: audit-issue

## Details
# DCA order can be cancelled even when the token transfers have not been successfully completed

## Summary
The cancel_dca_order Function cancels a DCA order without verifying if the token transfers are successful
## Vulnerability Detail
In the cancel_dca_order function, it first retrieves the DCA order associated with the given _uid. Then, it checks if the message sender (caller) is the same as the owner of the DCA order. If the caller is the owner, it calls the internal function _cancel_dca_order to perform the cancellation process.
The vulnerability arises from the fact that the _cancel_dca_order function doesn't include any token transfer checks. The _cancel_dca_order function calls another internal function _cleanup_order, which effectively removes the DCA order from the contract storage and updates the user's list of DCA orders. However, it doesn't revert or handle any potential token transfer failures.
## Impact
if the DCA order involves token transfers fail some reason, the user may not receive their tokens back as expected leading to loss of funds
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L284-L292
## Tool used

Manual Review

## Recommendation
https://github.com/seerether/Unstoppable/blob/main/unstoppablemitigate4
Make sure to also include the _safe_transfer function in the contract, as it is used for token transfers and error handling:
https://github.com/seerether/Unstoppable/blob/main/unstoppablemitigate4a
