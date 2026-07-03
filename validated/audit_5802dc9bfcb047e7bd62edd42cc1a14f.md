Audit Report

## Title
Permanent Freezing of Unclaimed Yield When Last Staker Exits During Active Reward Period - (File: `contracts/KERNEL/KernelDepositPool.sol`)

## Summary
When the last staker calls `initiateWithdrawal` for their full balance during an active reward period, `totalKernelStaked` drops to zero. The `rewardPerToken()` accumulator permanently freezes at `rewardPerTokenStored`, and all reward tokens allocated for the remaining period (`rewardRate * (finishAt - block.timestamp)`) become irrecoverably locked. No admin sweep, recovery, or rescue function exists in the contract.

## Finding Description

**Step 1 — `updateReward` snapshots state before balance reduction.**

`initiateWithdrawal` applies `updateReward(msg.sender)` as a modifier before its body executes. [1](#0-0)  This correctly credits `earned(msg.sender)` and snapshots `rewardPerTokenStored` while `totalKernelStaked` is still non-zero. [2](#0-1) 

**Step 2 — `totalKernelStaked` is reduced to zero.**

After the modifier, the function body decrements both `balanceOf` and `totalKernelStaked`. [3](#0-2)  If this was the last staker, `totalKernelStaked == 0` from this point forward.

**Step 3 — `rewardPerToken()` freezes permanently.**

With `totalKernelStaked == 0`, every subsequent call to `rewardPerToken()` returns the frozen `rewardPerTokenStored`. [4](#0-3)  The `rewardRate` is still non-zero and `finishAt` is still in the future, but the accumulator never advances. Critically, `updatedAt` is advanced to `lastTimeRewardApplicable()` on every subsequent `updateReward` call (e.g., when a new staker enters), so the elapsed time during the zero-staked window is silently discarded — those rewards are permanently unaccounted for.

**Step 4 — Admin cannot restart distribution while staked supply is zero.**

`notifyRewardAmount` reverts with `NoStakedTokens` when `totalKernelStaked == 0`. [5](#0-4)  The admin cannot even reset the reward period to recover stranded tokens.

**Step 5 — No recovery path exists.**

The admin function section contains only `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser`. [6](#0-5)  There is no `recoverERC20`, `sweepStrandedRewards`, or `emergencyWithdraw`.

**Step 6 — The contract acknowledges the risk but relies solely on off-chain controls.**

The NatSpec explicitly documents this failure mode and states it is mitigated by "ensuring there are always some tokens staked." [7](#0-6)  This is a purely operational promise with zero on-chain enforcement; any staker can exit at any time.

## Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

The exiting staker correctly receives their principal (via `claimWithdrawal`) and their accrued rewards up to the withdrawal moment (via `getReward`). However, the reward tokens allocated for the remainder of the active period — `rewardRate * (finishAt - block.timestamp)` — are permanently locked in the contract with no mechanism to recover them. This exactly matches the allowed impact class: *Medium. Permanent freezing of unclaimed yield.*

## Likelihood Explanation

- Any unprivileged staker can trigger this unilaterally by calling `initiateWithdrawal` for their full balance; no special role, collusion, or privileged access is required.
- The only mitigation is an off-chain operational promise, which is unenforceable on-chain.
- The scenario is reachable accidentally (a staker simply wanting to exit) or deliberately (a griefing staker).
- Likelihood is **Medium**: requires the last staker to exit mid-period, a plausible real-world scenario especially in low-participation pools.

## Recommendation

1. Add an admin `recoverStrandedRewards` function callable only after `finishAt`, restricted to `DEFAULT_ADMIN_ROLE`, that transfers the surplus reward balance (i.e., `rewardsToken.balanceOf(address(this)) - totalPendingRewards`) back to the admin.
2. Alternatively, enforce on-chain that `initiateWithdrawal` cannot reduce `totalKernelStaked` to zero while `block.timestamp < finishAt`, reverting with a descriptive error.
3. At minimum, when `totalKernelStaked` drops to zero mid-period, snapshot the remaining undistributed rewards and allow the admin to reclaim them after `finishAt`.

## Proof of Concept

```solidity
// 1. Admin sets duration and notifies reward amount (1000e18 tokens, 10-day period)
pool.setRewardsDuration(10 days);
rewardToken.approve(address(pool), 1000e18);
pool.notifyRewardAmount(1000e18);
// rewardRate = 1000e18 / 10 days

// 2. Warp halfway through the period
vm.warp(block.timestamp + 5 days);

// 3. Last staker initiates withdrawal for full balance
// updateReward runs first: correctly credits ~500e18 earned rewards
pool.initiateWithdrawal(stakerBalance);
// totalKernelStaked is now 0

// 4. Staker claims their correctly-accrued rewards (works fine)
pool.getReward();

// 5. Warp to end of period
vm.warp(finishAt);

// 6. Assert: ~500e18 reward tokens are permanently locked
// rewardPerToken() returns frozen rewardPerTokenStored forever
// No staker can claim them; no admin can recover them
assertGt(rewardToken.balanceOf(address(pool)), 0);

// 7. Confirm admin cannot call notifyRewardAmount to reset (reverts NoStakedTokens)
vm.expectRevert(KernelDepositPool.NoStakedTokens.selector);
pool.notifyRewardAmount(1e18);
```

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L17-23)
```text
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
 */
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-241)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-320)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L325-326)
```text
        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-411)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L544-621)
```text
    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Sets the duration for rewards distribution
     * @param _duration The duration in seconds
     */
    function setRewardsDuration(uint256 _duration) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (finishAt >= block.timestamp) revert RewardDurationNotFinished();
        if (_duration == 0) revert InvalidDuration();
        duration = _duration;
        emit RewardsDurationUpdated(_duration);
    }

    /**
     * @notice Notifies the contract about a new reward amount
     * @dev Uses a transfer-in pattern to determine the exact reward amount received.
     *      Also, to avoid undistributed rewards when no one is staked, this function reverts if totalKernelStaked is
     *      zero.
     * @param _amount The amount of reward tokens to add
     */
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

    /**
     * @notice Updates the withdrawal delay
     * @param _withdrawalDelay The new withdrawal delay
     */
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
    }

    /**
     * @notice Updates the maximum number of withdrawals per user
     * @param _maxNumberOfWithdrawalsPerUser The new maximum number of withdrawals per user
     */
    function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
            revert InvalidMaxNumberOfWithdrawalsPerUser();
        }

        maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
        emit MaxNumberOfWithdrawalsPerUserUpdated(_maxNumberOfWithdrawalsPerUser);
    }
}
```
