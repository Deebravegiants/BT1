# [M] `depositAndFix` can be made to fail

## Summary
Severity: Medium
Contest weight: 0.1107
Dataset id: 1059
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There’s a griefing attack where an attacker can make any user transaction for `TempusController.depositAndFix` fail. In `_depositAndFix`, `swapAmount` many yield shares are swapped to principal where `swapAmount` is derived from the function arguments. A final `assert(yieldShares.balanceOf(address(this)) == 0)` statement checks that the yield shares of the contract are zero after the swap. This is only true if no other yield shares were already in the contract.

However, an attacker can frontrun this call and send the smallest unit of yield shares to the contract which then makes the original deposit-and-fix transaction fail.

## Recommendation
Remove the `assert` check.

Good catch. This can block users from doing this action via controller

[mijovic patched](https://github.com/code-423n4/2021-10-tempus-findings/issues/20#issuecomment-948350220):

Fixed in <https://github.com/tempus-finance/tempus-protocol/pull/370>
