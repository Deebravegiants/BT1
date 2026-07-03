### Title
Missing Emergency Pause Mechanism in `KernelDepositPool` Staking and Withdrawal Functions - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` is a KERNEL token staking contract with no emergency pause capability. Unlike the closely related `KernelVaultETH` and `LRTWithdrawalManager` contracts that implement `PausableUpgradeable` and guard critical functions with `whenNotPaused`, `KernelDepositPool` has no pause mechanism whatsoever. If the contract is exploited, the admin cannot halt staking, withdrawal, or reward distribution operations.

---

### Finding Description

`KernelDepositPool` inherits only from `AccessControlUpgradeable` and `ReentrancyGuardUpgradeable`, with no `PausableUpgradeable` integration. [1](#0-0) 

All five user-callable functions that move KERNEL tokens or distribute rewards are completely unguarded by any pause check: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

There is no `pause()` function, no `whenNotPaused` modifier, and no emergency stop of any kind in the contract. The four admin functions (`setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, `setMaxNumberOfWithdrawalsPerUser`) cannot halt user operations.

By direct contrast, the closely related `KernelVaultETH` — which also handles KERNEL tokens — properly inherits `PausableUpgradeable` and guards its deposit functions: [6](#0-5) [7](#0-6) 

Similarly, `LRTWithdrawalManager` applies `whenNotPaused` to all user-facing withdrawal functions: [8](#0-7) 

---

### Impact Explanation

If the contract is exploited — for example, a bug in the `rewardPerToken()` / `earned()` accounting allows draining of reward tokens, or a flaw in `claimWithdrawal()` allows unauthorized extraction of staked KERNEL — the admin has no mechanism to halt operations. An attacker can continue draining funds while the admin is powerless to stop it. This maps to **High: Theft of unclaimed yield** (reward token drain) or **Critical: Direct theft of user funds** (staked KERNEL drain) depending on the exploit path.

---

### Likelihood Explanation

Medium. The contract holds real user KERNEL tokens and distributes a separate `rewardsToken`. The reward accounting (`rewardPerToken`, `earned`, `updateReward` modifier) involves non-trivial arithmetic across multiple state variables. The absence of a pause mechanism is a defense-in-depth gap that becomes critical if any logic bug exists. The protocol has already demonstrated awareness of this risk by implementing pause in every analogous contract (`KernelVaultETH`, `LRTWithdrawalManager`, `RSETHPoolV3`).

---

### Recommendation

Add `PausableUpgradeable` to `KernelDepositPool` and apply `whenNotPaused` to `stake()`, `stakeFor()`, `initiateWithdrawal()`, `claimWithdrawal()`, and `getReward()`. Add a `pause()` function restricted to an appropriate admin role and an `unpause()` function restricted to `DEFAULT_ADMIN_ROLE`, consistent with the pattern used in `KernelVaultETH`.

```diff
- contract KernelDepositPool is Initializable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
+ contract KernelDepositPool is Initializable, AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {

- function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
+ function stake(uint256 _amount) external nonReentrant whenNotPaused updateReward(msg.sender) {

- function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
+ function initiateWithdrawal(uint256 _amount) external nonReentrant whenNotPaused updateReward(msg.sender) {

- function claimWithdrawal(uint256 _withdrawalId) external nonReentrant {
+ function claimWithdrawal(uint256 _withdrawalId) external nonReentrant whenNotPaused {

- function getReward() external nonReentrant updateReward(msg.sender) {
+ function getReward() external nonReentrant whenNotPaused updateReward(msg.sender) {

+ function pause() external onlyRole(DEFAULT_ADMIN_ROLE) { _pause(); }
+ function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) { _unpause(); }
```

---

### Proof of Concept

1. Admin detects an exploit draining reward tokens from `KernelDepositPool`.
2. Admin attempts to stop the exploit — but there is no `pause()` function to call.
3. The attacker continues calling `getReward()` or `claimWithdrawal()` unimpeded, draining all available reward tokens or staked KERNEL.
4. Compare: if the same scenario occurred in `KernelVaultETH`, the admin would call `pause()` (line 317) to immediately block `depositKernel()` via `whenNotPaused`. [9](#0-8) 

`KernelDepositPool` has no equivalent function anywhere in its 621 lines. [10](#0-9)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L24-24)
```text
contract KernelDepositPool is Initializable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L344-379)
```text
    function claimWithdrawal(uint256 _withdrawalId) external nonReentrant {
        Withdrawal storage withdrawal = withdrawals[_withdrawalId];

        if (withdrawal.user == address(0)) {
            revert WithdrawalDoesNotExist();
        }

        if (withdrawal.user != msg.sender) {
            revert NotYourWithdrawal();
        }

        if (block.timestamp < withdrawal.unlockTime) {
            revert WithdrawalNotReady();
        }

        if (withdrawal.claimed) {
            revert WithdrawalAlreadyClaimed();
        }

        withdrawal.claimed = true;

        // Remove the withdrawal ID from the user's list of withdrawal IDs
        uint256[] storage userWithdrawalIdsArray = userWithdrawalIds[msg.sender];
        for (uint256 i = 0; i < userWithdrawalIdsArray.length; ++i) {
            if (userWithdrawalIdsArray[i] == _withdrawalId) {
                userWithdrawalIdsArray[i] = userWithdrawalIdsArray[userWithdrawalIdsArray.length - 1];
                userWithdrawalIdsArray.pop();
                break;
            }
        }

        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

        emit WithdrawalClaimed(msg.sender, withdrawal.amount, _withdrawalId);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-390)
```text
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

**File:** contracts/KERNEL/KernelVaultETH.sol (L21-21)
```text
contract KernelVaultETH is Initializable, AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L193-195)
```text
    function depositKernel(uint256 amount) external nonReentrant whenNotPaused {
        _depositKernel(msg.sender, amount);
    }
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L317-319)
```text
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L150-161)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
```
