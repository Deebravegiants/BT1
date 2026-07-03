Audit Report

## Title
Rewards permanently lost when `totalKernelStaked` drops to zero mid-period via `initiateWithdrawal` - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary

`KernelDepositPool` uses a Synthetix-style reward accounting model where `rewardPerTokenStored` does not increment when `totalKernelStaked == 0`, but the `updatedAt` timestamp still unconditionally advances in the `updateReward` modifier. While `notifyRewardAmount` prevents starting a reward period with zero stakers, there is no on-chain guard preventing `totalKernelStaked` from reaching zero mid-period via `initiateWithdrawal`. Any rewards accrued during the zero-supply window are permanently locked in the contract with no recovery mechanism.

## Finding Description

The `updateReward` modifier at lines 232–242 unconditionally sets `updatedAt = lastTimeRewardApplicable()` regardless of whether `totalKernelStaked` is zero:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();   // always advances
    ...
}
``` [1](#0-0) 

`rewardPerToken()` at lines 408–414 returns `rewardPerTokenStored` unchanged when `totalKernelStaked == 0`, meaning the time interval is consumed without distributing any rewards:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;   // no increment
    }
    ...
}
``` [2](#0-1) 

`initiateWithdrawal` at lines 325–326 immediately decrements `totalKernelStaked` with no floor check:

```solidity
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
``` [3](#0-2) 

The `notifyRewardAmount` guard at lines 569–570 only prevents starting a new period with zero stakers; it does not prevent the supply from reaching zero during an active period: [4](#0-3) 

The contract's own NatSpec at lines 17–22 explicitly acknowledges this gap and relies entirely on an off-chain operational guarantee ("ensuring there are always some tokens staked … for the entire duration of the reward period"), which is not enforced on-chain: [5](#0-4) 

There is no admin sweep, recovery, or redistribution function anywhere in the contract.

**Exploit path:**
1. Admin calls `notifyRewardAmount` with stakers present → `rewardRate` and `finishAt` are set.
2. All stakers call `initiateWithdrawal` → `totalKernelStaked` drops to zero; `updateReward` correctly snapshots accrued rewards up to this point and sets `updatedAt = now`.
3. Time passes with `totalKernelStaked == 0`. Every call that touches `updateReward` (or any view of `rewardPerToken`) returns the same `rewardPerTokenStored` but `updatedAt` will be advanced to the current time on the next interaction.
4. A new staker calls `stake` → `updateReward` runs: `rewardPerToken()` still returns the same `rewardPerTokenStored` (supply was 0 throughout), and `updatedAt` is now advanced past the gap. The rewards for the entire zero-supply window (`rewardRate × duration_of_zero_supply`) are permanently unclaimable.

## Impact Explanation

The impact is **permanent freezing of unclaimed yield** (Medium severity per the allowed scope). Reward tokens sent to the contract via `notifyRewardAmount` that fall within a zero-supply interval are permanently unclaimable. The amount lost equals `rewardRate × duration_of_zero_supply_window`. There is no admin recovery function, no sweep mechanism, and no way to redistribute the lost rewards.

## Likelihood Explanation

The scenario is reachable by any unprivileged staker calling the public `initiateWithdrawal` function. It is realistic when: (a) a single large staker (e.g., a protocol-controlled address with `STAKE_FOR_ROLE`) holds all staked tokens and withdraws; (b) a coordinated exit occurs during a depeg event or protocol migration; or (c) stakers naturally exit before a long reward period ends. The withdrawal delay only delays token recovery — `totalKernelStaked` drops to zero immediately at `initiateWithdrawal` call time, not at `claimWithdrawal` time. [6](#0-5) 

## Recommendation

Skip the `updatedAt` advancement inside `updateReward` when `totalKernelStaked == 0`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    if (totalKernelStaked != 0) {
        updatedAt = lastTimeRewardApplicable();
    }
    if (_account != address(0)) {
        rewards[_account] = earned(_account);
        userRewardPerTokenPaid[_account] = rewardPerTokenStored;
    }
    _;
}
```

This ensures the zero-supply interval is not consumed, and rewards resume correctly once stakers return.

## Proof of Concept

1. Deploy `KernelDepositPool`; admin sets `duration = 30 days`.
2. Alice stakes `100e18` KERNEL tokens. Admin calls `notifyRewardAmount(1_000e18)`. `rewardRate ≈ 385e12/s`, `finishAt = now + 30 days`.
3. After 10 days, Alice calls `initiateWithdrawal(100e18)`. `updateReward` runs: `rewardPerTokenStored` correctly captures 10 days of rewards; `updatedAt = now`; `totalKernelStaked = 0`.
4. 10 more days pass with no stakers. No state changes occur.
5. Bob calls `stake(100e18)`. `updateReward` runs: `rewardPerToken()` returns the same `rewardPerTokenStored` (supply was 0), and `updatedAt` advances to `now`. The 10-day gap (`≈ 385e12 × 864_000 ≈ 332e18` reward tokens) is permanently locked in the contract.
6. Verify: `rewardsToken.balanceOf(address(pool))` exceeds the sum of all claimable `earned()` values across all users by `≈ 332e18`.

**Foundry invariant test plan:** Write an invariant asserting `rewardsToken.balanceOf(address(pool)) == sum(earned(user) for all users) + undistributed_future_rewards`. Fuzz `initiateWithdrawal` calls that drive `totalKernelStaked` to zero mid-period and verify the invariant breaks under the current code but holds with the recommended fix.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L17-22)
```text
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L569-570)
```text
        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
