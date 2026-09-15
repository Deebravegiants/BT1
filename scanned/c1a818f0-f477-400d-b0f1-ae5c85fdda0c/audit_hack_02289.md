# [M] \[M01\] Incorrect event parameters

## Summary
Severity: Medium
Source: https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/financial-templates/optimistic-rewarder/OptimisticRewarderBase.sol#L64-L69
Type: audit-issue

## Details
The `OptimisticRewarderBase` contract defines a [Requested event](https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/financial-templates/optimistic-rewarder/OptimisticRewarderBase.sol#L64-L69) which is emitted from the `requestRedemption` function when a redemption is requested. This event is defined to emit the [expiry time of the redemption](https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/financial-templates/optimistic-rewarder/OptimisticRewarderBase.sol#L68) as its last parameter. However, [when the event is emitted](https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/financial-templates/optimistic-rewarder/OptimisticRewarderBase.sol#L174), its last parameter is incorrectly set to the [current time](https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/financial-templates/optimistic-rewarder/OptimisticRewarderBase.sol#L167).

Similarly the [Redeemed event](https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/financial-templates/optimistic-rewarder/OptimisticRewarderBase.sol#L305) reads the expiry time after the record is deleted, so it will be incorrectly set to zero.

Given that this event can be used to trigger off-chain computations, consider updating the emitted value appropriately.

**Update:** _Fixed as of commit [f04eef9](https://github.com/UMAprotocol/protocol/pull/3694/commits/f04eef99c09dc09b9d7ff3ff2d6d10dd4a1975e3) in [PR3694](https://github.com/UMAprotocol/protocol/pull/3694)._
