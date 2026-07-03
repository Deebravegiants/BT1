### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks All Withdrawals Until Admin Intervenes - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.sol`'s `initialize()` function never sets `maxNumberOfWithdrawalsPerUser`, leaving it at its Solidity default of `0`. The guard in `initiateWithdrawal()` immediately evaluates `0 >= 0` as `true` and reverts with `WithdrawalLimitReached()` for every caller, freezing all staked KERNEL tokens until an admin separately calls `setMaxNumberOfWithdrawalsPerUser`.

### Finding Description
The state variable `maxNumberOfWithdrawalsPerUser` is declared but never assigned in `initialize()`:

```solidity
// initialize() — lines 259-271
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    // ...
    kernelToken = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);
    // maxNumberOfWithdrawalsPerUser is never set → defaults to 0
}
```

`initiateWithdrawal()` enforces a cap on open withdrawals per user:

```solidity
// line 323
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

Because `maxNumberOfWithdrawalsPerUser == 0` and `userWithdrawalIds[msg.sender].length` starts at `0`, the condition `0 >= 0` is always `true` from the very first call. Every invocation of `initiateWithdrawal()` reverts, regardless of how many KERNEL tokens the user has staked.

A secondary uninitialized variable, `withdrawalDelay`, also defaults to `0`, meaning that once the admin does set `maxNumberOfWithdrawalsPerUser`, all withdrawals become immediately claimable with no enforced delay — bypassing the intended time-lock protection. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
Any user who calls `stake()` and then attempts `initiateWithdrawal()` will be permanently blocked until an admin calls `setMaxNumberOfWithdrawalsPerUser`. Their staked KERNEL tokens are locked in the contract with no exit path. This constitutes a **temporary freezing of funds** for all stakers. The secondary `withdrawalDelay = 0` issue means the intended delay protection is also absent until separately configured. [4](#0-3) [5](#0-4) 

### Likelihood Explanation
This is triggered by any user who stakes KERNEL tokens and then tries to withdraw — a core, expected user flow. The condition is active from the moment the contract is deployed and initialized, requiring zero attacker sophistication. It affects 100% of stakers until an admin intervenes. The admin setter `setMaxNumberOfWithdrawalsPerUser` explicitly rejects `0` as a value, confirming the intent was always to have a non-zero limit, yet the initializer never enforces this. [6](#0-5) 

### Recommendation
Initialize both `maxNumberOfWithdrawalsPerUser` and `withdrawalDelay` to safe non-zero values inside `initialize()`, mirroring the pattern used by `KernelVaultETH.sol` which validates and sets `_minDeposit` at initialization time:

```solidity
function initialize(
    address _admin,
    address _kernelToken,
    address _rewardToken,
    uint256 _withdrawalDelay,
    uint256 _maxNumberOfWithdrawalsPerUser
) external initializer {
    // existing checks ...
    if (_withdrawalDelay == 0 || _withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert InvalidWithdrawalDelay();
    if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER)
        revert InvalidMaxNumberOfWithdrawalsPerUser();

    withdrawalDelay = _withdrawalDelay;
    maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
    // ...
}
``` [7](#0-6) 

### Proof of Concept
```solidity
function test_KernelDepositPool_WithdrawalBlocked_UninitializedMax() public {
    // Assume contract is freshly initialized (maxNumberOfWithdrawalsPerUser == 0)
    vm.startPrank(user);
    kernelToken.approve(address(kernelDepositPool), 1 ether);
    kernelDepositPool.stake(1 ether);

    // Any attempt to withdraw immediately reverts
    vm.expectRevert(KernelDepositPool.WithdrawalLimitReached.selector);
    kernelDepositPool.initiateWithdrawal(1 ether);
    // User's 1 ether is now locked with no exit path
    vm.stopPrank();
}
```

The check `userWithdrawalIds[msg.sender].length (0) >= maxNumberOfWithdrawalsPerUser (0)` evaluates to `true`, reverting every call to `initiateWithdrawal` until an admin sets a non-zero limit. [8](#0-7)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L96-108)
```text
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L598-603)
```text
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
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

**File:** contracts/KERNEL/KernelVaultETH.sol (L144-168)
```text
    function initialize(
        address _admin,
        address _operator,
        address _kernel,
        address _kernelOftAdapter,
        uint32 _dstLzChainId,
        address _receiver,
        uint256 _minDeposit
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_operator);
        UtilLib.checkNonZeroAddress(_kernel);
        UtilLib.checkNonZeroAddress(_kernelOftAdapter);
        UtilLib.checkNonZeroAddress(_receiver);

        if (_dstLzChainId == 0) {
            revert InvalidLzChainId();
        }

        if (_minDeposit == 0) {
            revert InvalidMinDeposit();
        }
```
