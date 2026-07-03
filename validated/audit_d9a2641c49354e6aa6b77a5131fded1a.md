### Title
Precision loss in `rewardPerToken()` allows any unprivileged caller to permanently freeze reward accrual for all stakers via repeated `getReward()` calls - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool.rewardPerToken()` performs integer division that truncates to zero when the elapsed time is short relative to `totalKernelStaked`. Because the `updateReward` modifier unconditionally advances `updatedAt` even when `rewardPerToken()` does not change, any caller can repeatedly invoke the permissionless `getReward()` function to consume time intervals without recording any reward accrual, permanently destroying yield for every staker.

---

### Finding Description

`rewardPerToken()` computes the global reward accumulator as:

```solidity
// KernelDepositPool.sol L408-413
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [1](#0-0) 

The numerator is `rewardRate * timeDelta * 1e18`. When `timeDelta` is small enough that this product is less than `totalKernelStaked`, Solidity's integer division truncates the result to zero, leaving `rewardPerTokenStored` unchanged.

The `updateReward` modifier runs before every state-changing function and **always** advances `updatedAt` to `lastTimeRewardApplicable()`, regardless of whether `rewardPerToken()` actually increased:

```solidity
// KernelDepositPool.sol L232-242
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();   // <-- always advances, even on truncation
    if (_account != address(0)) {
        rewards[_account] = earned(_account);
        userRewardPerTokenPaid[_account] = rewardPerTokenStored;
    }
    _;
}
``` [2](#0-1) 

`getReward()` is callable by any address with no stake requirement and no access control:

```solidity
// KernelDepositPool.sol L382-390
function getReward() external nonReentrant updateReward(msg.sender) {
    uint256 rewardAmount = rewards[msg.sender];
    if (rewardAmount > 0) {
        rewards[msg.sender] = 0;
        rewardsToken.safeTransfer(msg.sender, rewardAmount);
        emit RewardsClaimed(msg.sender, rewardAmount);
    }
}
``` [3](#0-2) 

An attacker with zero stake calls `getReward()` within the truncation window. The modifier fires, `updatedAt` advances, but `rewardPerTokenStored` stays the same. The elapsed time is permanently lost — no staker ever receives rewards for that interval. Repeating this every few seconds drains the entire reward budget.

---

### Impact Explanation

**High — Theft of unclaimed yield / permanent freezing of unclaimed yield for all stakers.**

Every time the attacker successfully calls `getReward()` within the truncation window, the rewards that should have accrued during that interval are permanently unrecoverable. Over a full reward period, a sustained attacker can eliminate 100% of distributed rewards. The `rewardsToken` balance remains locked in the contract with no mechanism to reclaim it.

---

### Likelihood Explanation

**Medium.**

The attack is most effective when `rewardsToken` has low decimals (e.g., USDT/USDC with 6 decimals). The `KernelDepositPool` accepts any ERC-20 as `rewardsToken` at initialization.

Concrete example with USDT rewards:

```
rewardRate  = 100e6 USDT / 604800 s  ≈ 165 (USDT units/second)
DECIMAL_PRECISION = 1e18
totalKernelStaked = 1_000e18 KERNEL

Truncation condition:
  rewardRate * timeDelta * 1e18 < totalKernelStaked
  165 * timeDelta * 1e18 < 1_000e18
  timeDelta < 1_000 / 165 ≈ 6.06 seconds
```

The attacker must call `getReward()` at most every ~6 seconds. On L2 chains (Arbitrum, Base, Optimism) where this contract is deployed, block times are 0.25–2 seconds and gas costs are negligible, making sustained bot-driven exploitation straightforward. The attacker needs no capital — zero KERNEL stake is required.

---

### Recommendation

1. **Do not advance `updatedAt` when `rewardPerToken()` did not change.** Only update `updatedAt` if the computed `rewardPerToken` is strictly greater than `rewardPerTokenStored`:

```solidity
modifier updateReward(address _account) {
    uint256 newRewardPerToken = rewardPerToken();
    if (newRewardPerToken > rewardPerTokenStored) {
        rewardPerTokenStored = newRewardPerToken;
        updatedAt = lastTimeRewardApplicable();
    }
    if (_account != address(0)) {
        rewards[_account] = earned(_account);
        userRewardPerTokenPaid[_account] = rewardPerTokenStored;
    }
    _;
}
```

2. **Scale `rewardRate` by `DECIMAL_PRECISION` at storage time** (in `notifyRewardAmount`) so the numerator in `rewardPerToken()` is always large enough to avoid truncation for any reasonable `timeDelta`.

3. **Restrict `getReward()` to callers with a non-zero staked balance**, or add a minimum elapsed-time guard before allowing `updateReward` to advance `updatedAt`.

---

### Proof of Concept

```
Setup:
  rewardsToken = USDT (6 decimals)
  duration     = 7 days (604800 s)
  reward       = 100e6 USDT
  rewardRate   = 100e6 / 604800 ≈ 165
  totalKernelStaked = 1_000e18 KERNEL

Truncation window:
  165 * timeDelta * 1e18 / 1_000e18 = 0  when timeDelta ≤ 6 s

Attack loop (bot, no KERNEL required):
  t=0:      admin calls notifyRewardAmount → updatedAt = 0
  t=5:      attacker calls getReward()
              rewardPerToken() = 0 + (165 * 5 * 1e18) / 1_000e18 = 825e18/1_000e18 = 0 (truncated)
              updatedAt advances to t=5, rewardPerTokenStored unchanged
  t=10:     attacker calls getReward()
              rewardPerToken() = 0 + (165 * 5 * 1e18) / 1_000e18 = 0 (truncated)
              updatedAt advances to t=10
  ... repeated every 5 s for 604800 s (7 days) ...

Result:
  rewardPerTokenStored = 0 throughout the entire reward period
  All stakers earn 0 rewards
  100e6 USDT remains locked in the contract forever
```

The attacker calls `getReward()` (lines 382–390) with zero stake. Each call triggers `updateReward` (lines 232–242), which advances `updatedAt` (line 234) while `rewardPerToken()` (lines 408–413) truncates to zero. The entire 100 USDT reward budget is silently destroyed. [4](#0-3) [1](#0-0) [3](#0-2)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-413)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
```
