### Title
`updatedAt` Advances During Zero-Supply Periods, Permanently Losing Rewards - (`contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

The `updateReward` modifier in `KernelDepositPool` unconditionally advances `updatedAt` to `lastTimeRewardApplicable()` even when `totalKernelStaked == 0`. Because `rewardPerToken()` freezes `rewardPerTokenStored` during zero-supply periods, any rewards accrued while no tokens are staked are silently discarded and permanently unclaimable.

---

### Finding Description

The `updateReward` modifier always executes:

```solidity
rewardPerTokenStored = rewardPerToken();
updatedAt = lastTimeRewardApplicable();   // unconditional
``` [1](#0-0) 

Meanwhile, `rewardPerToken()` short-circuits when `totalKernelStaked == 0`, returning the stored value without advancing the accumulator:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;   // no time-weighted accrual
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [2](#0-1) 

When `totalKernelStaked` drops to zero mid-period (e.g., after `initiateWithdrawal`), the next call to `updateReward` — triggered by the next staker — will:

1. Call `rewardPerToken()` → returns the frozen `rewardPerTokenStored` (no new accrual).
2. Set `updatedAt = lastTimeRewardApplicable()` → jumps past the entire zero-supply gap.

The rewards that should have accrued during the zero-supply window are now permanently unaccountable: `updatedAt` has moved forward, so the future `rewardPerToken()` calculation using `(lastTimeRewardApplicable() - updatedAt)` will never include that gap again.

The `notifyRewardAmount` guard (`if (totalKernelStaked == 0) revert NoStakedTokens()`) only prevents starting a fresh reward period with no stakers. It does not protect against a mid-period zero-supply window caused by a full withdrawal. [3](#0-2) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Rewards emitted during any period where `totalKernelStaked == 0` are permanently stranded in the contract. No user can ever claim them. The reward token balance of the contract grows beyond what is distributable, and the deficit is borne by all future stakers who receive proportionally less than the protocol intends to emit.

---

### Likelihood Explanation

Any user who holds the entire staked supply can trigger this by calling `initiateWithdrawal` for their full balance, waiting any amount of time, and then staking again (or allowing a new staker to enter). This is a normal, unprivileged user action requiring no special role. The scenario is realistic whenever the pool has a single dominant staker or temporarily empties between reward epochs. [4](#0-3) 

---

### Recommendation

In the `updateReward` modifier, only advance `updatedAt` when `totalKernelStaked > 0`. When supply is zero, the elapsed reward tokens should either be re-queued or `updatedAt` should remain frozen so the gap is correctly accounted for when supply returns:

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

This mirrors the remediation suggested in TOKE-4: gate the timestamp advance on a non-zero supply so that zero-supply periods do not silently consume reward budget.

---

### Proof of Concept

Setup: `finishAt = t+15`, `rewardRate = 100`, `rewardPerTokenStored = 0`, `updatedAt = t+0`, `totalKernelStaked = 0`.

| Time | Action | `rewardPerTokenStored` | `updatedAt` | `totalKernelStaked` |
|------|--------|----------------------|-------------|---------------------|
| t+0  | Alice stakes 100 | 0 | t+0 | 100 |
| t+5  | Alice calls `initiateWithdrawal(100)` | `5e18` | t+5 | 0 |
| t+10 | Bob calls `stake(100)` → `updateReward` fires with `totalKernelStaked=0` | `5e18` (frozen) | **t+10** ← gap consumed | 100 |
| t+15 | Bob calls `getReward()` | `10e18` | t+15 | 100 |

- Alice claims: `100 × (5e18 − 0) / 1e18 = 500`
- Bob claims: `100 × (10e18 − 5e18) / 1e18 = 500`
- Total distributed: **1000**
- Total generated: `15 × 100 = 1500`
- **Permanently lost: 500** (rewards from t+5 → t+10 when `totalKernelStaked == 0`, consumed by the unconditional `updatedAt = lastTimeRewardApplicable()` at t+10) [1](#0-0) [2](#0-1)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-326)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-570)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
