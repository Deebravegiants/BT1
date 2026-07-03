### Title
Uninitialized `withdrawalDelay` Defaults to Zero, Bypassing Intended Withdrawal Lockup - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.sol` declares a `withdrawalDelay` state variable that is never set in `initialize()`, leaving it at the Solidity default of `0`. This is the direct analog of the reference bug: a time-delay value that should represent a meaningful duration (e.g., days) is effectively set to zero seconds, allowing users to bypass the intended withdrawal lockup entirely.

### Finding Description
`KernelDepositPool` is a staking contract for KERNEL tokens. It declares a `withdrawalDelay` state variable intended to enforce a waiting period between `initiateWithdrawal()` and `claimWithdrawal()`. [1](#0-0) 

The `initialize()` function never assigns a value to `withdrawalDelay`: [2](#0-1) 

So `withdrawalDelay` remains `0` after deployment. When a user calls `initiateWithdrawal()`, the unlock time is computed as: [3](#0-2) 

With `withdrawalDelay == 0`, `unlockTime == block.timestamp`. The `claimWithdrawal()` guard: [4](#0-3) 

…is satisfied immediately (even in the same block), since `block.timestamp >= unlockTime` is true from the moment of initiation. The admin setter exists but is never called during initialization: [5](#0-4) 

The upper-bound constant `MAX_WITHDRAWAL_DELAY = 30 days` is correct, but the actual operative value starts at `0`: [6](#0-5) 

### Impact Explanation
Until an admin explicitly calls `setWithdrawalDelay()`, any user can stake KERNEL tokens and immediately reclaim them in the same block, completely bypassing the withdrawal lockup. The staking contract fails to deliver its promised lockup guarantee. No funds are stolen, but the core invariant of the contract (stakers must wait before withdrawing) is broken.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The window exists from the moment of deployment until an admin calls `setWithdrawalDelay()`. Because `initialize()` does not set the delay, any deployment that omits a follow-up admin call leaves the contract in this broken state. This is a realistic deployment scenario.

### Recommendation
Set a non-zero default for `withdrawalDelay` directly inside `initialize()`, for example:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    // ... existing setup ...
    withdrawalDelay = 7 days; // enforce a meaningful default
}
```

Alternatively, add a `require(withdrawalDelay > 0)` guard inside `initiateWithdrawal()` so the function reverts until the admin has configured the delay.

### Proof of Concept
1. `KernelDepositPool` is deployed and `initialize()` is called — `withdrawalDelay` is `0`.
2. Alice calls `initiateWithdrawal(amount)`. `unlockTime = block.timestamp + 0 = block.timestamp`.
3. Alice immediately calls `claimWithdrawal(withdrawalId)` in the same block. `block.timestamp >= unlockTime` → passes.
4. Alice receives her KERNEL tokens with zero waiting period, defeating the lockup mechanism. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L35-35)
```text
    uint256 public constant MAX_WITHDRAWAL_DELAY = 30 days;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L95-96)
```text
    /// @notice Delay (in seconds) before withdrawals can be claimed after initiation
    uint256 public withdrawalDelay;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L259-271)
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L598-604)
```text
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
    }
```
