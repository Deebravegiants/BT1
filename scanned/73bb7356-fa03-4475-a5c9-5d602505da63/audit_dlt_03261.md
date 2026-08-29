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

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/30_
