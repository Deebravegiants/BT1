### Title
`rewardRate` Integer Division Truncation Permanently Locks Reward Tokens in `KernelDepositPool` - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
In `KernelDepositPool.notifyRewardAmount()`, `rewardRate` is computed as a raw integer division `receivedAmount / duration` with no precision multiplier. The truncated remainder (`receivedAmount % duration`) is transferred into the contract but can never be distributed to stakers, permanently locking those reward tokens.

### Finding Description
`notifyRewardAmount()` computes the per-second reward rate as:

```solidity
rewardRate = receivedAmount / duration;          // line 580
// or, mid-period:
rewardRate = (receivedAmount + remaining) / duration;  // line 583
``` [1](#0-0) 

This is a plain integer division. The truncated dust `receivedAmount % duration` is already held by the contract (transferred in at line 574) but is never accounted for in any future distribution. The `DECIMAL_PRECISION = 1e18` constant is applied only inside `rewardPerToken()` and `earned()` for per-token accounting — it does not prevent the precision loss that already occurred when `rewardRate` was computed. [2](#0-1) 

When a new reward period is started via a subsequent `notifyRewardAmount()` call, the transfer-in pattern measures only the newly transferred amount (`balanceAfter - balanceBefore`), so the previously locked dust is never recaptured. [3](#0-2) 

There is no admin sweep or rescue function in the contract to recover stranded tokens.

### Impact Explanation
Every call to `notifyRewardAmount()` permanently locks `receivedAmount % duration` reward tokens. For low-decimal tokens the loss per call is non-trivial:

- **USDC (6 decimals), 30-day duration (2,592,000 s)**: distributing 100 USDC (100,000,000 units) → `rewardRate = 38`, distributed = 98,496,000 units, **locked = 1,504,000 units (1.504 USDC)** per call.
- **WBTC (8 decimals), 30-day duration**: distributing 1 WBTC (100,000,000 units) → same rate → **locked ≈ 0.01504 WBTC (~$1,500 at $100k/BTC)** per call.

Stakers receive fewer rewards than the amount deposited by the admin. The locked tokens are irrecoverable. This matches the **Medium** impact category: *Permanent freezing of unclaimed yield*.

### Likelihood Explanation
The `rewardsToken` is set at initialization and accepts any ERC20. The protocol is designed to distribute KERNEL-ecosystem rewards, and low-decimal tokens (USDC, WBTC) are common choices for reward programs. The loss occurs on every legitimate `notifyRewardAmount()` call — no adversarial action is required. Likelihood is **High** whenever a sub-18-decimal token is used as `rewardsToken`.

### Recommendation
Scale `rewardRate` by a precision multiplier (e.g., `DECIMAL_PRECISION = 1e18`) at storage time, and divide by the same multiplier when computing actual reward amounts:

```solidity
// In notifyRewardAmount():
rewardRate = (receivedAmount * DECIMAL_PRECISION) / duration;

// In rewardPerToken():
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;
    // DECIMAL_PRECISION already baked into rewardRate, remove the extra multiply

// In earned():
return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account])
    / DECIMAL_PRECISION) + rewards[_account];
```

This is the standard fix used by Synthetix and its derivatives: store the rate at high precision so that integer truncation at the rate level is negligible.

### Proof of Concept

**Setup**:
- `rewardsToken` = USDC (6 decimals)
- `duration` = 30 days = 2,592,000 seconds
- `totalKernelStaked` = 1,000,000e18 KERNEL (non-zero, required by contract)

**Step 1** — Admin calls `notifyRewardAmount(100_000_000)` (100 USDC):
```
receivedAmount = 100_000_000
rewardRate     = 100_000_000 / 2_592_000 = 38   ← truncated (true value: 38.58...)
``` [4](#0-3) 

**Step 2** — Reward period elapses fully (30 days pass).

**Step 3** — All stakers call `getReward()`. Total claimable:
```
rewardRate * duration = 38 * 2_592_000 = 98_496_000 units (98.496 USDC)
``` [5](#0-4) 

**Step 4** — Contract still holds `100_000_000 - 98_496_000 = 1_504_000` units (1.504 USDC). No function exists to distribute or recover this balance. It is permanently locked.

**Step 5** — Admin calls `notifyRewardAmount(100_000_000)` again for a new period. The transfer-in pattern measures only the new 100 USDC transferred; the 1.504 USDC residual is invisible to the accounting and remains locked forever. [3](#0-2)

### Citations

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L573-577)
```text
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-584)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }
```
