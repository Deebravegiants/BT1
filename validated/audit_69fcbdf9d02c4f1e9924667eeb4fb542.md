Audit Report

## Title
Reward Tokens Permanently Locked When `totalKernelStaked` Drops to Zero Mid-Period - (`contracts/KERNEL/KernelDepositPool.sol`)

## Summary

`KernelDepositPool` uses a Synthetix-style reward accounting model where `initiateWithdrawal()` immediately decrements `totalKernelStaked` before the withdrawal delay elapses. If this causes `totalKernelStaked` to reach zero during an active reward period, the `updateReward` modifier unconditionally advances `updatedAt` while `rewardPerToken()` short-circuits and returns the stored value unchanged. All reward tokens emitted during the zero-staking window are permanently locked in the contract with no recovery path.

## Finding Description

`initiateWithdrawal()` immediately decrements `totalKernelStaked` at line 326 before any withdrawal delay elapses:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L325-326
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
```

This allows `totalKernelStaked` to reach zero while `rewardRate > 0` and `block.timestamp < finishAt`.

The `rewardPerToken()` function short-circuits when `totalKernelStaked == 0`, returning `rewardPerTokenStored` unchanged (L409-410):

```solidity
if (totalKernelStaked == 0) {
    return rewardPerTokenStored;
}
```

However, the `updateReward` modifier unconditionally advances `updatedAt` to `lastTimeRewardApplicable()` regardless of whether `totalKernelStaked` is zero (L233-234):

```solidity
rewardPerTokenStored = rewardPerToken();
updatedAt = lastTimeRewardApplicable();
```

The combination is fatal: when the next user interacts with the contract after a zero-staking window, `updateReward` runs, `rewardPerTokenStored` is not increased (because `rewardPerToken()` returns the stored value), but `updatedAt` is pushed forward to the current time. The entire time gap during which `totalKernelStaked == 0` is silently consumed. Rewards emitted during that window are never credited to any user and can never be claimed.

The `notifyRewardAmount()` guard at L570 (`if (totalKernelStaked == 0) revert NoStakedTokens()`) only prevents starting a new reward period with zero stakers. It does not prevent all stakers from exiting mid-period, which is the actual trigger. There is no admin sweep function among `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser`.

Notably, the contract's own NatSpec comment at lines 18-22 explicitly acknowledges this behavior:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract. In this deployment, we're avoiding this issue by ensuring there are always some tokens staked… for the entire duration of the reward period."*

This acknowledgment confirms the behavior is real, but the stated mitigation is purely operational and is not enforced by any on-chain mechanism. Any staker can call `initiateWithdrawal()` at any time.

## Impact Explanation

Reward tokens (`rewardsToken`) accumulate in the contract balance but are never credited to `rewardPerTokenStored` during the zero-staking window. The shortfall between the contract's `rewardsToken` balance and the sum of all claimable `rewards[user]` values grows monotonically and is irrecoverable. There is no admin function to sweep or redistribute the stranded tokens. This constitutes **permanent freezing of unclaimed yield** (Medium severity per the allowed impact scope).

## Likelihood Explanation

Any single staker holding 100% of `totalKernelStaked` can trigger this unilaterally by calling `initiateWithdrawal()` during an active reward period. The `withdrawalDelay` can be up to 30 days (`MAX_WITHDRAWAL_DELAY`), meaning `totalKernelStaked` can remain zero for up to 30 days while `rewardRate > 0`. The `KernelMerkleDistributor` uses `stakeFor` to auto-stake claimed KERNEL, meaning staker composition can shift rapidly after a distribution event, making a temporary single-staker scenario realistic. No privileged access is required; the trigger is a standard user withdrawal.

## Recommendation

Do not advance `updatedAt` when `totalKernelStaked == 0`, so that rewards emitted during the zero-staking window are preserved for future stakers:

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

Alternatively, add an admin-only `recoverStrandedRewards()` function that transfers the difference between the contract's `rewardsToken` balance and the sum of all pending rewards to a treasury address after `finishAt`.

## Proof of Concept

```
Setup:
  - duration = 100s, rewardRate = 10 KERNEL/s (1000 KERNEL total)
  - Alice stakes 100 KERNEL; admin calls notifyRewardAmount(1000)

t=0:   notifyRewardAmount called; finishAt = t+100; rewardRate = 10/s
t=10:  Alice calls initiateWithdrawal(100)
         → updateReward(Alice): rewardPerTokenStored += 10*10/100 = 1.0; updatedAt = t10
         → totalKernelStaked = 0
         → Alice's pending reward = 100 * 1.0 = 100 KERNEL ✓

t=10→t=60: totalKernelStaked == 0; 500 KERNEL emitted but credited to nobody
         → rewardPerTokenStored stays at 1.0; updatedAt stays at t10

t=60:  Bob stakes 100 KERNEL
         → updateReward(Bob): rewardPerToken() returns 1.0 (zero-staking branch)
         → updatedAt advances to t60 ← 50-second gap silently consumed
         → totalKernelStaked = 100

t=100: Bob calls getReward()
         → rewardPerToken() = 1.0 + 10*(100-60)/100 = 5.0
         → Bob earns 500 KERNEL

Result:
  Alice claims 100 KERNEL
  Bob claims   500 KERNEL
  Total claimed: 600 KERNEL
  Contract holds: 400 KERNEL permanently locked
```

Foundry test plan: deploy `KernelDepositPool`, stake as Alice, call `notifyRewardAmount`, `vm.warp` to t=10, call `initiateWithdrawal`, `vm.warp` to t=60, stake as Bob, `vm.warp` to t=100, call `getReward` for both users, assert `rewardsToken.balanceOf(address(pool)) == 400e18` with no callable function able to reduce it.