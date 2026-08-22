# [M] [ADRIRO-NEW-M-04] CVX tracking misses to account for rewards

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/56
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L206


# Vulnerability details

## Summary

The updated codebase now tracks CVX balances internally. While this is correctly handled in most operations, accounting fails to consider CVX tokens coming from claimed rewards.

## Impact

CVX balances in the Votium strategy are now tracked internally. This is done by the introduction of a `trackedCvxBalance` variable that is updated whenever CVX is bought, sold or locked in Convex.

However, the implementation fails to consider potential CVX tokens coming from rewards. When claiming rewards from either Convex or Votium, CVX tokens might be transferred to the contract, and should be accounted for as part of `trackedCvxBalance`, since these are tokens owned by the protocol.

This wasn't an issue before, since CVX balance was simply queried on demand using `balanceOf()`. But with the introduction of custom tracking for CVX tokens, a failure to consider this scenario would mean not accounting these rewards as part of the owned CVX by the protocol.

## Recommendation

When claiming rewards in `claimRewards()`, account for any difference in CVX balance and add that to the `trackedCvxBalance` variable.

```diff
    function claimRewards(
        IVotiumMerkleStash.ClaimParam[] calldata _claimProofs
    ) public onlyRewarder {
+       uint256 cvxBalanceBefore = IERC20(CVX_ADDRESS).balanceOf(address(this));
        claimVotiumRewards(_claimProofs);
        claimVlCvxRewards();
+       uint256 cvxBalanceAfter = IERC20(CVX_ADDRESS).balanceOf(address(this));
+       trackedCvxBalance += cvxBalanceAfter - cvxBalanceBefore;
    }
```



## Assessed type

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/56_
