### Title
`initiateWithdrawal()` Always Reverts When `maxNumberOfWithdrawalsPerUser` Is Uninitialized — (`File: contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.initiateWithdrawal()` contains a withdrawal-limit guard that compares `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`. Because `maxNumberOfWithdrawalsPerUser` is never set in `initialize()`, it defaults to `0`. Any `uint256` length value satisfies `>= 0`, so the guard **always** reverts with `WithdrawalLimitReached`, permanently blocking every staker from initiating a withdrawal until an admin manually calls `setMaxNumberOfWithdrawalsPerUser()`.

---

### Finding Description

`initialize()` sets `kernelToken`, `rewardsToken`, and roles, but never assigns `maxNumberOfWithdrawalsPerUser`: [1](#0-0) 

The variable therefore holds its Solidity default of `0`. Inside `initiateWithdrawal()`: [2](#0-1) 

The guard is:

```solidity
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

With `maxNumberOfWithdrawalsPerUser == 0`, the condition reduces to `length >= 0`, which is unconditionally `true` for every `uint256`. Every call to `initiateWithdrawal()` reverts immediately, regardless of how much the user has staked.

The setter enforces a non-zero value, so the admin cannot accidentally leave it at zero after calling the setter — but the setter is never called during initialization: [3](#0-2) 

This is structurally identical to the reference bug: a guard that uses a zero-sentinel value (`end == 0` for perpetual locks; `maxNumberOfWithdrawalsPerUser == 0` for the uninitialized pool) causes a legitimate operation to be unconditionally blocked for an entire class of users.

---

### Impact Explanation

Every user who has staked KERNEL tokens via `stake()` or `stakeFor()` is unable to call `initiateWithdrawal()`. Their staked principal is locked in the contract with no exit path until an admin intervenes. This constitutes **temporary freezing of funds** (Medium). [4](#0-3) 

---

### Likelihood Explanation

Medium. The contract is upgradeable and the `initialize()` function is the sole setup entry point. There is no in-code enforcement that `setMaxNumberOfWithdrawalsPerUser()` must be called before staking opens. Any deployment that omits this post-init step — including upgrades that re-initialize — leaves the pool in the broken state. Users can stake immediately after deployment, but cannot withdraw.

---

### Recommendation

Initialize `maxNumberOfWithdrawalsPerUser` to a safe non-zero default inside `initialize()`:

```diff
 function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
     ...
+    maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER;
 }
```

---

### Proof of Concept

1. Deploy `KernelDepositPool` and call `initialize(admin, kernelToken, rewardToken)` — do **not** call `setMaxNumberOfWithdrawalsPerUser()`.
2. User approves and calls `stake(100e18)`. Succeeds; `balanceOf[user] == 100e18`.
3. User calls `initiateWithdrawal(100e18)`.
4. Execution reaches:
   ```solidity
   if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser)
       revert WithdrawalLimitReached();
   // 0 >= 0 → true → always reverts
   ```
5. Transaction reverts with `WithdrawalLimitReached`. User's 100 KERNEL are frozen.
6. Admin calls `setMaxNumberOfWithdrawalsPerUser(10)`. Step 3 now succeeds. [5](#0-4)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-288)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
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
