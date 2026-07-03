Audit Report

## Title
`maxNumberOfWithdrawalsPerUser` Uninitialized in `initialize()` Permanently Blocks All Withdrawals - (File: `contracts/KERNEL/KernelDepositPool.sol`)

## Summary
`KernelDepositPool.initialize()` never assigns `maxNumberOfWithdrawalsPerUser`, leaving it at the Solidity default of `0`. Because `initiateWithdrawal()` guards with `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, the condition `0 >= 0` is immediately and unconditionally true for every caller, causing every withdrawal attempt to revert with `WithdrawalLimitReached`. Any user who stakes before an admin calls `setMaxNumberOfWithdrawalsPerUser()` has their KERNEL tokens frozen with no alternative exit path.

## Finding Description
`maxNumberOfWithdrawalsPerUser` is declared as a plain storage variable with no inline default: [1](#0-0) 

`initialize()` sets only `kernelToken`, `rewardsToken`, and the admin role — it never touches `maxNumberOfWithdrawalsPerUser`: [2](#0-1) 

`initiateWithdrawal()` enforces the limit as its third guard, before any state is mutated: [3](#0-2) 

With `maxNumberOfWithdrawalsPerUser == 0`, the expression `userWithdrawalIds[msg.sender].length >= 0` evaluates to `true` for every address — including fresh ones with zero open withdrawals — so the function always reverts. `stake()` accepts tokens freely with no preconditions beyond a non-zero amount: [4](#0-3) 

There is no alternative withdrawal function in the contract. The only remedy is an admin call to `setMaxNumberOfWithdrawalsPerUser()`, which additionally enforces that the value is non-zero: [5](#0-4) 

## Impact Explanation
**Critical — Permanent freezing of funds.** Every KERNEL token deposited via `stake()` or `stakeFor()` before the admin sets the limit is irrecoverable through any user-accessible path. There is no emergency exit, no direct `withdraw()`, and no bypass of the `initiateWithdrawal` guard. The freeze persists indefinitely until an admin acts; if the admin key is lost or the admin never acts, the freeze is truly permanent. [6](#0-5) 

## Likelihood Explanation
**High.** The contract is immediately usable after deployment — `stake()` imposes no preconditions beyond a non-zero amount. Any user who stakes in the window between deployment and the admin's configuration call has their funds frozen. Because `initialize()` is the canonical and only setup entry point and it omits this field, the freeze is the default state of every fresh deployment. No attacker action is required; the broken state is self-inflicted by the contract's own initialization logic. [2](#0-1) 

## Recommendation
Set `maxNumberOfWithdrawalsPerUser` to a safe non-zero default inside `initialize()`, using the already-defined constant `MAX_WITHDRAWALS_PER_USER` (100), so the contract is never deployed in a state where withdrawals are impossible:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    UtilLib.checkNonZeroAddress(_admin);
    UtilLib.checkNonZeroAddress(_kernelToken);
    UtilLib.checkNonZeroAddress(_rewardToken);

    __AccessControl_init();
    __ReentrancyGuard_init();

    _setupRole(DEFAULT_ADMIN_ROLE, _admin);

    kernelToken = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);

    maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // add this line
}
``` [7](#0-6) 

## Proof of Concept
```solidity
// 1. Deploy KernelDepositPool; initialize() is called — maxNumberOfWithdrawalsPerUser == 0
// 2. User approves and stakes
kernelToken.approve(address(pool), 1e18);
pool.stake(1e18);                        // succeeds — tokens transferred in

// 3. User tries to withdraw
pool.initiateWithdrawal(1e18);
// REVERTS: WithdrawalLimitReached()
// Reason: userWithdrawalIds[user].length (0) >= maxNumberOfWithdrawalsPerUser (0) → true

// 4. No other withdrawal function exists; funds are frozen until admin acts.
```

Foundry test plan: deploy the contract, call `initialize()`, have a test address approve and call `stake(1e18)`, then assert that `initiateWithdrawal(1e18)` reverts with `WithdrawalLimitReached`. Confirm that after admin calls `setMaxNumberOfWithdrawalsPerUser(10)`, the same `initiateWithdrawal` call succeeds. [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L38-38)
```text
    uint256 public constant MAX_WITHDRAWALS_PER_USER = 100;
```

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
