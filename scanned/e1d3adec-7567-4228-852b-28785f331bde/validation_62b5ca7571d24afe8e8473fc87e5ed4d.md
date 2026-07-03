### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks All Withdrawal Initiations Until Admin Intervention - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` never initializes `maxNumberOfWithdrawalsPerUser` in its `initialize()` function, leaving it at the Solidity default of `0`. The guard in `initiateWithdrawal` evaluates `0 >= 0 = true` and reverts for every caller, permanently freezing all staked KERNEL tokens until an admin manually calls `setMaxNumberOfWithdrawalsPerUser`.

### Finding Description
`KernelDepositPool.initialize()` sets `kernelToken`, `rewardsToken`, and access-control roles, but never assigns `maxNumberOfWithdrawalsPerUser`. [1](#0-0) 

The state variable therefore holds its zero default. Every call to `initiateWithdrawal` hits the following guard: [2](#0-1) 

Because `userWithdrawalIds[msg.sender].length` is `0` for any fresh caller, the condition `0 >= 0` is immediately `true` and the function reverts with `WithdrawalLimitReached`. No withdrawal can ever be initiated until the admin calls `setMaxNumberOfWithdrawalsPerUser` with a non-zero value.

The setter enforces `_maxNumberOfWithdrawalsPerUser != 0`, confirming that `0` is an invalid operational value, yet the initializer leaves the contract in exactly that invalid state: [3](#0-2) 

### Impact Explanation
Any user who has staked KERNEL tokens via `stake()` or `stakeFor()` cannot recover their principal until the admin intervenes. `stake()` accepts any non-zero amount with no minimum, so users can lock real value immediately after deployment. The staked balance is held inside the contract and the only exit path — `initiateWithdrawal` — is unconditionally blocked. This constitutes a **temporary freezing of funds** (Medium).

### Likelihood Explanation
The freeze is automatic and affects every user from the moment the contract is deployed. No attacker action is required; any honest user who stakes before the admin sets the limit will find their funds locked. The likelihood is **certain** for any deployment that does not call `setMaxNumberOfWithdrawalsPerUser` as an immediate post-deployment step.

### Recommendation
Initialize `maxNumberOfWithdrawalsPerUser` to a safe non-zero default (e.g., `MAX_WITHDRAWALS_PER_USER`) inside `initialize()`:

```solidity
maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER;
```

This mirrors how `LRTDepositPool` initializes its analogous limit: [4](#0-3) 

### Proof of Concept
1. Deploy `KernelDepositPool` and call `initialize(admin, kernelToken, rewardToken)`. Do **not** call `setMaxNumberOfWithdrawalsPerUser`.
2. Any user calls `stake(1e18)` — succeeds; `balanceOf[user] = 1e18`.
3. Same user calls `initiateWithdrawal(1e18)`.
4. Execution reaches `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser` → `0 >= 0` → `true` → reverts with `WithdrawalLimitReached`.
5. The user's `1e18` KERNEL is permanently inaccessible until the admin calls `setMaxNumberOfWithdrawalsPerUser(n)` where `n > 0`. [5](#0-4)

### Citations

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L610-619)
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
```

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
```
