### Title
O(N) Storage Array Scan in `claimWithdrawal` Causes Unbounded Gas Growth - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.claimWithdrawal` performs a linear scan over the caller's `userWithdrawalIds` storage array to locate and remove the claimed entry. Every call reads up to `maxNumberOfWithdrawalsPerUser` storage slots, mirroring the exact gas-greedy queue-removal pattern from the reference report.

### Finding Description
In `claimWithdrawal`, after marking a withdrawal as claimed, the contract removes the corresponding ID from the user's storage array via a full linear scan:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L366-373
uint256[] storage userWithdrawalIdsArray = userWithdrawalIds[msg.sender];
for (uint256 i = 0; i < userWithdrawalIdsArray.length; ++i) {
    if (userWithdrawalIdsArray[i] == _withdrawalId) {
        userWithdrawalIdsArray[i] = userWithdrawalIdsArray[userWithdrawalIdsArray.length - 1];
        userWithdrawalIdsArray.pop();
        break;
    }
}
``` [1](#0-0) 

`userWithdrawalIds` is declared as a plain dynamic array in storage:

```solidity
mapping(address user => uint256[] withdrawalIds) public userWithdrawalIds;
``` [2](#0-1) 

The cap on array length is enforced by the state variable `maxNumberOfWithdrawalsPerUser`, not the constant `MAX_WITHDRAWALS_PER_USER = 100`:

```solidity
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
``` [3](#0-2) 

The constant `MAX_WITHDRAWALS_PER_USER = 100` is defined but is not used in the guard — only the mutable state variable `maxNumberOfWithdrawalsPerUser` is checked: [4](#0-3) 

Additionally, `initialize` never sets `maxNumberOfWithdrawalsPerUser`, so it defaults to `0` until an admin explicitly configures it: [5](#0-4) 

### Impact Explanation
Each call to `claimWithdrawal` performs up to N cold `SLOAD` operations (~2,100 gas each) over the storage array. At `maxNumberOfWithdrawalsPerUser = 100`, that is ~210,000 gas in reads alone before any writes. If the admin setter for `maxNumberOfWithdrawalsPerUser` does not enforce the `MAX_WITHDRAWALS_PER_USER = 100` constant as a hard ceiling, the loop becomes effectively unbounded and a user with a sufficiently large array could find `claimWithdrawal` reverting due to out-of-gas, permanently freezing their KERNEL tokens in the contract.

**Impact: Medium — Unbounded gas consumption / potential temporary or permanent fund freeze.**

### Likelihood Explanation
Any unprivileged user can call `initiateWithdrawal` repeatedly (up to the configured limit) to grow their `userWithdrawalIds` array, then call `claimWithdrawal`. No special role or external dependency is required. The entry path is fully self-contained and permissionless.

### Recommendation
Replace the `uint256[]` storage array with a mapping-based structure that supports O(1) removal without scanning. The codebase already contains `DoubleEndedQueue.Uint256Deque` (used in `LRTWithdrawalManager`) which uses monotonically increasing `_begin`/`_end` indices — exactly the pattern recommended in the reference report: [6](#0-5) 

Alternatively, maintain a `mapping(uint256 withdrawalId => uint256 arrayIndex)` alongside the array to enable O(1) lookup and swap-and-pop without scanning.

### Proof of Concept
1. User calls `initiateWithdrawal(1)` N times (up to `maxNumberOfWithdrawalsPerUser`), building `userWithdrawalIds[user]` to length N.
2. After the withdrawal delay passes, user calls `claimWithdrawal(withdrawalIds[0])` — the first ID pushed.
3. The loop at L367 scans all N entries before finding the match at index 0 (worst case: target is at the end).
4. Gas cost scales as O(N) storage reads. At large N (if the admin-settable cap is raised beyond 100), the transaction can exceed the block gas limit, making the user's funds permanently unclaimable. [7](#0-6)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L38-38)
```text
    uint256 public constant MAX_WITHDRAWALS_PER_USER = 100;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L104-105)
```text
    /// @notice Mapping of user addresses to their withdrawal IDs
    mapping(address user => uint256[] withdrawalIds) public userWithdrawalIds;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L323-323)
```text
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L344-379)
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

        if (withdrawal.claimed) {
            revert WithdrawalAlreadyClaimed();
        }

        withdrawal.claimed = true;

        // Remove the withdrawal ID from the user's list of withdrawal IDs
        uint256[] storage userWithdrawalIdsArray = userWithdrawalIds[msg.sender];
        for (uint256 i = 0; i < userWithdrawalIdsArray.length; ++i) {
            if (userWithdrawalIdsArray[i] == _withdrawalId) {
                userWithdrawalIdsArray[i] = userWithdrawalIdsArray[userWithdrawalIdsArray.length - 1];
                userWithdrawalIdsArray.pop();
                break;
            }
        }

        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

        emit WithdrawalClaimed(msg.sender, withdrawal.amount, _withdrawalId);
    }
```

**File:** contracts/utils/DoubleEndedQueue.sol (L42-46)
```text
    struct Uint256Deque {
        uint128 _begin;
        uint128 _end;
        mapping(uint128 index => uint256) _data;
    }
```
