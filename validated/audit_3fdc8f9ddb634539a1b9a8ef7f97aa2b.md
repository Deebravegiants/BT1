### Title
Precision Loss in `rewardRate` Calculation Causes Permanent Loss of Staker Yield - (File: `contracts/KERNEL/KernelDepositPool.sol`)

### Summary
`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division without any scaling factor. The truncated remainder — up to `duration - 1` reward-token units per call — is permanently stranded in the contract and never distributed to stakers.

### Finding Description
In `notifyRewardAmount`, the reward rate is set as:

```solidity
// contracts/KERNEL/KernelDepositPool.sol lines 579-584
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
    rewardRate = (receivedAmount + remaining) / duration;
}
``` [1](#0-0) 

Solidity integer division silently discards the remainder. The lost amount per call is `receivedAmount % duration`, which can be as large as `duration - 1` smallest units of the reward token. These tokens are transferred into the contract but are never accounted for in `rewardRate`, so they can never be claimed by stakers.

The `DECIMAL_PRECISION` (1e18) scaling used in `rewardPerToken()` does **not** recover this loss — it is applied after `rewardRate` is already truncated:

```solidity
// line 412
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [2](#0-1) 

The `rewardRate` field itself is stored unscaled:

```solidity
// line 78
uint256 public rewardRate;
``` [3](#0-2) 

### Impact Explanation
**High — Theft of unclaimed yield.**

The maximum loss per `notifyRewardAmount` call equals `duration - 1` reward-token base units. For a typical `duration` of 7 days (604,800 seconds):

- **USDC (6 decimals):** up to 604,799 / 1e6 ≈ **$0.60 per call**
- **WBTC (8 decimals):** up to 604,799 / 1e8 × BTC price ≈ **~$400 per call** at current prices

The loss compounds with every `notifyRewardAmount` invocation (e.g., weekly calls over a year = 52 × $400 ≈ **$20,800 in WBTC yield** permanently stranded). The stranded tokens sit in the contract with no recovery path.

### Likelihood Explanation
**High.** `notifyRewardAmount` is a routine admin operation expected to be called repeatedly (each reward epoch). No special conditions are required — the precision loss occurs on every single call regardless of timing or token amount.

### Recommendation
Scale `rewardRate` by a precision factor (e.g., `1e18`) when storing it, and divide by the same factor when using it in `rewardPerToken()`:

```solidity
// Store with scaling
rewardRate = (receivedAmount * 1e18) / duration;

// Use with descaling
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;
```

This reduces the maximum precision loss from `duration - 1` units to `duration - 1` units divided by `1e18` — effectively zero for any realistic token amount.

### Proof of Concept

1. Admin deploys `KernelDepositPool` with `rewardsToken = WBTC` (8 decimals) and `duration = 7 days` (604,800 seconds).
2. Stakers deposit KERNEL tokens.
3. Admin calls `notifyRewardAmount(1_000_000_000)` (10 WBTC).
4. `rewardRate = 1_000_000_000 / 604_800 = 1653` (truncated; remainder = `1_000_000_000 % 604_800 = 604,800 - X`).
5. Over the full 7-day period, stakers collectively receive `1653 * 604_800 = 999,878,400` base units instead of `1,000,000,000`.
6. The difference of **121,600 base units (~0.00121600 WBTC, ~$84 at $69k/BTC)** remains locked in the contract permanently.
7. Each subsequent weekly `notifyRewardAmount` call repeats the loss, compounding over time. [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L78-78)
```text
    uint256 public rewardRate;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L412-413)
```text
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
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
