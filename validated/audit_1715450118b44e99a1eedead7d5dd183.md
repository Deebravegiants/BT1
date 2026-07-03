### Title
Precision Loss in `rewardPerToken()` Causes Permanent Freezing of Unclaimed Yield When `totalKernelStaked` Is Large - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` uses a Synthetix-style reward accumulator with `DECIMAL_PRECISION = 1e18`. When `totalKernelStaked` is large relative to `rewardRate * timeDelta * 1e18`, the per-period increment to `rewardPerTokenStored` rounds down to zero, silently discarding rewards for that interval. Because there is no recovery path for unallocated rewards, those tokens are permanently frozen in the contract.

---

### Finding Description

`rewardPerToken()` computes the reward accumulator increment as:

```solidity
(rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION) / totalKernelStaked
``` [1](#0-0) 

`DECIMAL_PRECISION` is fixed at `1e18`: [2](#0-1) 

`rewardRate` is derived from the deposited reward amount divided by the distribution duration:

```solidity
rewardRate = receivedAmount / duration;
``` [3](#0-2) 

The precision loss condition is:

```
rewardRate * timeDelta * 1e18 < totalKernelStaked
```

When this holds, the integer division truncates to zero and the rewards for that entire interval are silently discarded. The `updateReward` modifier is triggered on every `stake`, `initiateWithdrawal`, and `getReward` call, so `timeDelta` is frequently as small as one block (~12 s). [4](#0-3) 

A second precision loss occurs in `earned()`:

```solidity
return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
    + rewards[_account];
``` [5](#0-4) 

Even if `rewardPerToken()` returns a non-zero delta, the subsequent division by `DECIMAL_PRECISION` can truncate the per-user earned amount to zero for small balances.

The KERNEL token has a fixed total supply of `1,000,000,000 * 10^18` wei: [6](#0-5) 

There is no admin function to rescue rewards that were lost to rounding; `notifyRewardAmount` only adds new rewards and does not account for previously unaccumulated amounts. [7](#0-6) 

---

### Impact Explanation

Rewards deposited via `notifyRewardAmount` that are lost to per-block rounding are permanently locked in the contract. No user can claim them, and no admin function can recover them. This constitutes **permanent freezing of unclaimed yield**.

Impact: **Medium** — Permanent freezing of unclaimed yield.

---

### Likelihood Explanation

KERNEL has a 1 billion token supply. Consider a realistic scenario:

- `receivedAmount = 1e18` (1 reward token), `duration = 365 days`
- `rewardRate = 1e18 / 31_536_000 ≈ 31_709`
- Per-block increment numerator: `31_709 * 12 * 1e18 ≈ 3.8e23`
- Precision loss threshold: `totalKernelStaked > 3.8e23` ≈ **380,000 KERNEL tokens**

380,000 KERNEL out of a 1 billion supply (0.038%) is trivially achievable in any live deployment. With larger staking participation (e.g., 10% of supply = 1e26 tokens staked), even a reward rate of `1e18 / duration` per second loses every per-block increment unless `timeDelta` exceeds ~3,000 seconds between updates.

Any unprivileged staker calling `stake()` increases `totalKernelStaked` and pushes the system further into the precision-loss regime.

---

### Recommendation

1. **Increase `DECIMAL_PRECISION`**: Replace `1e18` with `1e36` (or higher) so the numerator `rewardRate * timeDelta * DECIMAL_PRECISION` stays above `totalKernelStaked` across realistic staking levels.

2. **Track dust**: Accumulate the remainder from `rewardRate * timeDelta * DECIMAL_PRECISION % totalKernelStaked` and carry it forward to the next update interval, preventing per-period loss.

3. **Enforce a minimum reward rate relative to total staked**: In `notifyRewardAmount`, revert if `rewardRate * DECIMAL_PRECISION < totalKernelStaked` to prevent configurations that guarantee precision loss from the start.

---

### Proof of Concept

**Setup:**
- KERNEL total supply: `1e27` wei (1 billion tokens, 18 decimals)
- `totalKernelStaked = 1e24` (1 million KERNEL tokens staked — 0.1% of supply)
- `receivedAmount = 100e18` (100 reward tokens), `duration = 365 days`
- `rewardRate = 100e18 / 31_536_000 ≈ 3_170_979`

**Per-block precision check (`timeDelta = 12 s`):**
```
numerator = 3_170_979 * 12 * 1e18 = 3.8e25
totalKernelStaked = 1e24
increment = 3.8e25 / 1e24 = 38  (non-zero, OK at this level)
```

**With 10 million KERNEL staked (`totalKernelStaked = 1e25`):**
```
increment = 3.8e25 / 1e25 = 3  (still non-zero but heavily truncated)
```

**With 100 million KERNEL staked (`totalKernelStaked = 1e26`):**
```
increment = 3.8e25 / 1e26 = 0  ← rounds to zero
```

At 10% of total supply staked (100 million KERNEL), every per-block `updateReward` call discards the entire interval's rewards. Over a 365-day period with 12-second blocks, that is `365 * 24 * 3600 / 12 = 2,628,000` intervals, each losing `3_170_979 * 12 = 38,051,748` reward-wei. Total lost: `38,051,748 * 2,628,000 ≈ 1e14` reward-wei per second of staking — effectively **all 100 reward tokens** are permanently frozen in the contract while stakers receive zero yield. [1](#0-0) [5](#0-4) [2](#0-1)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L32-32)
```text
    uint256 public constant DECIMAL_PRECISION = 1e18;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-424)
```text
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
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

**File:** contracts/KERNEL/KERNEL.sol (L9-11)
```text
    constructor(address safeAddress) ERC20("KERNEL", "KERNEL") ERC20Permit("KERNEL") {
        _mint(safeAddress, 1_000_000_000 * 10 ** decimals());
    }
```
