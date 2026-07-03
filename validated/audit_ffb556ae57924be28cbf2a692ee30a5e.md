### Title
Rewards Permanently Lost When `totalKernelStaked` Drops to Zero During an Active Reward Period - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` uses a Synthetix-style staking reward model. When `totalKernelStaked` drops to zero during an active reward window, `rewardPerToken()` stops accumulating and the rewards allocated to that elapsed time are permanently locked in the contract with no mechanism to recover them.

---

### Finding Description

The `rewardPerToken()` function returns `rewardPerTokenStored` unchanged whenever `totalKernelStaked == 0`:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [1](#0-0) 

This means any time elapsed with zero stakers is silently skipped — the `rewardRate * elapsed` tokens for that window are never attributed to anyone and remain permanently stuck in the contract.

The `initiateWithdrawal` function immediately decrements `totalKernelStaked` at initiation time (not at claim time):

```solidity
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
``` [2](#0-1) 

So if all stakers call `initiateWithdrawal` during an active reward period, `totalKernelStaked` immediately hits zero, and all rewards for the remainder of the period (`rewardRate * remainingTime`) are permanently frozen in the contract.

The contract itself acknowledges this in its NatSpec:

> "If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract." [3](#0-2) 

The only code-level protection is the guard in `notifyRewardAmount` that prevents *starting* a reward period with zero stakers:

```solidity
if (totalKernelStaked == 0) revert NoStakedTokens();
``` [4](#0-3) 

But there is **no protection** against `totalKernelStaked` dropping to zero *after* a reward period has started. The operational mitigation mentioned in the comment ("ensuring there are always some tokens staked … for the entire duration of the reward period") is not enforced at the contract level.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Rewards already transferred into the contract via `notifyRewardAmount` and allocated via `rewardRate` for the remaining period become permanently unclaimable. No admin function, recovery path, or sweep mechanism exists to retrieve them. The `rewardsToken` balance in the contract exceeds what can ever be claimed.

---

### Likelihood Explanation

Users have an unrestricted right to call `initiateWithdrawal` at any time for any amount of their staked balance. There is no lock-up preventing full exit during an active reward period. A coordinated or organic mass exit (e.g., loss of confidence in the protocol, a better yield opportunity elsewhere, or a market event) can drive `totalKernelStaked` to zero mid-period. The `MAX_WITHDRAWAL_DELAY` of 30 days only delays the token transfer — `totalKernelStaked` is decremented immediately at initiation, so the reward loss occurs the moment the last staker calls `initiateWithdrawal`. [5](#0-4) 

---

### Recommendation

Add a check in `initiateWithdrawal` (or a separate recovery function) to handle the case where `totalKernelStaked` would drop to zero during an active reward period. Options include:

1. **Checkpoint and pause the reward rate** when `totalKernelStaked` reaches zero, storing the unallocated rewards so they can be rolled into the next period via `notifyRewardAmount`.
2. **Revert** if `totalKernelStaked - _amount == 0` and `block.timestamp < finishAt`, forcing the last staker to wait until the reward period ends before fully exiting.
3. **Carry forward** unallocated rewards: when `notifyRewardAmount` is called again, compute the stuck amount and add it to the new period's `receivedAmount`.

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` with `duration = 7 days`. `rewardRate = 1_000e18 / 604800 ≈ 1653 tokens/sec`. `finishAt = now + 7 days`.
2. At `now + 1 day`, all stakers call `initiateWithdrawal(fullBalance)`. `totalKernelStaked` becomes `0`.
3. For the remaining 6 days, `rewardPerToken()` returns `rewardPerTokenStored` unchanged — no rewards accumulate.
4. Rewards lost ≈ `1653 * 6 * 86400 ≈ 857,145,600` token-wei (≈ 857 tokens), permanently stuck in the contract.
5. No function exists to recover these tokens. [1](#0-0) [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-337)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

        // Create a withdrawal record
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
        userWithdrawalIds[msg.sender].push(withdrawalId);

        emit WithdrawalInitiated(msg.sender, _amount, withdrawalId, unlockTime);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-591)
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
```
