### Title
Reward Tokens Permanently Locked When All Stakers Withdraw During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
When `totalKernelStaked` drops to zero during an active reward distribution window, `rewardPerToken()` correctly halts accrual to avoid division-by-zero, but the reward tokens that would have been distributed during the zero-staker interval are permanently locked in the contract with no recovery path.

### Finding Description
`KernelDepositPool.rewardPerToken()` guards against zero supply:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L408-414
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;   // accrual silently stops
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
```

`initiateWithdrawal()` immediately decrements `totalKernelStaked` (before the unlock delay):

```solidity
// contracts/KERNEL/KernelDepositPool.sol L325-326
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
```

The `updateReward` modifier, which runs on every state-changing call, snapshots `updatedAt = lastTimeRewardApplicable()` at the moment of the last withdrawal. Once `totalKernelStaked == 0`, no further accrual occurs. If a new staker later arrives, `updateReward` fires again before the stake is recorded — at that instant `totalKernelStaked` is still 0, so `rewardPerToken()` still returns the stored value and `updatedAt` is advanced to the current time. The reward tokens that should have been distributed during the zero-staker gap are silently skipped and remain in the contract balance forever.

When the reward period eventually expires and `notifyRewardAmount()` is called again, the branch taken is:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L579-580
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;   // old locked tokens NOT included
}
```

The stranded tokens are never folded back into the new rate, so they are permanently irrecoverable.

The contract's own NatSpec acknowledges this risk but relies entirely on an off-chain operational assumption:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L17-23
* @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
*      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
*      ensuring there are always some tokens staked...
```

No on-chain enforcement backs this assumption.

### Impact Explanation
Any reward tokens emitted during a zero-staker interval are permanently frozen in the contract. They cannot be claimed by any user and are not recycled into future reward periods. This constitutes **permanent freezing of unclaimed yield** (Medium per the allowed impact scope).

### Likelihood Explanation
`initiateWithdrawal()` is a normal, permissionless user action. All stakers can independently decide to exit — due to market conditions, loss of confidence, or simply end-of-season behaviour — without any coordination. The withdrawal delay (up to 30 days) does not prevent `totalKernelStaked` from hitting zero; it only delays the token transfer. Because the zero-staker state is reachable through ordinary user behaviour with no admin involvement required, likelihood is realistic.

### Recommendation
Add a rescue path for stranded rewards. Two options:

1. **Fold leftover rewards into the next period**: In `notifyRewardAmount()`, when `block.timestamp >= finishAt`, compute the unallocated balance and add it to `receivedAmount` before calculating the new `rewardRate`.
2. **Admin sweep**: Add an admin-only function callable only after `finishAt` that transfers any reward surplus (contract balance minus what is owed to current stakers) back to a treasury address.

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` while 1 000 KERNEL are staked → `rewardRate = 1_000e18 / duration`.
2. The sole staker calls `initiateWithdrawal(1_000)` → `totalKernelStaked = 0`, `updatedAt` snapped to current block.
3. 30 days pass (the full reward window). `rewardPerToken()` returns `rewardPerTokenStored` unchanged throughout; no rewards accrue.
4. A new staker calls `stake(1)`. `updateReward` fires: `totalKernelStaked` is still 0 at that instant → `rewardPerTokenStored` unchanged, `updatedAt` advanced to now.
5. After `finishAt`, admin calls `notifyRewardAmount(100e18)` → `rewardRate = 100e18 / duration`. The original ~1 000e18 reward tokens remain in the contract balance, permanently unclaimable. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L17-23)
```text
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
 */
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-584)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }
```
