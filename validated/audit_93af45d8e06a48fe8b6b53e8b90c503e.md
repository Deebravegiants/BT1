### Title
First Depositor Steals All Staking Rewards via 1-Wei Stake — (`contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` accumulates `rewardPerTokenStored` by dividing by `totalKernelStaked`. Because `stake()` accepts any non-zero amount and `notifyRewardAmount()` only requires `totalKernelStaked > 0`, an attacker who stakes **1 wei** before any legitimate user causes the entire reward distribution to be credited to that 1-wei position, stealing all unclaimed yield for the period.

---

### Finding Description

`KernelDepositPool` is a Synthetix-style staking contract. The core accumulator is:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L408-L413
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
```

And the per-user earnings:

```solidity
// L421-L423
function earned(address _account) public view returns (uint256) {
    return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
        + rewards[_account];
}
```

`stake()` enforces only `_amount != 0`:

```solidity
// L281-L288
function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    if (_amount == 0) revert AmountZero();
    balanceOf[msg.sender] += _amount;
    totalKernelStaked += _amount;
    kernelToken.safeTransferFrom(msg.sender, address(this), _amount);
    emit Staked(msg.sender, _amount);
}
```

`notifyRewardAmount()` enforces only `totalKernelStaked != 0`:

```solidity
// L566-L570
function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
    if (_amount == 0) revert AmountZero();
    if (totalKernelStaked == 0) revert NoStakedTokens();
    ...
    rewardRate = receivedAmount / duration;
```

The contract's own NatSpec comment acknowledges the design gap:

> *"Otherwise, staking just 1 wei by any address will ensure that the contract never has any unallocated rewards."*

This comment frames 1-wei staking as a **solution** to unallocated rewards, but it simultaneously creates the attack surface: whoever stakes that 1 wei first becomes the sole beneficiary of the entire reward stream until legitimate stakers arrive.

When `totalKernelStaked = 1` and the admin calls `notifyRewardAmount(R)`:

```
rewardRate = R / duration

After full duration:
rewardPerTokenStored += rewardRate * duration * 1e18 / 1
                      = R * 1e18

attacker.earned() = 1 * (R * 1e18 - 0) / 1e18 = R   ← all rewards
```

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The attacker claims the entire reward pool (`R` tokens) deposited by the admin for the distribution period. Legitimate stakers who join after `notifyRewardAmount` is called receive rewards only from the moment they stake, diluting the attacker's share going forward, but the rewards accrued during the window `[notifyRewardAmount call → first legitimate stake]` are permanently captured by the attacker's 1-wei position.

If no legitimate users stake during the full period (e.g., the contract is newly deployed and the admin seeds rewards before users arrive), the attacker captures **100% of the reward distribution**.

---

### Likelihood Explanation

**Medium.**

- No front-running is required. The attacker simply needs to call `stake(1)` before any legitimate user, which is trivially achievable on a freshly deployed or newly reset contract.
- The protocol's own comment explicitly suggests that 1-wei staking is an acceptable operational pattern, making it likely that no on-chain or off-chain guard prevents this.
- The admin's `notifyRewardAmount` call is a routine operational action; the admin has no on-chain signal distinguishing a legitimate 1-wei "dust" stake from an attacker's position.
- The cost to the attacker is 1 wei of KERNEL plus gas.

---

### Recommendation

1. **Enforce a minimum stake** in `stake()` (e.g., `require(_amount >= MIN_STAKE)`), preventing dust positions from capturing disproportionate rewards.
2. **Alternatively**, initialize `totalKernelStaked` with a protocol-owned seed amount (analogous to Uniswap v2's dead-share approach) so that 1-wei positions are always negligible relative to the denominator.
3. **At minimum**, add an on-chain check in `notifyRewardAmount` that `totalKernelStaked` exceeds a meaningful threshold before allowing reward distribution to begin.

---

### Proof of Concept

**Setup:** `duration = 30 days`, reward token `R = 1,000,000e18`.

1. **Attacker** calls `stake(1)` → `totalKernelStaked = 1`, `balanceOf[attacker] = 1`.
2. **Admin** calls `notifyRewardAmount(1_000_000e18)`:
   - `rewardRate = 1_000_000e18 / (30 days) ≈ 3.858e17` tokens/second.
3. **30 days pass.** No legitimate user stakes (or they stake much later).
4. `rewardPerToken()` returns:
   ```
   0 + (3.858e17 * 2_592_000 * 1e18) / 1 = 1_000_000e18
   ```
5. **Attacker** calls `getReward()`:
   ```
   earned(attacker) = 1 * (1_000_000e18 - 0) / 1e18 = 1_000_000e18
   ```
   → Attacker receives the entire `1,000,000` reward tokens.
6. **Legitimate users** who staked after step 1 receive `0` rewards for this period. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L14-22)
```text
/**
 * @title Kernel Staking Rewards Contract
 * @dev Implements a basic staking mechanism with rewards
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-288)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-423)
```text
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-592)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();

        // Transfer reward tokens into the contract
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;

        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }

        if (rewardRate == 0) revert RewardRateZero();

        finishAt = block.timestamp + duration;
        updatedAt = block.timestamp;

        emit NotifyRewardAmount(receivedAmount, finishAt);
    }
```
