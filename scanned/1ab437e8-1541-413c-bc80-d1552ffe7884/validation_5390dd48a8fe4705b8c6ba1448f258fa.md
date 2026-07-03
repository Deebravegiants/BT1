### Title
Reward Tokens Permanently Locked in `KernelDepositPool` When `totalKernelStaked` Drops to Zero Mid-Period - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` distributes a `rewardsToken` to stakers of `kernelToken`. When `totalKernelStaked` reaches zero during an active reward distribution window, the reward tokens that should have been distributed during the zero-staking interval are permanently locked in the contract. No admin or user function exists to recover them.

---

### Finding Description

`KernelDepositPool` uses a Synthetix-style reward accounting model. The `rewardPerToken()` function accumulates rewards proportional to elapsed time and `rewardRate`, but only when `totalKernelStaked > 0`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;   // accumulation halts
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [1](#0-0) 

When `totalKernelStaked` is zero, `rewardPerTokenStored` is frozen. The `rewardRate` continues to be non-zero and `finishAt` is still in the future, so reward tokens that were pre-funded via `notifyRewardAmount` sit idle in the contract. They are never credited to any user and there is no function to recover them.

Any user can bring `totalKernelStaked` to zero by calling `initiateWithdrawal` for their full balance:

```solidity
function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    ...
    balanceOf[msg.sender] -= _amount;
    totalKernelStaked -= _amount;   // can reach 0
    ...
}
``` [2](#0-1) 

The guard in `notifyRewardAmount` only prevents *starting* a new reward period with zero stakers; it does not prevent the supply from draining to zero *during* an active period:

```solidity
function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
    ...
    if (totalKernelStaked == 0) revert NoStakedTokens();   // only at period start
    ...
}
``` [3](#0-2) 

The contract itself acknowledges this in its NatSpec comment but relies entirely on an off-chain operational assumption ("ensuring there are always some tokens staked … for the entire duration of the reward period"), with no on-chain enforcement or recovery path: [4](#0-3) 

The admin functions cover only `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser`. None recover stranded `rewardsToken` balances. `KernelDepositPool` does not inherit from `Recoverable` (which provides `recoverTokens`): [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

`rewardsToken` pre-funded into `KernelDepositPool` for a reward period becomes permanently unclaimable whenever `totalKernelStaked` reaches zero mid-period. The tokens remain in the contract balance but are never distributed to any user and cannot be withdrawn by any role. This is a direct loss of yield owed to stakers.

---

### Likelihood Explanation

The scenario is reachable by any unprivileged staker. If a single user holds the entire staked supply (common in early protocol stages or after mass withdrawals), they can call `initiateWithdrawal` for their full balance at any time, immediately dropping `totalKernelStaked` to zero. No special permissions, front-running, or external conditions are required. The `withdrawalDelay` does not prevent the accounting damage — it only delays the KERNEL token transfer, while `totalKernelStaked` is decremented immediately at `initiateWithdrawal` time. [7](#0-6) 

---

### Recommendation

Add an admin-only `recoverStrandedRewards` function (or inherit `Recoverable`) that allows the admin to sweep `rewardsToken` balance in excess of what is owed to current stakers. Alternatively, enforce the invariant on-chain by reverting `initiateWithdrawal` when it would bring `totalKernelStaked` to zero while a reward period is active (`block.timestamp < finishAt`), or by tracking and crediting the "unallocated" reward tokens to a treasury address whenever `totalKernelStaked` is zero.

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` with `duration = 7 days`. `rewardRate = 1_000e18 / 7 days`. `finishAt = now + 7 days`.
2. Alice is the only staker with `balanceOf[Alice] = 100e18`, `totalKernelStaked = 100e18`.
3. After 1 day, Alice calls `initiateWithdrawal(100e18)`. `totalKernelStaked` becomes `0`.
4. For the remaining 6 days, `rewardPerToken()` returns the frozen `rewardPerTokenStored`. No rewards accumulate.
5. `rewardRate * 6 days ≈ 857e18` reward tokens are stuck in the contract.
6. No function exists to recover them. `notifyRewardAmount` reverts with `NoStakedTokens` if called while `totalKernelStaked == 0`, so even a new period cannot be started to "absorb" the stranded tokens. [8](#0-7) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-23)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
 */
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L24-25)
```text
contract KernelDepositPool is Initializable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-338)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

        // Create a withdrawal record
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
        userWithdrawalIds[msg.sender].push(withdrawalId);

        emit WithdrawalInitiated(msg.sender, _amount, withdrawalId, unlockTime);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-591)
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
```

**File:** contracts/utils/Recoverable.sol (L41-57)
```text
    function recoverTokens(
        address tokenAddress,
        address recipient,
        uint256 amount
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(tokenAddress);
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (IERC20(tokenAddress).balanceOf(address(this)) < amount) revert InsufficientBalance();

        IERC20(tokenAddress).safeTransfer(recipient, amount);

        emit TokensRecovered(tokenAddress, recipient, amount);
    }
```
