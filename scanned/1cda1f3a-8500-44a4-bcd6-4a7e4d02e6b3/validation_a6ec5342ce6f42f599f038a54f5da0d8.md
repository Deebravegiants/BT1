### Title
`rewardPerToken()` Increment Rounds to Zero with Low-Decimal Reward Tokens and Large Stake — (`contracts/KERNEL/KernelDepositPool.sol`)

### Summary

`KernelDepositPool` implements a Synthetix-style staking rewards mechanism. The `rewardPerToken()` function accumulates a per-token reward increment on every `updateReward` call. When the configured `rewardsToken` has few decimals (e.g., USDC at 6 decimals), the `rewardRate` is a small integer, and the per-second increment to `rewardPerTokenStored` rounds to zero whenever `totalKernelStaked` is sufficiently large. Rewards that round to zero in each update interval are permanently unrecoverable, causing a portion of the deposited reward tokens to be frozen in the contract.

### Finding Description

`notifyRewardAmount` computes `rewardRate` in raw token-wei per second with no additional precision scaling:

```solidity
rewardRate = receivedAmount / duration;
``` [1](#0-0) 

`rewardPerToken()` then accumulates the per-token share using `DECIMAL_PRECISION = 1e18` as the only scaling factor:

```solidity
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [2](#0-1) 

The increment rounds to zero whenever:

```
rewardRate * timeDelta * 1e18 < totalKernelStaked
```

**Concrete scenario — USDC rewards, 1 million KERNEL staked:**

| Parameter | Value |
|---|---|
| Reward token | USDC (6 decimals) |
| `receivedAmount` | 1,000 USDC = 1,000,000,000 (1e9) |
| `duration` | 30 days = 2,592,000 s |
| `rewardRate` | `1e9 / 2592000 ≈ 385` (USDC wei/s) |
| `totalKernelStaked` | 1,000,000 KERNEL = 1e24 |

Per-second increment: `385 * 1 * 1e18 / 1e24 = 385 / 1e6 = 0`.

The increment only becomes non-zero when `timeDelta ≥ 1e24 / (385 * 1e18) ≈ 2,597 seconds (~43 minutes)`. Every `updateReward` call that occurs within a 43-minute window produces a zero increment, and those rewards are permanently lost — they are never added to `rewardPerTokenStored` and cannot be recovered.

The `updateReward` modifier is triggered on every user-facing call: [3](#0-2) 

So `stake()`, `stakeFor()`, `initiateWithdrawal()`, and `getReward()` all trigger the rounding loss. [4](#0-3) 

### Impact Explanation

**Permanent freezing of unclaimed yield (Medium).** Reward tokens deposited by the admin via `notifyRewardAmount` are transferred into the contract but can never be distributed to stakers if the per-update increment consistently rounds to zero. The stuck tokens have no recovery path — there is no admin sweep function for undistributed rewards. The fraction lost scales with interaction frequency: the more often users interact with the contract, the larger the proportion of rewards permanently frozen.

### Likelihood Explanation

**Medium.** The `rewardsToken` is set at initialization and is not constrained to 18-decimal tokens. USDC is a natural candidate for a staking reward token in the Kelp/KERNEL ecosystem. KERNEL tokens are 18-decimal and a protocol with meaningful TVL would easily have millions of KERNEL staked (1e24+ wei), which is the threshold at which per-second increments round to zero for USDC rewards. No privileged compromise is required — the rounding occurs automatically as users interact normally with the contract. [5](#0-4) 

### Recommendation

Scale `rewardRate` by `DECIMAL_PRECISION` at assignment time so that the stored rate already carries the precision multiplier:

```solidity
// In notifyRewardAmount:
rewardRate = (receivedAmount * DECIMAL_PRECISION) / duration;

// In rewardPerToken():
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;

// earned() remains unchanged since DECIMAL_PRECISION cancels correctly
```

This is the approach used by the canonical Synthetix implementation and eliminates the rounding-to-zero condition for any realistic combination of reward token decimals and stake size.

### Proof of Concept

1. Admin calls `setRewardsDuration(2592000)` (30 days).
2. Admin calls `notifyRewardAmount(1_000_000_000)` (1,000 USDC). `rewardRate = 1_000_000_000 / 2_592_000 = 385`.
3. 1,000,000 KERNEL tokens are staked across users → `totalKernelStaked = 1e24`.
4. User A calls `stake(1)` at `t = 0`. `updateReward` fires: `rewardPerToken()` increment = `385 * 0 * 1e18 / 1e24 = 0`. `rewardPerTokenStored` unchanged.
5. 60 seconds later, User B calls `getReward()`. `updateReward` fires: increment = `385 * 60 * 1e18 / 1e24 = 23100e18 / 1e24 = 23100 / 1e6 = 0`. Still zero.
6. After 2,597 seconds, the first non-zero increment occurs. All rewards that should have accrued during the first 2,596 seconds (`385 * 2596 ≈ 999,460` USDC wei) are permanently lost.
7. If users interact every minute throughout the 30-day period, the total lost rewards ≈ `(2596/2597) * 1000 USDC ≈ 999.6 USDC` permanently frozen in the contract. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L32-32)
```text
    uint256 public constant DECIMAL_PRECISION = 1e18;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
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
