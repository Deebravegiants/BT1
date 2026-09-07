# [M] Permanent funds lock in `StargateRewardableWrapper`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/27
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/stargate/StargateRewardableWrapper.sol#L48


# Vulnerability details

## Impact
The staked funds might be locked because the deposit/withdraw/transfer logic reverts.

## Proof of Concept
In `StargateRewardableWrapper`, `_claimAssetRewards()` claims the accumulated rewards from the staking contract and it's called during every deposit/withdraw/transfer in [_beforeTokenTransfer()](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L124) and [_claimAndSyncRewards()](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L77).

```solidity
    function _claimAssetRewards() internal override {
        stakingContract.deposit(poolId, 0);
    }
```

And in the stargate staking contract, [deposit()](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L153) calls [updatePool()](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L136) inside the function.

```solidity
    function updatePool(uint256 _pid) public {
        PoolInfo storage pool = poolInfo[_pid];
        if (block.number <= pool.lastRewardBlock) {
            return;
        }
        uint256 lpSupply = pool.lpToken.balanceOf(address(this));
        if (lpSupply == 0) {
            pool.lastRewardBlock = block.number;
            return;
        }
        uint256 multiplier = getMultiplier(pool.lastRewardBlock, block.number);
        uint256 stargateReward = multiplier.mul(stargatePerBlock).mul(pool.allocPoint).div(totalAllocPoint); //@audit revert when totalAllocPoint = 0

        pool.accStargatePerShare = pool.accStargatePerShare.add(stargateReward.mul(1e12).div(lpSupply));
        pool.lastRewardBlock = block.number;
    }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/27_
