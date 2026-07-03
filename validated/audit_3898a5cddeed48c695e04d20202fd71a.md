### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks All Withdrawals Until Admin Intervention - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary

`KernelDepositPool.initialize()` does not set `maxNumberOfWithdrawalsPerUser`, leaving it at its default value of `0`. Because `initiateWithdrawal()` guards with `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, and `0 >= 0` is always true, every withdrawal attempt reverts with `WithdrawalLimitReached` from the moment of deployment until an admin explicitly calls `setMaxNumberOfWithdrawalsPerUser`. Users who stake KERNEL tokens immediately after deployment have their funds temporarily frozen with no self-service remedy.

### Finding Description

`KernelDepositPool.initialize()` sets only `kernelToken`, `rewardsToken`, and the admin role. It does not initialize `maxNumberOfWithdrawalsPerUser`:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    // ...
    _setupRole(DEFAULT_ADMIN_ROLE, _admin);
    kernelToken = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);
    // maxNumberOfWithdrawalsPerUser is NOT set → defaults to 0
}
```

The withdrawal guard in `initiateWithdrawal()` is:

```solidity
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

With `maxNumberOfWithdrawalsPerUser == 0`, the condition `0 >= 0` evaluates to `true` for every caller, causing every call to `initiateWithdrawal()` to revert. There is no alternative unstake path in the contract. The only remedy is an admin call to `setMaxNumberOfWithdrawalsPerUser`, which validates `_maxNumberOfWithdrawalsPerUser == 0` as invalid and therefore cannot be used to restore the zero state once fixed.

### Impact Explanation

Any user who calls `stake()` before the admin sets `maxNumberOfWithdrawalsPerUser` has their KERNEL tokens locked in the contract with no self-service exit. This constitutes a **temporary freezing of funds** (Medium severity per the allowed scope). The freeze persists for an indeterminate period — from deployment until admin action — and is especially harmful during the early high-activity period immediately after launch, when users are most likely to stake and may also need to exit.

### Likelihood Explanation

**High.** This condition is present on every fresh deployment of `KernelDepositPool`. The `initialize()` function is the sole initialization path and it structurally omits the parameter. Any user who stakes before the admin completes post-deployment configuration is affected. No on-chain warning or guard prevents staking while withdrawals are blocked.

### Recommendation

Set a safe non-zero default for `maxNumberOfWithdrawalsPerUser` inside `initialize()`, for example:

```solidity
maxNumberOfWithdrawalsPerUser = 10; // or any reasonable default ≤ MAX_WITHDRAWALS_PER_USER
```

Alternatively, accept `maxNumberOfWithdrawalsPerUser` as an `initialize()` parameter and validate it is non-zero before storing it.

### Proof of Concept

1. Admin deploys and calls `KernelDepositPool.initialize(admin, kernelToken, rewardToken)`.
2. `maxNumberOfWithdrawalsPerUser` is `0` (Solidity default).
3. Alice calls `stake(100e18)` — succeeds; her balance is recorded.
4. Alice calls `initiateWithdrawal(100e18)`:
   - Check: `userWithdrawalIds[Alice].length >= maxNumberOfWithdrawalsPerUser` → `0 >= 0` → `true`
   - Reverts with `WithdrawalLimitReached`.
5. Alice's 100e18 KERNEL tokens remain locked in the contract.
6. No other withdrawal function exists. Alice must wait for admin to call `setMaxNumberOfWithdrawalsPerUser(N)`.

Relevant code references: [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-323)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
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
