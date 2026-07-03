Audit Report

## Title
Zero-Staked Window Permanently Locks Reward Tokens During Active Distribution Period — (`contracts/KERNEL/KernelDepositPool.sol`)

## Summary
When `totalKernelStaked` drops to zero mid-period, `rewardPerToken()` freezes at `rewardPerTokenStored` while `updateReward` continues advancing `updatedAt`. Any `rewardRate`-denominated tokens emitted during this window are permanently unclaimable. The contract's own NatSpec acknowledges this behavior but relies on an off-chain, unenforced operational assumption to prevent it.

## Finding Description

**Root cause — `rewardPerToken()` freezes when `totalKernelStaked == 0`:** [1](#0-0) 

When `totalKernelStaked == 0`, the function returns the frozen `rewardPerTokenStored` without accumulating any new rewards for the elapsed time.

**`updateReward` advances `updatedAt` regardless of staked supply:** [2](#0-1) 

`updatedAt = lastTimeRewardApplicable()` executes unconditionally. When `totalKernelStaked == 0`, `rewardPerTokenStored` is written back as the frozen value, but `updatedAt` jumps forward — permanently discarding the time gap from the accumulator.

**`initiateWithdrawal` has no guard against zeroing `totalKernelStaked` mid-period:** [3](#0-2) 

Any staker holding 100% of `totalKernelStaked` can call `initiateWithdrawal(fullBalance)`, setting `totalKernelStaked = 0` during an active reward period. No on-chain check prevents this.

**The only zero-staked guard is in `notifyRewardAmount`, which only prevents starting a period with zero stakers:** [4](#0-3) 

This guard does not protect against `totalKernelStaked` reaching zero mid-period.

**The contract's own NatSpec acknowledges the issue but relies on an unenforced off-chain assumption:** [5](#0-4) 

**Exploit flow:**

| Step | Action | State |
|------|--------|-------|
| T | Last staker calls `initiateWithdrawal(fullBalance)` | `totalKernelStaked = 0`, `updatedAt = T`, `rewardPerTokenStored` frozen |
| T → T+Δ | No staker present; `rewardRate` tokens continue to emit | `rewardPerToken()` returns frozen value; gap = `rewardRate * Δ` tokens |
| T+Δ | New staker calls `stake(amount)` | `updateReward` runs with `totalKernelStaked == 0`; `rewardPerTokenStored` stays frozen; `updatedAt` jumps to T+Δ |
| T+Δ+ | `totalKernelStaked` non-zero | Future accumulation starts from T+Δ; T→T+Δ gap skipped entirely |

The `rewardRate * Δ` tokens are in the contract's balance (deposited via `notifyRewardAmount`) but can never be claimed by any past, present, or future staker.

## Impact Explanation
Reward tokens emitted during the zero-staked window are permanently locked in the contract. No staker can ever claim them. This constitutes **permanent freezing of unclaimed yield** — a Medium severity impact per the allowed scope. No principal is lost; only yield is affected.

## Likelihood Explanation
- Requires only a single staker holding 100% of `totalKernelStaked` to call `initiateWithdrawal`.
- No admin involvement, no front-running, no external dependency.
- Fully permissionless and triggerable by any ordinary user through a standard withdrawal action.
- The off-chain mitigation ("ensure tokens are always staked") cannot be enforced if the last staker simply decides to exit.

## Recommendation
**Option A (preferred):** In `initiateWithdrawal`, revert if the withdrawal would zero `totalKernelStaked` during an active reward period:
```solidity
if (block.timestamp < finishAt && totalKernelStaked - _amount == 0) revert NoStakedTokens();
```

**Option B:** Decouple `updatedAt` advancement from the zero-staked check — only advance `updatedAt` when `totalKernelStaked > 0`, so the gap is not silently discarded.

**Option C (minimal):** Add an admin-callable `recoverUnallocatedRewards()` to sweep locked gap rewards back to the treasury, preventing permanent lock-up.

## Proof of Concept
```solidity
function test_zeroStakedWindowLocksRewards() public {
    // Setup: single staker, active reward period
    pool.stake(1000e18);
    pool.notifyRewardAmount(rewardRate * duration); // totalKernelStaked > 0, passes guard

    uint256 T = block.timestamp;

    // Last staker exits — totalKernelStaked = 0
    pool.initiateWithdrawal(1000e18);

    // 100 seconds pass with no stakers; rewardRate tokens emitted but not accumulated
    vm.warp(T + 100);

    // New staker joins — updateReward sees totalKernelStaked==0, freezes rPTS, advances updatedAt to T+100
    pool.stake(1000e18);

    // Warp to end of period and claim
    vm.warp(finishAt);
    pool.getReward();

    uint256 totalClaimed = rewardsToken.balanceOf(address(this));
    uint256 gap = rewardRate * 100;

    // Gap rewards are permanently locked in the contract
    assertEq(rewardsToken.balanceOf(address(pool)), gap);
}
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-326)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L569-570)
```text
        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
