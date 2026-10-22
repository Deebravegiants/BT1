# [M] M-05 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-xeth-mitigation
Published: 2023-06-16
Source: https://github.com/code-423n4/2023-06-xeth-mitigation-findings/issues/8
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-xeth/commit/aebc3244cbb0deb67f3cdef160b390da27888de7#L230


# Vulnerability details

If wxETH drips when nothing is staked, then the first staker can claim every drop.

# Mitigation
https://github.com/code-423n4/2023-05-xeth/commit/aebc3244cbb0deb67f3cdef160b390da27888de7

This PR is added in the method `_accrueDrip()` to return if `totalSupply() == 0` to avoid dropping at 0.

But this doesn't solve the original problem, because when supply changes from `0` to `1`, it doesn't modify `lastReport`.
So suppose a user `stake(1)` immediately after `stake(1)` again, the second `stake(1)` to calculate the blockDelta, `uint256 blockDelta = block.number - lastReport;`
At this point `blockDelta` is still very large, which will cause drap to be taken up as well

It should be similar to `dripEnabled` to true which will modify `lastReport = block.number`.

A simple suggestion is as follows:

```solidity
    function _accrueDrip() private {
        /// @dev if drip is disabled, no need to accrue
-       if (!dripEnabled || totalSupply() == 0) return;
+       if (!dripEnabled) return;
+       if (totalSupply() == 0) { 
+         lastReport = block.number; 
+         return;
+       }
```


## Assessed type

Context
