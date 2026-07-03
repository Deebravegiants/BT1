### Title
Reward Tokens Permanently Frozen When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
In `KernelDepositPool.sol`, when all stakers call `initiateWithdrawal()` during an active reward period, `totalKernelStaked` drops to zero. The `rewardPerToken()` function returns `rewardPerTokenStored` unchanged (no reward advancement), but the `updateReward` modifier still advances `updatedAt` to `lastTimeRewardApplicable()`. Any reward tokens that should have been distributed during the zero-staked window are permanently frozen in the contract and can never be claimed.

### Finding Description
The `rewardPerToken()` function has a guard for the zero-supply case:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:408-413
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;   // ← no advancement
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
```

However, the `updateReward` modifier unconditionally advances `updatedAt`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:232-242
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();       // frozen when totalKernelStaked == 0
    updatedAt = lastTimeRewardApplicable();        // ← always advances
    ...
}
```

`initiateWithdrawal()` immediately decrements `totalKernelStaked` in its function body (after the modifier runs):

```solidity
// contracts/KERNEL/KernelDepositPool.sol:320-338
function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    ...
    balanceOf[msg.sender] -= _amount;
    totalKernelStaked -= _amount;   // ← can reach 0
    ...
}
```

When the last staker calls `initiateWithdrawal()`:
1. `updateReward` runs first (while `totalKernelStaked` is still > 0), correctly snapshotting rewards up to that moment and setting `updatedAt = block.timestamp`.
2. `totalKernelStaked` is then set to 0.
3. For all subsequent calls (e.g., a new staker calling `stake()`), `updateReward` runs with `totalKernelStaked == 0`, so `rewardPerTokenStored` stays frozen while `updatedAt` advances past the entire zero-staked window.
4. When the new staker's `stake()` body executes and `totalKernelStaked` becomes > 0, the time gap has already been consumed by `updatedAt` with no reward credit.

The contract's own NatSpec acknowledges this at lines 18–22 but relies entirely on an off-chain operational assumption with no on-chain enforcement:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:18-22
* @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
*      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
*      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
*      as well as for the entire duration of the reward period.
```

### Impact Explanation
Reward tokens (`rewardsToken`) corresponding to the zero-staked window are permanently locked in `KernelDepositPool`. They cannot be claimed by any user and cannot be recovered by the admin (there is no rescue/sweep function for `rewardsToken`). This constitutes **permanent freezing of unclaimed yield** (Medium).

### Likelihood Explanation
Any staker can call `initiateWithdrawal()` at any time — it is an unprivileged, externally reachable function. If the total staked supply is small (e.g., one or a few stakers), a single user withdrawing their full balance suffices to trigger the condition. The protocol's only mitigation is an off-chain operational promise, which provides no on-chain guarantee.

### Recommendation
When `totalKernelStaked == 0`, do **not** advance `updatedAt`. Change the `updateReward` modifier so that `updatedAt` is only updated when `totalKernelStaked > 0`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    if (totalKernelStaked > 0) {
        updatedAt = lastTimeRewardApplicable();
    }
    if (_account != address(0)) {
        rewards[_account] = earned(_account);
        userRewardPerTokenPaid[_account] = rewardPerTokenStored;
    }
    _;
}
```

This ensures that the time elapsed while no tokens are staked is not silently consumed, so rewards for that window remain distributable when stakers return.

### Proof of Concept
1. Admin calls `notifyRewardAmount(1000e18)` with Alice staked (passes `NoStakedTokens` guard). `rewardRate = 1000e18 / duration`, `finishAt = block.timestamp + duration`, `updatedAt = block.timestamp`.
2. Alice calls `initiateWithdrawal(aliceBalance)`. `updateReward` runs (correctly snapshots her rewards), then `totalKernelStaked = 0`.
3. 50% of the reward duration elapses with no stakers. During this window, any call to `updateReward` (e.g., a `getReward()` call by Alice) advances `updatedAt` to `lastTimeRewardApplicable()` while `rewardPerTokenStored` stays frozen.
4. Bob calls `stake(1e18)`. `updateReward` runs: `rewardPerToken()` returns `rewardPerTokenStored` (unchanged, since `totalKernelStaked` is still 0 at modifier time), and `updatedAt` is advanced to `block.timestamp`.
5. Bob's `stake()` body sets `totalKernelStaked = 1e18`.
6. For the remaining 50% of the period, Bob earns rewards correctly. But the 50% of reward tokens corresponding to the zero-staked window (~500e18 tokens) are permanently frozen in the contract — no user can ever claim them, and no admin function can recover them. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L14-23)
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
 */
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-338)
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
