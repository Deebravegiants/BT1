### Title
Precision Loss in `rewardRate` Calculation Permanently Locks Reward Tokens for Low-Decimal Reward Tokens - (`contracts/KERNEL/KernelDepositPool.sol`)

### Summary
`KernelDepositPool.notifyRewardAmount()` calculates `rewardRate = receivedAmount / duration` using raw integer division with no precision scaling. For low-decimal reward tokens (e.g., WBTC at 8 decimals, USDC at 6 decimals), the truncation remainder (`receivedAmount % duration`) is permanently locked in the contract with no recovery path. Additionally, the `rewardRate == 0` guard forces the admin to provide a minimum reward amount of at least `duration` token-units, which for low-decimal tokens over long periods represents a significant economic constraint.

### Finding Description
In `notifyRewardAmount`, the reward rate is set as:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:579-584
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
    rewardRate = (receivedAmount + remaining) / duration;
}
``` [1](#0-0) 

`rewardRate` is stored as a raw integer with no precision multiplier. The contract will distribute exactly `rewardRate * duration` tokens over the period, but `receivedAmount` tokens were already transferred in. The difference — `receivedAmount % duration` — is permanently stranded in the contract because there is no `sweep`, `rescue`, or `recoverERC20` function anywhere in the contract. [2](#0-1) 

The `rewardRate == 0` guard at line 586 prevents a silent zero-distribution but does not fix the precision loss for non-zero rates:

```solidity
if (rewardRate == 0) revert RewardRateZero();
``` [3](#0-2) 

The `rewardPerToken()` function applies `DECIMAL_PRECISION` (1e18) to the time delta, not to `rewardRate` itself, so the truncation in `rewardRate` propagates directly into all reward calculations:

```solidity
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [4](#0-3) 

**Concrete example with WBTC (8 decimals), 1-year distribution:**
- `receivedAmount = 1e8` (1 WBTC)
- `duration = 31,536,000` seconds
- `rewardRate = 1e8 / 31,536,000 = 3` (truncated from 3.17...)
- Total distributed = `3 × 31,536,000 = 94,608,000` satoshis = 0.946 WBTC
- **Permanently locked = 5,392,000 satoshis ≈ 0.054 WBTC ≈ $1,458 at $27k/BTC**

**Zero-rate constraint example:**
- `receivedAmount = 31,535,999` satoshis (just under 0.315 WBTC)
- `duration = 31,536,000` seconds
- `rewardRate = 0` → `notifyRewardAmount` reverts with `RewardRateZero`
- Admin is forced to provide at least 31,536,000 satoshis (≈ $8,500) just to start a 1-year distribution

### Impact Explanation
**Permanent freezing of unclaimed yield (Medium).** Every call to `notifyRewardAmount` with a low-decimal reward token permanently locks `receivedAmount % duration` tokens in the contract. These tokens are deposited by the admin with the intent of distributing them to stakers, but they are irrecoverable. For WBTC or similar tokens over realistic distribution periods, this can represent hundreds to thousands of dollars per distribution epoch.

### Likelihood Explanation
The `rewardsToken` is set once at initialization and is not restricted to 18-decimal tokens. [5](#0-4) 

If the protocol configures `KernelDepositPool` with a low-decimal reward token (WBTC, USDC, USDT, etc.) — a realistic operational choice — the precision loss occurs on every `notifyRewardAmount` call. No attacker action is required; the loss is automatic and structural.

### Recommendation
Scale `rewardRate` by `DECIMAL_PRECISION` at storage time and remove the scaling from `rewardPerToken()`:

```solidity
// In notifyRewardAmount:
rewardRate = receivedAmount * DECIMAL_PRECISION / duration;

// In rewardPerToken():
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;
```

This eliminates the per-epoch token loss and reduces the minimum viable reward amount to 1 wei of the reward token regardless of decimals.

### Proof of Concept
1. Deploy `KernelDepositPool` with WBTC (8 decimals) as `rewardsToken`.
2. Set `duration = 31,536,000` (1 year).
3. Admin calls `notifyRewardAmount(1e8)` (1 WBTC).
4. `rewardRate = 1e8 / 31,536,000 = 3`.
5. After the full year, total claimable rewards = `3 × 31,536,000 = 94,608,000` satoshis.
6. Contract balance of WBTC = `1e8 - 94,608,000 = 5,392,000` satoshis permanently locked.
7. No admin function exists to recover the locked tokens.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L259-270)
```text
    function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_kernelToken);
        UtilLib.checkNonZeroAddress(_rewardToken);

        __AccessControl_init();
        __ReentrancyGuard_init();

        _setupRole(DEFAULT_ADMIN_ROLE, _admin);

        kernelToken = IERC20(_kernelToken);
        rewardsToken = IERC20(_rewardToken);
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
