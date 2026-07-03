### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks All Withdrawal Initiations Until Admin Intervenes - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.initialize()` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at its default value of `0`. Because `initiateWithdrawal` guards with `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, and any `uint256` length is always `>= 0`, every call to `initiateWithdrawal` reverts with `WithdrawalLimitReached` until an admin separately calls `setMaxNumberOfWithdrawalsPerUser`. Any KERNEL tokens staked before that admin action are temporarily frozen.

### Finding Description
`KernelDepositPool.initialize()` sets `kernelToken`, `rewardsToken`, and the admin role, but leaves `maxNumberOfWithdrawalsPerUser` at its Solidity default of `0`. [1](#0-0) 

The withdrawal guard in `initiateWithdrawal` is:

```solidity
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
``` [2](#0-1) 

Because `maxNumberOfWithdrawalsPerUser == 0` and `uint256` array `.length` is always `>= 0`, this condition is unconditionally `true`. Every call to `initiateWithdrawal` reverts, regardless of how much the user has staked.

The setter that could fix this is:

```solidity
function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
    external onlyRole(DEFAULT_ADMIN_ROLE) { ... }
``` [3](#0-2) 

Notably, `setMaxNumberOfWithdrawalsPerUser` itself rejects `0` as an argument (`if (_maxNumberOfWithdrawalsPerUser == 0 || ...) revert`), confirming that `0` is an invalid operational value — yet `initialize()` leaves the variable at exactly that invalid value. [4](#0-3) 

### Impact Explanation
Any user who calls `stake()` or is staked via `stakeFor()` before the admin calls `setMaxNumberOfWithdrawalsPerUser` has their KERNEL tokens temporarily frozen: `initiateWithdrawal` always reverts, so the tokens cannot be queued for return. The freeze lasts until the admin notices and calls the setter. This matches the **Medium — Temporary freezing of funds** impact category.

### Likelihood Explanation
The contract is deployable and immediately open for staking (`stake()` has no admin-gating). A user can stake in the same block as deployment. If the admin does not call `setMaxNumberOfWithdrawalsPerUser` atomically in the same deployment transaction, a window exists — potentially indefinitely — during which all withdrawal initiations revert. The likelihood is **Medium**: the deployment sequence is not enforced on-chain, and the missing initialization is not surfaced by any revert or event.

### Recommendation
Initialize `maxNumberOfWithdrawalsPerUser` to a safe non-zero default inside `initialize()`, for example:

```solidity
maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // 100
```

This mirrors the pattern used for `maxNodeDelegatorLimit` in `LRTDepositPool.initialize()`, which is set to `10` directly in the initializer. [5](#0-4) 

### Proof of Concept
1. Admin deploys `KernelDepositPool` and calls `initialize(admin, kernelToken, rewardToken)`. `maxNumberOfWithdrawalsPerUser` is `0`.
2. User calls `stake(1e18)`. Succeeds — `balanceOf[user] = 1e18`, `totalKernelStaked = 1e18`.
3. User calls `initiateWithdrawal(1e18)`.
   - `_amount == 0` → false
   - `balanceOf[msg.sender] < _amount` → false
   - `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser` → `0 >= 0` → **true** → reverts `WithdrawalLimitReached`
4. User's `1e18` KERNEL is locked in the contract with no path to recovery until admin calls `setMaxNumberOfWithdrawalsPerUser(n)` where `n > 0`. [6](#0-5)

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

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
```
