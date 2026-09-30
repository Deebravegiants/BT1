# [M] Recommended Explicit Pool Validity Checks

## Summary
Severity: Medium
Contest weight: 0.6994
Dataset id: 13120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SushiSwap has a central contract MasterChef that has been tasked with not only the migration (Section 3.1), but also the pool management, staking/unstaking support, as well as the reward distribution to various pools and stakers. In the following, we show the key pool data structure. Note all added pools are maintained in an array poolInfo.

```solidity
// Info of each pool.
struct PoolInfo {
    IERC20 lpToken; // Address of LP token contract.
    uint256 allocPoint; // How many allocation points assigned to this pool. SUSHIs distribute per block.
    uint256 lastRewardBlock; // Last block number that SUSHIs distribution occurs.
    uint256 accSushiPerShare; // Accumulated SUSHIs per share, times 1e12. See below.
}

// Info of each pool.
PoolInfo[] public poolInfo;
```

Confidential

When there is a need to add a new pool, set a new allocPoint for an existing pool, stake (by depositing the supported UniswapV2s LP tokens), unstake (by redeeming previously deposited UniswapV2s LP tokens), query pending SUSHI rewards, or migrate the pool assets, there is a constant need to perform sanity checks on the pool validity. The current implementation simply relies on the implicit, compiler-generated bound-checks of arrays to ensure the pool index stays within the array range [0, poolInfo.length-1]. However, considering the importance of validating given pools and their numerous occasions, a better alternative is to make explicit the sanity checks by introducing a new modifier, say validatePool. This new modifier essentially ensures the given _pool_id or _pid indeed points to a valid, live pool, and additionally give semantically meaningful information when it is not!

```solidity
// Deposit LP tokens
MasterChef for SUSHI allocation.
function deposit(uint256 _pid, uint256 _amount) public {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pending = user.amount.mul(pool.accSushiPerShare).div(1e12).sub(user.rewardDebt);
        safeSushiTransfer(msg.sender, pending);
    }
    pool.lpToken.safeTransferFrom(address(msg.sender), address(this), _amount);
    user.amount = user.amount.add(_amount);
    user.rewardDebt = user.amount.mul(pool.accSushiPerShare).div(1e12);
    emit Deposit(msg.sender, _pid, _amount);
}
```

We highlight that there are a number of functions that can be benefited from the new pool-validating modifier, including set(), migrate(), deposit(), withdraw(), emergencyWithdraw(), pendingSushi() and updatePool().

## Recommendation
Apply necessary sanity checks to ensure the given _pid is legitimate. Accordingly, a new modifier validatePool can be developed and appended to each function in the above list.

```solidity
modifier validatePool(uint256 _pid) {
    require(_pid < poolInfo.length, "chef: pool exists?");
}

// Deposit LP tokens
MasterChef for SUSHI allocation.
function deposit(uint256 _pid, uint256 _amount) public validatePool(_pid) {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pending = user.amount.mul(pool.accSushiPerShare).div(1e12).sub(user.rewardDebt);
        safeSushiTransfer(msg.sender, pending);
    }
    pool.lpToken.safeTransferFrom(address(msg.sender), address(this), _amount);
    user.amount = user.amount.add(_amount);
    user.rewardDebt = user.amount.mul(pool.accSushiPerShare).div(1e12);
    emit Deposit(msg.sender, _pid, _amount);
}
```
