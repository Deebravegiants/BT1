### Title
First Staker with 1 Wei Inflates `rewardPerTokenStored` and Steals All Rewards - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.rewardPerToken()` divides by `totalKernelStaked` with no minimum-stake guard. An attacker who is the sole staker with 1 wei when `notifyRewardAmount` is called will cause `rewardPerTokenStored` to accumulate at `rewardRate * 1e18` per second, allowing them to drain the entire reward pool via `getReward()`.

---

### Finding Description

`rewardPerToken()` computes the per-token reward accumulator as:

```solidity
rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [1](#0-0) 

When `totalKernelStaked == 1` (1 wei), the division by 1 means the accumulator grows by `rewardRate * timeDelta * 1e18` per second. The `earned()` function then computes:

```solidity
balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION
``` [2](#0-1) 

With `balanceOf[attacker] = 1` and the inflated delta `= rewardRate * timeDelta * 1e18`:

```
earned = 1 * rewardRate * timeDelta * 1e18 / 1e18 = rewardRate * timeDelta
```

This equals the **total rewards distributed** in that window — the attacker earns 100% of all rewards.

`stake()` enforces only `_amount != 0`, so 1 wei is a valid stake: [3](#0-2) 

`notifyRewardAmount` only checks `totalKernelStaked > 0`, which 1 wei satisfies: [4](#0-3) 

The contract's own NatSpec comment even acknowledges this behavior, framing it as a feature rather than a vulnerability: [5](#0-4) 

The `updateReward` modifier snapshots `rewardPerTokenStored` and `userRewardPerTokenPaid` on every user action, so the inflated value is permanently locked in for the attacker: [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

An attacker who is the sole staker (or who stakes before any other user) when `notifyRewardAmount` is called will earn the entirety of the reward pool. Legitimate stakers who join later receive `rewardPerToken` already inflated to the maximum, so their `earned()` delta is zero or negligible. All reward tokens transferred into the contract by the admin are claimable by the attacker via `getReward()` with no delay. [7](#0-6) 

---

### Likelihood Explanation

**Medium.** The attack requires the attacker to be the only staker (or the dominant staker with 1 wei) at the moment `notifyRewardAmount` is called. This is realistic in two scenarios:

1. **Cold-start**: The pool is freshly deployed or a reward period just ended. The attacker stakes 1 wei before any legitimate user, then the admin calls `notifyRewardAmount`.
2. **Front-run**: The attacker monitors the mempool for the admin's `notifyRewardAmount` transaction, withdraws all their legitimate stake, and re-stakes 1 wei in the same block ahead of the admin's call.

The cost to the attacker is 1 wei of KERNEL plus gas. The reward is the entire reward pool.

---

### Recommendation

1. **Enforce a minimum stake**: Require `_amount >= MINIMUM_STAKE` (e.g., `1e18`) in `stake()` and `stakeFor()`.
2. **Enforce a minimum `totalKernelStaked` in `notifyRewardAmount`**: Revert if `totalKernelStaked < MINIMUM_TOTAL_STAKED` rather than just `> 0`.
3. **Alternatively, use a virtual offset**: Add a constant virtual supply (e.g., `1e18`) to the denominator in `rewardPerToken()` so that a 1 wei stake cannot dominate the accumulator. [1](#0-0) 

---

### Proof of Concept

```
Setup:
  - KERNEL token with 18 decimals, rewardToken with 18 decimals
  - duration = 7 days = 604800 seconds
  - rewardAmount = 1e18 (1 reward token)
  - rewardRate = 1e18 / 604800 ≈ 1653 wei/second

Step 1: Attacker stakes 1 wei
  kernelToken.approve(pool, 1)
  pool.stake(1)
  → totalKernelStaked = 1

Step 2: Admin calls notifyRewardAmount(1e18)
  → totalKernelStaked == 1 > 0, check passes
  → rewardRate = 1e18 / 604800 ≈ 1653

Step 3: After T seconds (e.g., T = 604800, full duration)
  rewardPerToken() = 0 + (1653 * 604800 * 1e18) / 1
                   ≈ 1e36

  earned(attacker) = 1 * (1e36 - 0) / 1e18 = 1e18

Step 4: Attacker calls getReward()
  → receives ≈ 1e18 reward tokens (the entire reward pool)

Step 5: Attacker calls initiateWithdrawal(1) and claimWithdrawal after delay
  → recovers their 1 wei KERNEL stake

Net gain: ~1e18 reward tokens at a cost of 1 wei KERNEL + gas.
Any legitimate staker who joins after Step 2 finds userRewardPerTokenPaid
already set to the inflated rewardPerTokenStored, earning zero rewards.
``` [1](#0-0) [2](#0-1)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-286)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-424)
```text
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-570)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
