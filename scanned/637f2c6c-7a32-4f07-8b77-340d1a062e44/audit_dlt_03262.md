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

    function deposit(uint256 _pid, uint256 _amount) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        updatePool(_pid);
        ...
    }
```

The problem is `updatePool()` reverts when `totalAllocPoint == 0` and this value can be changed by stargate admin using [set()](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L100).

So user funds might be locked like the below.
1. The stargate staking contract had one pool and `totalAllocPoint = 10`.
2. In `StargateRewardableWrapper`, some users staked their funds using [deposit()](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20Wrapper.sol#L42).
3. After that, that pool was removed by the stargate admin due to an unexpected reason. So the admin called [set(0, 0)](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L100) to reset the pool. Then `totalAllocPoint = 0` now.
In the stargate contract, it's not so critical because this contract has [emergencyWithdraw()](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L184) to rescue funds without caring about rewards. Normal users can withdraw their funds using this function.
4. But in `StargateRewardableWrapper`, there is no logic to be used under the emergency and deposit/withdraw won't work because `_claimAssetRewards()` reverts in [updatePool()](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L147) due to 0 division.

## Tools Used
Manual Review

## Recommended Mitigation Steps
We should implement a logic for an emergency in `StargateRewardableWrapper`.

During the emergency, `_claimAssetRewards()` should return 0 without interacting with the staking contract and we should use `stakingContract.emergencyWithdraw()` to rescue the funds.


## Assessed type

Error
