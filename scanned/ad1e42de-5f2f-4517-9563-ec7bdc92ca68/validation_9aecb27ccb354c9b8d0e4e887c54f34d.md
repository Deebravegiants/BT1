### Title
`KernelDepositPool.stake` / `stakeFor` Do Not Account for Fee-on-Transfer Tokens When Updating Staking Balances — (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.stake` and `stakeFor` credit the full nominal `_amount` to `balanceOf` and `totalKernelStaked` without measuring the actual tokens received. The same contract's `notifyRewardAmount` explicitly uses a before/after balance snapshot to handle fee-on-transfer tokens for the rewards token. This inconsistency means that if `kernelToken` carries a transfer fee, staking balances are permanently inflated relative to actual holdings, diluting rewards for all stakers and eventually making withdrawals impossible for the last claimants.

### Finding Description
In `KernelDepositPool.stake`:

```solidity
balanceOf[msg.sender] += _amount;
totalKernelStaked += _amount;
kernelToken.safeTransferFrom(msg.sender, address(this), _amount);
```

And in `stakeFor`:

```solidity
balanceOf[_account] += _amount;
totalKernelStaked += _amount;
kernelToken.safeTransferFrom(msg.sender, address(this), _amount);
```

Both functions update accounting state with the caller-supplied `_amount` before (or without) verifying what was actually received. If `kernelToken` deducts a transfer fee, the contract holds fewer tokens than `totalKernelStaked` records.

By contrast, `notifyRewardAmount` in the same contract explicitly guards against this:

```solidity
uint256 balanceBefore = rewardsToken.balanceOf(address(this));
rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
uint256 balanceAfter = rewardsToken.balanceOf(address(this));
uint256 receivedAmount = balanceAfter - balanceBefore;
// "Calculate the actual amount of tokens received in case of a transfer fee (tax)"
```

The developer comment confirms awareness of fee-on-transfer tokens for the rewards path, yet the staking path has no equivalent protection.

### Impact Explanation
- `totalKernelStaked` is inflated by the cumulative fee amount across all stakes. Since `rewardPerToken()` divides by `totalKernelStaked`, every staker earns fewer rewards than entitled — **theft of unclaimed yield (High)**.
- On withdrawal, `claimWithdrawal` calls `kernelToken.safeTransfer(msg.sender, withdrawal.amount)` using the inflated recorded amount. Once the real token balance is exhausted, later withdrawers cannot claim — **temporary/permanent freezing of funds (Critical/Medium)**.

### Likelihood Explanation
Any user can call `stake` permissionlessly. The condition is that `kernelToken` carries a transfer fee. The `notifyRewardAmount` guard and its inline comment show the developers explicitly considered this class of token for the rewards path, making it a realistic concern for the staking path as well. If the KERNEL token is upgraded or replaced with a fee-bearing variant, the vulnerability becomes immediately exploitable by any depositor.

### Recommendation
Apply the same before/after balance pattern used in `notifyRewardAmount` to both `stake` and `stakeFor`:

```solidity
uint256 balanceBefore = kernelToken.balanceOf(address(this));
kernelToken.safeTransferFrom(msg.sender, address(this), _amount);
uint256 received = kernelToken.balanceOf(address(this)) - balanceBefore;

balanceOf[_account] += received;
totalKernelStaked += received;
```

### Proof of Concept
1. Deploy `KernelDepositPool` with a `kernelToken` that charges a 1% transfer fee.
2. Alice calls `stake(1000e18)`. The contract receives `990e18` tokens but records `balanceOf[Alice] = 1000e18` and `totalKernelStaked = 1000e18`.
3. Bob calls `stake(1000e18)`. Contract receives another `990e18`; records `totalKernelStaked = 2000e18`. Actual balance: `1980e18`.
4. Both call `initiateWithdrawal(1000e18)` and wait for the delay.
5. Alice calls `claimWithdrawal` — succeeds, draining `1000e18` from the `1980e18` balance.
6. Bob calls `claimWithdrawal` — reverts because only `980e18` remains, but `withdrawal.amount = 1000e18`. Bob's funds are frozen.

Reward dilution occurs in parallel: `rewardPerToken()` divides by `totalKernelStaked = 2000e18` instead of the correct `1980e18`, so both stakers earn ~1% fewer rewards than owed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L296-314)
```text
    function stakeFor(
        address _account,
        uint256 _amount
    )
        external
        nonReentrant
        onlyRole(STAKE_FOR_ROLE)
        updateReward(_account)
    {
        UtilLib.checkNonZeroAddress(_account);

        if (_amount == 0) revert AmountZero();

        balanceOf[_account] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit StakedFor(msg.sender, _account, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L375-378)
```text
        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

        emit WithdrawalClaimed(msg.sender, withdrawal.amount, _withdrawalId);
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
