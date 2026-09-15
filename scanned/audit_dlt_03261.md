# [M] Possible rounding during the reward calculation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/30
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L86


# Vulnerability details

## Impact
Some rewards might be locked inside the contract due to the rounding loss.

## Proof of Concept
`_claimAndSyncRewards()` claimed the rewards from the staking contract and tracks `rewardsPerShare` with the current supply.

```solidity
    function _claimAndSyncRewards() internal virtual {
        uint256 _totalSupply = totalSupply();
        if (_totalSupply == 0) {
            return;
        }
        _claimAssetRewards();
        uint256 balanceAfterClaimingRewards = rewardToken.balanceOf(address(this));

        uint256 _rewardsPerShare = rewardsPerShare;
        uint256 _previousBalance = lastRewardBalance;

        if (balanceAfterClaimingRewards > _previousBalance) {
            uint256 delta = balanceAfterClaimingRewards - _previousBalance;
            // {qRewards/share} += {qRewards} * {qShare/share} / {qShare}
            _rewardsPerShare += (delta * one) / _totalSupply; //@audit possible rounding loss
        }
        lastRewardBalance = balanceAfterClaimingRewards;
        rewardsPerShare = _rewardsPerShare;
    }
```

It uses [one](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L38) as a multiplier and from [this setting](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20Wrapper.sol#L32-L39) we know it has the same decimals as `underlying`(thus `totalSupply`).

My concern is `_claimAndSyncRewards()` is called for each deposit/transfer/withdraw in [_beforeTokenTransfer()](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L124) and it will make the rounding problem more serious.

1. Let's consider [underlyingDecimals = 18](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20Wrapper.sol#L34). `totalSupply = 10**6 with 18 decimals`, `rewardToken` has 6 decimals.
And total rewards for 1 year are `1M rewardToken` for `1M totalSupply`.
2. With the above settings, `_claimAndSyncRewards()` might be called every 1 min due to the frequent user actions.
3. Then expected rewards for 1 min are `1000000 / 365 / 24 / 60 = 1.9 rewardToken = 1900000 wei`.
4. During the [division](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L86), it will be `1900000 * 10**18 / (1000000 * 10**18) = 1`.
So users would lose almost 50% of rewards due to the rounding loss and these rewards will be locked inside the contract.

## Tools Used
Manual Review

## Recommended Mitigation Steps
I think there would be 2 mitigation.
1. Use a bigger multiplier.
2. Keep the remainders and use them next time in `_claimAndSyncRewards()` like this.

```solidity
    if (balanceAfterClaimingRewards > _previousBalance) {
        uint256 delta = balanceAfterClaimingRewards - _previousBalance; //new rewards
        uint256 deltaPerShare = (delta * one) / _totalSupply; //new delta per share

        // decrease balanceAfterClaimingRewards so remainders can be used next time
        balanceAfterClaimingRewards = _previousBalance + deltaPerShare * _totalSupply / one;

        _rewardsPerShare += deltaPerShare;
    }
    lastRewardBalance = balanceAfterClaimingRewards;
```


## Assessed type

Math
