### Title
`KernelDepositPool.initialize()` Fails to Set `withdrawalDelay` and `maxNumberOfWithdrawalsPerUser`, Causing Immediate Withdrawal Bypass and Temporary Fund Freeze - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.initialize()` sets only `kernelToken`, `rewardsToken`, and admin roles. It never initializes `withdrawalDelay` or `maxNumberOfWithdrawalsPerUser`, leaving both at their Solidity default of `0`. This produces two simultaneous broken invariants: (1) `maxNumberOfWithdrawalsPerUser == 0` causes every call to `initiateWithdrawal()` to revert with `WithdrawalLimitReached`, freezing all staked KERNEL tokens; and (2) `withdrawalDelay == 0` means that once the admin fixes (1), every withdrawal is claimable in the same block it is initiated, eliminating the intended time-lock entirely.

### Finding Description
`KernelDepositPool` is an upgradeable contract (OpenZeppelin `Initializable`, `_disableInitializers()` in constructor). Its sole initializer is:

```solidity
// contracts/KERNEL/KernelDepositPool.sol  line 259-271
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    UtilLib.checkNonZeroAddress(_admin);
    UtilLib.checkNonZeroAddress(_kernelToken);
    UtilLib.checkNonZeroAddress(_rewardToken);
    __AccessControl_init();
    __ReentrancyGuard_init();
    _setupRole(DEFAULT_ADMIN_ROLE, _admin);
    kernelToken  = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);
    // withdrawalDelay              ← never set, stays 0
    // maxNumberOfWithdrawalsPerUser ← never set, stays 0
}
```

`initiateWithdrawal()` contains two uses of these uninitialized values:

```solidity
// line 323
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser)
    revert WithdrawalLimitReached();          // 0 >= 0 → always reverts

// line 330
uint256 unlockTime = block.timestamp + withdrawalDelay;  // 0 → unlockTime == block.timestamp
```

And `claimWithdrawal()` checks:

```solidity
// line 355
if (block.timestamp < withdrawal.unlockTime) revert WithdrawalNotReady();
// block.timestamp < block.timestamp → false → passes immediately
```

**Effect 1 – Permanent withdrawal block (until admin intervenes):** Because `maxNumberOfWithdrawalsPerUser` is `0`, the guard `0 >= 0` is always `true`, so `initiateWithdrawal()` always reverts. No user can ever unstake KERNEL tokens.

**Effect 2 – Zero-delay withdrawals:** Once the admin calls `setMaxNumberOfWithdrawalsPerUser()`, `withdrawalDelay` is still `0`. Every withdrawal's `unlockTime` equals `block.timestamp` at initiation, so `claimWithdrawal()` can be called in the very same block, defeating the time-lock entirely.

The setter functions exist but are not called during initialization:

```solidity
// line 598-603
function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
    ...
    withdrawalDelay = _withdrawalDelay;
}

// line 610-619
function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
    external onlyRole(DEFAULT_ADMIN_ROLE) { ... }
```

There is no `reinitializer` function that sets these values, mirroring exactly the EigenLayer pattern where `withdrawalDelayBlocks` was moved to `DelegationManager` but had no path to be initialized on an already-live proxy.

### Impact Explanation
**Effect 1 (primary):** All KERNEL tokens staked via `stake()` or `stakeFor()` are immediately frozen. `initiateWithdrawal()` is the only exit path; with `maxNumberOfWithdrawalsPerUser == 0` it always reverts. Funds remain locked until the admin executes `setMaxNumberOfWithdrawalsPerUser()`. This is a **temporary freezing of funds** (Medium).

**Effect 2 (secondary):** After the admin fixes Effect 1, the zero `withdrawalDelay` means the time-lock provides no protection. A user can stake, initiate, and claim a withdrawal atomically within one block. This is **contract fails to deliver promised returns** (Low).

### Likelihood Explanation
The freeze is automatic and immediate upon deployment — no attacker action is required. Any user who stakes KERNEL tokens before the admin calls `setMaxNumberOfWithdrawalsPerUser()` is affected. The window between deployment and the admin setter call is the exposure window. Given that `initialize()` is called once at deployment and the setters are separate transactions, there is a realistic gap during which users can stake but cannot withdraw.

### Recommendation
Initialize both variables inside `initialize()` with safe non-zero defaults, or require them as constructor parameters:

```solidity
function initialize(
    address _admin,
    address _kernelToken,
    address _rewardToken,
    uint256 _withdrawalDelay,
    uint256 _maxNumberOfWithdrawalsPerUser
) external initializer {
    ...
    require(_withdrawalDelay > 0 && _withdrawalDelay <= MAX_WITHDRAWAL_DELAY, "bad delay");
    require(_maxNumberOfWithdrawalsPerUser > 0 && _maxNumberOfWithdrawalsPerUser <= MAX_WITHDRAWALS_PER_USER, "bad max");
    withdrawalDelay = _withdrawalDelay;
    maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
}
```

This mirrors the EigenLayer resolution: the variable must be set at initialization time, not left to a post-deployment admin call.

### Proof of Concept

1. Admin deploys `KernelDepositPool` proxy and calls `initialize(admin, kernelToken, rewardToken)`.
2. `withdrawalDelay = 0`, `maxNumberOfWithdrawalsPerUser = 0` (Solidity defaults).
3. Alice calls `stake(1000e18)` — succeeds; `balanceOf[Alice] = 1000e18`.
4. Alice calls `initiateWithdrawal(1000e18)`:
   - Guard: `userWithdrawalIds[Alice].length` is `0`; `maxNumberOfWithdrawalsPerUser` is `0`; `0 >= 0` → `revert WithdrawalLimitReached()`.
5. Alice's 1000 KERNEL are frozen with no exit path until admin calls `setMaxNumberOfWithdrawalsPerUser(n)`.
6. After admin fixes (5), Alice calls `initiateWithdrawal(1000e18)` — succeeds; `unlockTime = block.timestamp + 0 = block.timestamp`.
7. In the same block, Alice calls `claimWithdrawal(id)`:
   - Guard: `block.timestamp < block.timestamp` → `false` → passes.
   - Alice receives 1000 KERNEL immediately, with zero delay enforced. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L95-108)
```text
    /// @notice Delay (in seconds) before withdrawals can be claimed after initiation
    uint256 public withdrawalDelay;

    /// @notice A global incremental counter for withdrawal IDs
    uint256 public withdrawalCounter;

    /// @notice Mapping of withdrawal IDs to their withdrawal info
    mapping(uint256 withdrawalId => Withdrawal withdrawal) public withdrawals;

    /// @notice Mapping of user addresses to their withdrawal IDs
    mapping(address user => uint256[] withdrawalIds) public userWithdrawalIds;

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L344-357)
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
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L598-619)
```text
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
```
