### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks `initiateWithdrawal` Until Admin Intervenes - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.initialize` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at its default value of `0`. Because `initiateWithdrawal` guards against exceeding this limit with `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, and any `uint256` array length is always `>= 0`, the function unconditionally reverts with `WithdrawalLimitReached()` from the moment of deployment until an admin explicitly calls `setMaxNumberOfWithdrawalsPerUser`. This is the direct analog of the Duality `_acceptAdmin` bug: a user-facing function is rendered permanently inoperable because a prerequisite state variable is never initialized.

### Finding Description
`KernelDepositPool` is an upgradeable staking contract where users stake KERNEL tokens and later retrieve them via a two-step withdrawal flow (`initiateWithdrawal` → `claimWithdrawal`).

The `initialize` function sets up roles and token addresses but never assigns `maxNumberOfWithdrawalsPerUser`: [1](#0-0) 

As a result, `maxNumberOfWithdrawalsPerUser` retains its Solidity default of `0`.

Inside `initiateWithdrawal`, the guard is: [2](#0-1) 

Because `userWithdrawalIds[msg.sender].length` is a `uint256` (always `>= 0`) and `maxNumberOfWithdrawalsPerUser == 0`, the condition `length >= 0` is unconditionally `true`. Every call to `initiateWithdrawal` reverts with `WithdrawalLimitReached` regardless of how many tokens the user has staked or how few withdrawals they have open.

The fix function exists but is never called during initialization: [3](#0-2) 

### Impact Explanation
All staked KERNEL tokens are frozen in the contract from deployment until an admin manually calls `setMaxNumberOfWithdrawalsPerUser`. Users who have staked cannot initiate the withdrawal step, making their tokens inaccessible for the entire window between deployment and admin remediation. If the admin key is lost, compromised, or simply delayed, the freeze extends indefinitely. This matches **Medium – Temporary freezing of funds**.

### Likelihood Explanation
The omission is automatic and requires no attacker action. Any user who stakes KERNEL tokens immediately after deployment and attempts to withdraw will be blocked. The likelihood is high because the broken state is the default post-deployment state, not an edge case.

### Recommendation
Initialize `maxNumberOfWithdrawalsPerUser` to a safe non-zero default (e.g., `MAX_WITHDRAWALS_PER_USER`) inside `initialize`:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    // ... existing setup ...
    maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // add this line
}
```

Alternatively, add a `require(maxNumberOfWithdrawalsPerUser > 0, ...)` guard at the top of `initiateWithdrawal` with a descriptive error to make the misconfiguration immediately obvious.

### Proof of Concept
1. Deploy `KernelDepositPool` via proxy and call `initialize(admin, kernelToken, rewardToken)`.
2. As a user, approve and call `stake(1e18)` — succeeds.
3. Call `initiateWithdrawal(1e18)` — reverts with `WithdrawalLimitReached` because `maxNumberOfWithdrawalsPerUser == 0` and `0 >= 0` is `true`.
4. Staked tokens are locked; `claimWithdrawal` is unreachable since no withdrawal record is ever created.
5. Only after admin calls `setMaxNumberOfWithdrawalsPerUser(N)` with `N > 0` does step 3 succeed. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L107-108)
```text
    /// @notice The maximum number of withdrawals that any user can have open (unclaimed) at any time
    uint256 public maxNumberOfWithdrawalsPerUser;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L610-620)
```text
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
```
