### Title
Reward Token Dust Permanently Locked Due to `rewardRate` Integer Truncation in `notifyRewardAmount` - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.notifyRewardAmount()` computes `rewardRate` via integer division, which truncates the result. The truncated remainder — up to `duration - 1` wei of reward tokens per reward period — is transferred into the contract but can never be distributed to stakers or recovered by any party. There is no sweep or rescue function in the contract.

---

### Finding Description

In `notifyRewardAmount`, the reward rate is set as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;
// Line 583 (mid-period top-up)
rewardRate = (receivedAmount + remaining) / duration;
```

Both divisions truncate (Solidity rounds toward zero). This means the total rewards that will ever be emitted over the period is `rewardRate * duration`, which is strictly less than `receivedAmount` whenever `receivedAmount % duration != 0`. The difference — `receivedAmount % duration` tokens — is already held by the contract (transferred in at line 574) but is never accounted for in `rewardPerTokenStored`, `rewards[user]`, or any other claimable state.

The only outflow path for `rewardsToken` is `getReward()`, which transfers exactly `rewards[msg.sender]` — a value derived entirely from `rewardRate`. The dust is structurally unreachable. No admin sweep, rescue, or emergency withdrawal function exists in the contract. [1](#0-0) 

The `earned()` and `rewardPerToken()` functions compound this: both also use integer division, introducing additional per-user rounding losses on top of the `rewardRate` truncation. [2](#0-1) [3](#0-2) 

---

### Impact Explanation

**Permanent freezing of unclaimed yield (Medium).**

Every call to `notifyRewardAmount` with `receivedAmount % duration != 0` permanently locks `receivedAmount % duration` reward tokens in the contract. With a typical `duration` of 7–30 days (604,800–2,592,000 seconds), the maximum dust per period is `duration - 1` wei. Over many reward periods this accumulates monotonically and is irrecoverable. Stakers collectively receive less yield than was deposited into the contract. [4](#0-3) 

---

### Likelihood Explanation

**Certain.** Any reward amount that is not an exact multiple of `duration` — which is virtually every real-world reward deposit — triggers the truncation. The contract's own NatSpec comment acknowledges a related residue risk (rewards locked when `totalKernelStaked` hits zero), confirming the design is sensitive to this class of issue. [5](#0-4) 

---

### Recommendation

1. **Track and redistribute dust:** After computing `rewardRate`, calculate `dust = receivedAmount - (rewardRate * duration)` and either add it to the next period's reward or transfer it to a treasury address.
2. **Add a sweep function:** Implement an admin-only function to recover the difference between `rewardsToken.balanceOf(address(this))` and the sum of all pending `rewards[user]` balances, so dust does not accumulate permanently.
3. **Round up `rewardRate`:** For the last staker or final distribution, consider ceiling division to ensure all deposited rewards are emitted.

---

### Proof of Concept

```
Setup:
  duration = 604800 (7 days in seconds)
  receivedAmount = 1e18 (1 reward token, 18 decimals)

Step 1: Admin calls notifyRewardAmount(1e18)
  rewardRate = 1e18 / 604800 = 1653439153439153  (truncated)

Step 2: Full period elapses, all stakers call getReward()
  Total emitted = rewardRate * duration
               = 1653439153439153 * 604800
               = 999999999999999744

Step 3: Dust permanently locked in contract:
  1e18 - 999999999999999744 = 256 wei

Over 1000 reward periods: 256,000 wei locked (grows with larger duration values).
With duration = 2592000 (30 days): dust per period up to 2,591,999 wei (~2.6e-12 tokens).
No function exists to recover this dust — confirmed by absence of any sweep/rescue
in KernelDepositPool.sol.
``` [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-389)
```text
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-423)
```text
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
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
