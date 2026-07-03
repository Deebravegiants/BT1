Audit Report

## Title
Reward Tokens Permanently Locked When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary

`KernelDepositPool.sol` implements a Synthetix-style staking rewards contract where `rewardPerToken()` halts accumulation when `totalKernelStaked == 0`. If all stakers legitimately withdraw during an active reward period, the `rewardRate` and `finishAt` remain set but no user ever accrues the remaining rewards. The contract contains no recovery or sweep function for `rewardsToken`, making those tokens permanently inaccessible.

## Finding Description

`rewardPerToken()` contains a zero-stake guard that freezes `rewardPerTokenStored` when `totalKernelStaked == 0`:

```solidity
// L408-414
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [1](#0-0) 

`initiateWithdrawal` immediately decrements `totalKernelStaked` at the time of initiation, not at claim time:

```solidity
// L325-326
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
``` [2](#0-1) 

Once `totalKernelStaked` reaches zero, `rewardPerTokenStored` is frozen for the remainder of the period. The only outbound path for `rewardsToken` is `getReward()`, which only transfers `rewards[msg.sender]` — tokens never accrued to any user cannot be claimed by anyone: [3](#0-2) 

The `notifyRewardAmount` guard only prevents *starting* a new period with zero stake; it does not prevent stake from draining to zero mid-period: [4](#0-3) 

The contract has no `recoverERC20`, no `sweep`, and no admin function capable of extracting stranded `rewardsToken`. The entire admin function set consists of `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser` — none of which can move `rewardsToken` out of the contract except through the normal accrual path. [5](#0-4) 

The contract's own NatSpec acknowledges this limitation and relies entirely on an off-chain operational promise with no on-chain enforcement: [6](#0-5) 

## Impact Explanation

**Medium — Permanent freezing of unclaimed yield.** Reward tokens deposited via `notifyRewardAmount` for a given period are permanently locked in the contract if `totalKernelStaked` reaches zero before `finishAt`. The tokens are not transferred to an attacker; they are irreversibly inaccessible to both users and the protocol. This matches the allowed impact "Medium. Permanent freezing of unclaimed yield."

## Likelihood Explanation

**Medium.** Any staker can independently and legitimately call `initiateWithdrawal` followed by `claimWithdrawal` at any time — no coordination, no malicious intent, and no privileged access is required. The `withdrawalDelay` introduces a time buffer but does not prevent the condition. Rational stakers may simply exit the pool for any reason (e.g., better yield elsewhere, risk aversion), and the last staker to exit causes the lock without any awareness of doing so.

## Recommendation

1. **Add a token recovery function** restricted to `DEFAULT_ADMIN_ROLE`, callable only after `finishAt` has passed, that sweeps any `rewardsToken` balance exceeding the sum of all outstanding `rewards[]` entries back to the admin or treasury.
2. **Track unallocated rewards explicitly**: maintain an `unallocatedRewards` counter that accumulates `rewardRate * elapsed` whenever `totalKernelStaked == 0`, and allow the admin to redistribute or recover that amount after the period ends.
3. **Alternatively**, enforce the invariant on-chain by preventing `initiateWithdrawal` from reducing `totalKernelStaked` to zero while `block.timestamp < finishAt`, or by storing the "missed" window for redistribution when staking resumes.

## Proof of Concept

```
Setup:
  - duration = 100 seconds
  - Admin calls notifyRewardAmount(1000 tokens) with Alice staked
    → rewardRate = 10 tokens/sec, finishAt = T+100

T=0:   Alice stakes 1000 KERNEL (totalKernelStaked = 1000)
T=10:  Alice calls initiateWithdrawal(1000)
         → updateReward checkpoints rewards[Alice] = 10 * 10 = 100 tokens
         → totalKernelStaked = 0 immediately
T=10+withdrawalDelay: Alice calls claimWithdrawal()
         → totalKernelStaked remains 0

T=10 to T=100 (90 seconds):
  rewardPerToken() returns frozen rewardPerTokenStored
  rewardRate * 90 = 900 tokens are never accrued to anyone

T=100: finishAt passes.
  Alice calls getReward() → receives 100 tokens (her accrued amount)
  Remaining 900 tokens: no function can extract them.
  rewardsToken.balanceOf(address(KernelDepositPool)) = 900 (permanently locked)
```

Foundry invariant test plan: deploy `KernelDepositPool`, stake with a single actor, start a reward period via `notifyRewardAmount`, have the actor call `initiateWithdrawal` for their full balance, warp past `withdrawalDelay`, call `claimWithdrawal`, warp to `finishAt + 1`, call `getReward`, then assert `rewardsToken.balanceOf(address(pool)) > 0` and that no callable function reduces it to zero.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L325-326)
```text
        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;
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
