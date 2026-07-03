### Title
`maxNumberOfWithdrawalsPerUser` Not Set on `KernelDepositPool` Initialization, Permanently Blocking `initiateWithdrawal()` Until Admin Intervenes - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.initialize()` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at its default value of `0`. Because `initiateWithdrawal()` enforces a limit check against this variable, every call to `initiateWithdrawal()` reverts immediately after deployment, freezing all staked KERNEL tokens until an admin manually calls `setMaxNumberOfWithdrawalsPerUser()`.

### Finding Description
`KernelDepositPool` declares `maxNumberOfWithdrawalsPerUser` as a storage variable with no default assignment: [1](#0-0) 

The `initialize()` function sets only `kernelToken` and `rewardsToken`, leaving `maxNumberOfWithdrawalsPerUser` at `0`: [2](#0-1) 

The `initiateWithdrawal()` function enforces:

```solidity
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

Because `maxNumberOfWithdrawalsPerUser == 0` after initialization, the condition `0 >= 0` is always `true`, so every call to `initiateWithdrawal()` reverts with `WithdrawalLimitReached` from the moment the contract is deployed.

The setter `setMaxNumberOfWithdrawalsPerUser()` explicitly rejects `0` as an invalid value, confirming that `0` is not a valid operational state: [3](#0-2) 

### Impact Explanation
Any user who has staked KERNEL tokens via `stake()` or `stakeFor()` cannot initiate a withdrawal until an admin calls `setMaxNumberOfWithdrawalsPerUser()`. Staked KERNEL tokens are temporarily frozen — users cannot begin the unlock process at all. This matches **Medium — Temporary freezing of funds**. [4](#0-3) 

### Likelihood Explanation
This is triggered deterministically on every deployment of the contract before the admin calls the setter. Any user who stakes KERNEL tokens and then attempts to withdraw will hit the revert. No special conditions or attacker actions are required — the broken state is the default post-initialization state. Likelihood is **High**.

### Recommendation
Set `maxNumberOfWithdrawalsPerUser` to a valid non-zero value (e.g., `MAX_WITHDRAWALS_PER_USER`) inside `initialize()`:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    // ... existing checks ...
    kernelToken = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);
    maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // add this
}
``` [2](#0-1) 

### Proof of Concept

1. Admin deploys `KernelDepositPool` proxy and calls `initialize(admin, kernelToken, rewardToken)`.
2. `maxNumberOfWithdrawalsPerUser` is `0` (never set).
3. User calls `stake(100e18)` — succeeds, KERNEL tokens are transferred in.
4. User calls `initiateWithdrawal(100e18)`:
   - Check: `userWithdrawalIds[user].length >= maxNumberOfWithdrawalsPerUser` → `0 >= 0` → `true`
   - Reverts with `WithdrawalLimitReached`.
5. User's KERNEL tokens are locked in the contract with no path to withdrawal until admin calls `setMaxNumberOfWithdrawalsPerUser(N)`. [5](#0-4)

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
