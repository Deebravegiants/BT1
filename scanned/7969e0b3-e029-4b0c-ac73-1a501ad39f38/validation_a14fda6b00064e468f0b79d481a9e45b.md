### Title
Precision Loss in `notifyRewardAmount` Permanently Freezes Reward Tokens - (File: `contracts/KERNEL/KernelDepositPool.sol`)

### Summary
`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division of `receivedAmount / duration`. The truncated remainder (`receivedAmount % duration`) is transferred into the contract but can never be distributed to stakers, permanently freezing it. The extension path (when a new reward period is started before the previous one ends) compounds the loss by also underestimating the leftover rewards before performing a second truncating division.

### Finding Description
In `notifyRewardAmount`, the reward rate is computed as:

```solidity
// Line 580 — fresh period
rewardRate = receivedAmount / duration;

// Lines 582-583 — extension of an active period
uint256 remaining = (finishAt - block.timestamp) * rewardRate;
rewardRate = (receivedAmount + remaining) / duration;
``` [1](#0-0) 

The dust lost per call is `receivedAmount % duration` for a fresh period. For the extension path the loss is amplified: `remaining` is computed from the already-truncated `rewardRate`, so it underestimates the true leftover by the dust from the previous call; the subsequent division then introduces a second truncation on top of that.

The total rewards that will ever be distributed over the period is `rewardRate * duration`, which is strictly less than `receivedAmount`. The difference sits in the contract's `rewardsToken` balance permanently. There is no `recoverERC20`, `sweep`, or any other admin rescue function in the contract. [2](#0-1) 

### Impact Explanation
**Medium — Permanent freezing of unclaimed yield.**

Every call to `notifyRewardAmount` locks `receivedAmount % duration` reward tokens in the contract forever. For a `duration` of 7 days (604 800 seconds) and a reward token with low decimals (e.g. 8-decimal WBTC), the dust per call can be up to 604 799 token-units (≈ 0.006 WBTC ≈ $540 at $90 000/BTC). Repeated calls and the extension path multiply this loss. The stuck tokens are irrecoverable because no sweep function exists. [1](#0-0) 

### Likelihood Explanation
This occurs on every invocation of `notifyRewardAmount` where `receivedAmount` is not an exact multiple of `duration`. Because `duration` is measured in seconds (e.g. 604 800 for 7 days) and reward amounts are arbitrary integers, the condition `receivedAmount % duration == 0` is almost never satisfied in practice. The admin calling this function in good faith is sufficient to trigger the loss — no malicious intent or compromise is required. [2](#0-1) 

### Recommendation
1. **Track and account for dust explicitly.** After computing `rewardRate`, calculate the undistributed remainder and either return it to the caller or carry it forward into the next period:
   ```solidity
   rewardRate = receivedAmount / duration;
   uint256 dust = receivedAmount % duration;
   // return dust to caller or accumulate for next period
   ```
2. **For the extension path**, use the actual contract balance minus already-owed rewards to compute `remaining` rather than relying on the truncated `rewardRate`.
3. **Add a token-rescue function** (restricted to admin) so that any accidentally locked ERC20 tokens (excluding the staking token) can be recovered.

### Proof of Concept
Scenario: admin calls `notifyRewardAmount` with a WBTC-like 8-decimal reward token.

- `duration` = 7 days = 604 800 seconds
- `receivedAmount` = 1 000 000 (0.01 WBTC ≈ $900)
- `rewardRate` = 1 000 000 / 604 800 = **1** (integer division)
- Tokens actually distributed = 1 × 604 800 = 604 800
- **Dust permanently locked** = 1 000 000 − 604 800 = **395 200 units ≈ $356**

For the extension path, if the admin calls `notifyRewardAmount` again halfway through the period:

- `remaining` = (302 400 seconds left) × 1 = 302 400 (underestimates true leftover by 197 600 units of dust from the first call)
- `rewardRate` = (1 000 000 + 302 400) / 604 800 = 1 302 400 / 604 800 = **2**
- Tokens distributed = 2 × 604 800 = 1 209 600
- Total deposited = 2 000 000; total distributed = 1 209 600; **total permanently locked ≈ 790 400 units ≈ $711** [1](#0-0)

### Citations

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
