The code confirms all claims. `initialize()` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at `0`. The check `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser` evaluates to `0 >= 0 = true` for every fresh caller, causing `initiateWithdrawal()` to always revert. `stake()` has no corresponding guard. The only remedy is an admin call to `setMaxNumberOfWithdrawalsPerUser()`. This is not an admin-only attack — it is triggered by normal user staking behavior in the default deployment state.

---

Audit Report

## Title
`maxNumberOfWithdrawalsPerUser` Uninitialized in `initialize()` Permanently Freezes All Staked Funds - (File: `contracts/KERNEL/KernelDepositPool.sol`)

## Summary
`KernelDepositPool.initialize()` never assigns `maxNumberOfWithdrawalsPerUser`, leaving it at the Solidity default of `0`. Because `initiateWithdrawal()` reverts when `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, the condition `0 >= 0` is immediately true for every caller, making withdrawals impossible until an admin manually calls `setMaxNumberOfWithdrawalsPerUser()`. Any user who stakes before that admin call has their tokens permanently frozen with no alternative exit path.

## Finding Description
`maxNumberOfWithdrawalsPerUser` is declared as a plain storage `uint256` with no inline default: [1](#0-0) 

`initialize()` sets only `kernelToken`, `rewardsToken`, and the admin role — it never touches `maxNumberOfWithdrawalsPerUser`: [2](#0-1) 

`initiateWithdrawal()` enforces the limit as its third guard: [3](#0-2) 

With `maxNumberOfWithdrawalsPerUser == 0`, `userWithdrawalIds[msg.sender].length` (which is `0` for any fresh address) satisfies `0 >= 0`, so the function always reverts with `WithdrawalLimitReached`. Meanwhile, `stake()` imposes no such guard and accepts tokens freely: [4](#0-3) 

The sole remedy is an admin call to `setMaxNumberOfWithdrawalsPerUser()`, which enforces `_maxNumberOfWithdrawalsPerUser != 0`: [5](#0-4) 

There is no direct `withdraw()`, no emergency exit, and no bypass of the `initiateWithdrawal` guard anywhere in the contract.

## Impact Explanation
**Critical — Permanent freezing of funds.** Every KERNEL token deposited via `stake()` or `stakeFor()` before the admin configures the limit is irrecoverable through any user-accessible path. The impact matches the allowed scope exactly: permanent freezing of funds.

## Likelihood Explanation
**High.** `initialize()` is the canonical and only setup entry point. The frozen state is the default state of every fresh deployment. `stake()` imposes no preconditions beyond a non-zero amount, so any user who interacts with the contract in the window between deployment and the admin's configuration call will have their funds frozen. No attacker capability is required — ordinary user behavior triggers the freeze.

## Recommendation
Set `maxNumberOfWithdrawalsPerUser` to a safe non-zero default inside `initialize()`:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    // ... existing checks and setup ...
    maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // 100
}
```

This ensures the contract is never deployed in a state where withdrawals are impossible.

## Proof of Concept
```solidity
// 1. Deploy KernelDepositPool; initialize() is called — maxNumberOfWithdrawalsPerUser == 0

// 2. User stakes
kernelToken.approve(address(pool), 1e18);
pool.stake(1e18); // succeeds — no guard on maxNumberOfWithdrawalsPerUser

// 3. User attempts to withdraw
pool.initiateWithdrawal(1e18);
// REVERTS: WithdrawalLimitReached()
// userWithdrawalIds[user].length == 0, maxNumberOfWithdrawalsPerUser == 0
// 0 >= 0 → true → revert

// 4. No other withdrawal function exists; funds are permanently frozen.
// Admin has not yet called setMaxNumberOfWithdrawalsPerUser().
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L323-323)
```text
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
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
