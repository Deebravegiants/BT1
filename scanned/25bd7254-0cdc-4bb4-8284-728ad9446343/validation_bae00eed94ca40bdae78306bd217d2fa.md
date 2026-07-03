### Title
Accidentally Deposited Tokens in `KernelDepositPool` Would Get Permanently Stuck - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` is a staking-and-rewards contract that exclusively handles two tokens: `kernelToken` (the staking asset) and `rewardsToken` (the reward asset). The contract provides no mechanism to recover any other ERC-20 token accidentally transferred to it. Any third token sent to the contract — whether by a user mistake or an admin operational error — is permanently frozen with no path to recovery.

### Finding Description
`KernelDepositPool` manages exactly two ERC-20 tokens:

- `kernelToken` — received via `stake()` / `stakeFor()`, returned via `claimWithdrawal()`
- `rewardsToken` — deposited by admin via `notifyRewardAmount()`, claimed by stakers via `getReward()` [1](#0-0) 

The contract exposes no sweep, rescue, or `recoverTokens` function. It does not inherit from the protocol's own `Recoverable` abstract contract (which provides exactly this capability): [2](#0-1) 

The full admin function surface of `KernelDepositPool` is limited to `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser` — none of which can move an arbitrary token out of the contract: [3](#0-2) 

If any token other than `kernelToken` or `rewardsToken` is transferred to the contract address — for example, a user accidentally calling `transfer()` instead of `approve()` + `stake()`, or the admin accidentally calling `notifyRewardAmount` after changing `rewardsToken` off-chain but before updating the contract — those tokens are permanently locked.

The contract is also not `receive()`-capable for ETH, so native ETH sent to it would revert, but any ERC-20 `transfer()` call succeeds silently and the tokens are irrecoverable.

### Impact Explanation
Any ERC-20 token accidentally sent directly to `KernelDepositPool` is permanently frozen. There is no admin escape hatch, no upgrade path that is guaranteed to be executed, and no on-chain mechanism to retrieve the funds. This matches the **permanent freezing of funds** impact class.

### Likelihood Explanation
The scenario is realistic in two ways:
1. A user intending to stake KERNEL tokens calls `kernelToken.transfer(address(kernelDepositPool), amount)` instead of `approve` + `stake()`. The tokens arrive but are not credited to any balance mapping and cannot be recovered.
2. The admin intends to fund a new reward period with a different reward token but the `rewardsToken` state variable has not yet been updated; `notifyRewardAmount` pulls the correct `rewardsToken`, but if the admin pre-transfers the new token directly, those tokens are stuck.

Likelihood is **Low** (requires an operational mistake), but the consequence is irreversible.

### Recommendation
`KernelDepositPool` should inherit from the protocol's existing `Recoverable` contract, or add an equivalent admin-only `recoverTokens(address token, address recipient, uint256 amount)` function that explicitly guards against withdrawing `kernelToken` or `rewardsToken` (to prevent draining staker principal or undistributed rewards):

```solidity
function recoverTokens(address token, address recipient, uint256 amount)
    external onlyRole(DEFAULT_ADMIN_ROLE)
{
    if (token == address(kernelToken)) revert CannotRecoverStakingToken();
    if (token == address(rewardsToken)) revert CannotRecoverRewardsToken();
    IERC20(token).safeTransfer(recipient, amount);
}
```

### Proof of Concept
1. Deploy `KernelDepositPool` with `kernelToken = KERNEL` and `rewardsToken = USDC`.
2. A user holds `WETH` and mistakenly calls `WETH.transfer(address(kernelDepositPool), 1e18)`.
3. The transfer succeeds; `WETH.balanceOf(address(kernelDepositPool)) == 1e18`.
4. Inspect every function in `KernelDepositPool` — `claimWithdrawal` only transfers `kernelToken`, `getReward` only transfers `rewardsToken`, and no other outbound transfer path exists.
5. The 1 WETH is permanently locked with no on-chain recovery path. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L62-66)
```text
    /// @notice The KERNEL token contract (used for staking)
    IERC20 public kernelToken;

    /// @notice The rewards token contract
    IERC20 public rewardsToken;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L375-390)
```text
        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

        emit WithdrawalClaimed(msg.sender, withdrawal.amount, _withdrawalId);
    }

    /// @notice Allows a user to claim their earned rewards
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
        }
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L544-621)
```text
    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Sets the duration for rewards distribution
     * @param _duration The duration in seconds
     */
    function setRewardsDuration(uint256 _duration) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (finishAt >= block.timestamp) revert RewardDurationNotFinished();
        if (_duration == 0) revert InvalidDuration();
        duration = _duration;
        emit RewardsDurationUpdated(_duration);
    }

    /**
     * @notice Notifies the contract about a new reward amount
     * @dev Uses a transfer-in pattern to determine the exact reward amount received.
     *      Also, to avoid undistributed rewards when no one is staked, this function reverts if totalKernelStaked is
     *      zero.
     * @param _amount The amount of reward tokens to add
     */
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

    /**
     * @notice Updates the withdrawal delay
     * @param _withdrawalDelay The new withdrawal delay
     */
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
    }

    /**
     * @notice Updates the maximum number of withdrawals per user
     * @param _maxNumberOfWithdrawalsPerUser The new maximum number of withdrawals per user
     */
    function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
            revert InvalidMaxNumberOfWithdrawalsPerUser();
        }

        maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
        emit MaxNumberOfWithdrawalsPerUserUpdated(_maxNumberOfWithdrawalsPerUser);
    }
}
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
