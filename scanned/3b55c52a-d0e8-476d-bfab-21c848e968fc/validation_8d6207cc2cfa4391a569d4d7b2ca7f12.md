Looking at the code, the vulnerability claim is concrete and verifiable. Let me confirm the key facts:

1. `initialize` does **not** set `maxNumberOfWithdrawalsPerUser` — it only sets `kernelToken`, `rewardsToken`, and the admin role. [1](#0-0) 

2. `maxNumberOfWithdrawalsPerUser` is a plain storage variable that defaults to `0` in Solidity. [2](#0-1) 

3. `initiateWithdrawal` checks `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser` — with both sides at `0`, this is `0 >= 0 = true`, so it **always** reverts with `WithdrawalLimitReached`. [3](#0-2) 

4. `setMaxNumberOfWithdrawalsPerUser` explicitly rejects `0` as invalid, confirming the designers knew `0` is a broken value — yet `initialize` never sets it. [4](#0-3) 

5. `stake` has no such guard, so users can deposit tokens into a contract from which they cannot withdraw. [5](#0-4) 

This is a real, locally-testable bug — not an admin-compromise scenario. The admin doesn't need to be malicious; they simply need to omit one post-deploy call. The contract's own validation (`setMaxNumberOfWithdrawalsPerUser` rejecting `0`) proves `0` is an invalid operational value, yet the contract starts in that state.

---

### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks All Withdrawals Until Admin Intervenes — (`contracts/KERNEL/KernelDepositPool.sol`)

### Summary
`KernelDepositPool.initialize` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at the Solidity default of `0`. The guard in `initiateWithdrawal` evaluates `0 >= 0 = true` and reverts with `WithdrawalLimitReached` for every caller, freezing all staked KERNEL tokens until the admin calls `setMaxNumberOfWithdrawalsPerUser`.

### Finding Description
`maxNumberOfWithdrawalsPerUser` is declared as a storage variable with no default value assignment:

```solidity
// KernelDepositPool.sol line 108
uint256 public maxNumberOfWithdrawalsPerUser;
```

The `initialize` function sets `kernelToken`, `rewardsToken`, and the admin role, but never sets `maxNumberOfWithdrawalsPerUser`. It therefore starts at `0`.

`initiateWithdrawal` contains:

```solidity
// line 323
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

For any fresh user, `userWithdrawalIds[msg.sender].length == 0` and `maxNumberOfWithdrawalsPerUser == 0`, so `0 >= 0` is always `true`. Every call to `initiateWithdrawal` reverts immediately, regardless of staked balance.

The setter `setMaxNumberOfWithdrawalsPerUser` explicitly rejects `0`:

```solidity
// line 614
if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
    revert InvalidMaxNumberOfWithdrawalsPerUser();
}
```

This confirms the protocol treats `0` as an invalid value, yet the contract is deployed in that invalid state.

### Impact Explanation
All staked KERNEL tokens are frozen from the moment of deployment until the admin calls `setMaxNumberOfWithdrawalsPerUser` with a value ≥ 1. Users can stake freely (no analogous guard in `stake`) but cannot initiate any withdrawal. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation
The likelihood is moderate-to-high. The `initialize` function is the sole deployment entry point and contains no reminder or requirement to set this parameter. Any deployment that omits the post-init `setMaxNumberOfWithdrawalsPerUser` call — whether by oversight, incomplete deployment script, or rushed launch — results in a fully broken withdrawal path. The bug is silent: staking succeeds, but withdrawals fail with a misleading "limit reached" error even for a user with zero pending withdrawals.

### Recommendation
Set `maxNumberOfWithdrawalsPerUser` to a safe default inside `initialize`, or add it as a required constructor/initializer parameter:

```solidity
function initialize(
    address _admin,
    address _kernelToken,
    address _rewardToken,
    uint256 _maxNumberOfWithdrawalsPerUser  // add this
) external initializer {
    // ... existing checks ...
    if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
        revert InvalidMaxNumberOfWithdrawalsPerUser();
    }
    maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
}
```

Alternatively, initialize it inline to `MAX_WITHDRAWALS_PER_USER` (100) as a safe default.

### Proof of Concept
```solidity
// Local fork / unit test — no mainnet required
function testWithdrawalBlockedByDefault() public {
    // Deploy and initialize (no setMaxNumberOfWithdrawalsPerUser call)
    KernelDepositPool pool = new KernelDepositPool();
    pool.initialize(admin, address(kernelToken), address(rewardToken));

    // User stakes 1e18 KERNEL
    vm.startPrank(user);
    kernelToken.approve(address(pool), 1e18);
    pool.stake(1e18);

    // initiateWithdrawal reverts — 0 >= 0 triggers WithdrawalLimitReached
    vm.expectRevert(KernelDepositPool.WithdrawalLimitReached.selector);
    pool.initiateWithdrawal(1e18);
    vm.stopPrank();

    // Admin fixes it
    vm.prank(admin);
    pool.setMaxNumberOfWithdrawalsPerUser(10);

    // Now withdrawal succeeds
    vm.prank(user);
    pool.initiateWithdrawal(1e18); // no revert
}
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L614-616)
```text
        if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
            revert InvalidMaxNumberOfWithdrawalsPerUser();
        }
```
