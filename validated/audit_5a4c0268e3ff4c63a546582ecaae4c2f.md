### Title
Anyone Can Bypass `NodeDelegator::completeUnstaking()` Accounting by Calling EigenLayer's `DelegationManager::completeQueuedWithdrawal()` Directly - (File: contracts/NodeDelegator.sol)

---

### Summary

`NodeDelegator::completeUnstaking()` is the intended path for finalizing EigenLayer withdrawals. It decrements `LRTUnstakingVault::uncompletedWithdrawalCount` and forwards withdrawn assets to the vault. However, EigenLayer's `DelegationManager::completeQueuedWithdrawal()` is publicly callable by anyone. An external actor can call it directly, bypassing the protocol's accounting update, permanently inflating `uncompletedWithdrawalCount` and stranding withdrawn assets in the `NodeDelegator` rather than the `LRTUnstakingVault`.

---

### Finding Description

**Intended flow:**

1. `NodeDelegator::initiateUnstaking()` calls `DelegationManager::queueWithdrawals()` and increments `uncompletedWithdrawalCount` via `_getUnstakingVault().increaseUncompletedWithdrawalCount()`.
2. `NodeDelegator::completeUnstaking()` calls `DelegationManager::completeQueuedWithdrawal()`, then decrements `uncompletedWithdrawalCount` via `_getUnstakingVault().decreaseUncompletedWithdrawalCount()`, and forwards assets to `LRTUnstakingVault`. [1](#0-0) [2](#0-1) 

**The bypass:**

EigenLayer's `DelegationManager::completeQueuedWithdrawal()` is permissionless — anyone can call it for any queued withdrawal. The `NodeDelegator` is the `withdrawer` in the withdrawal struct, so assets are sent to the `NodeDelegator` regardless of who triggers the completion. The `NodeDelegator::completeUnstaking()` wrapper is `onlyLRTOperator`, but the underlying EigenLayer function has no such restriction. [3](#0-2) 

When an attacker calls `DelegationManager::completeQueuedWithdrawal()` directly:

- `_getUnstakingVault().decreaseUncompletedWithdrawalCount()` is **never called** → `uncompletedWithdrawalCount` remains permanently inflated.
- Withdrawn assets land in `NodeDelegator` but are **never forwarded** to `LRTUnstakingVault`.
- `LRTWithdrawalManager::unlockQueue()` reads `unstakingVault.balanceOf(asset)` to determine available assets; since the vault has no balance, no user withdrawals can be unlocked. [4](#0-3) [5](#0-4) 

**Compounding effect on new unstaking:**

`initiateUnstaking()` and `undelegate()` both check `uncompletedWithdrawalCount >= maxUncompletedWithdrawalCount`. With the counter inflated by each bypassed completion, the protocol eventually cannot queue any new EigenLayer withdrawals, freezing the entire unstaking pipeline. [6](#0-5) [7](#0-6) 

---

### Impact Explanation

**Temporary freezing of user withdrawal funds (Medium):** Withdrawn assets accumulate in `NodeDelegator` instead of `LRTUnstakingVault`. `LRTWithdrawalManager` cannot unlock queued user withdrawal requests because `unstakingVault.balanceOf(asset)` returns 0. Users who have already initiated withdrawals and are waiting for `unlockQueue()` cannot receive their assets until an operator manually calls `NodeDelegator::transferETHToLRTUnstakingVault()` or `transferBackToLRTDepositPool()` and the manager calls `LRTUnstakingVault::setUncompletedWithdrawalCount()` to resync. [8](#0-7) [9](#0-8) 

**Temporary freezing of new unstaking (Medium):** Each bypassed completion leaves `uncompletedWithdrawalCount` one unit too high. An attacker can repeat this for every queued withdrawal until the counter reaches `maxUncompletedWithdrawalCount`, after which `initiateUnstaking()` and `undelegate()` revert for all NodeDelegators.

---

### Likelihood Explanation

All queued EigenLayer withdrawals from `NodeDelegator` contracts are publicly visible on-chain via `DelegationManager::getQueuedWithdrawals()`. An attacker needs only to observe a queued withdrawal, wait for the EigenLayer unbonding period (~7 days), and call `DelegationManager::completeQueuedWithdrawal()` with the correct withdrawal struct before the operator does. No special privileges, capital, or front-running is required. The attack is repeatable for every queued withdrawal.

---

### Recommendation

1. **Do not rely solely on an internal counter.** Replace or supplement `uncompletedWithdrawalCount` with a live read from `DelegationManager::getQueuedWithdrawals(nodeDelegator).length`, as already done in `LRTUnstakingVault::setUncompletedWithdrawalCount()`. Make this the authoritative source rather than a manual resync escape hatch.

2. **Detect and handle out-of-band completions.** In `initiateUnstaking()` and `undelegate()`, compare the live EigenLayer queued withdrawal count against `uncompletedWithdrawalCount` and auto-correct if they diverge.

3. **Forward stranded assets.** Add a permissioned sweep function that detects asset balances in `NodeDelegator` that should be in `LRTUnstakingVault` and forwards them, reducing the manual recovery burden.

---

### Proof of Concept

```
1. Operator calls NodeDelegator::initiateUnstaking([stETHStrategy], [shares])
   → DelegationManager queues withdrawal W with withdrawer = NodeDelegator
   → uncompletedWithdrawalCount becomes 1

2. Attacker observes W on-chain via DelegationManager::getQueuedWithdrawals(NodeDelegator)

3. After EigenLayer's 7-day unbonding period, attacker calls:
   DelegationManager::completeQueuedWithdrawal(W, [stETH], true)
   → stETH is sent to NodeDelegator (the withdrawer)
   → NodeDelegator::completeUnstaking() is never called
   → uncompletedWithdrawalCount remains 1 (not decremented)
   → LRTUnstakingVault receives no stETH

4. LRTWithdrawalManager::unlockQueue(stETH, ...) reads:
   unstakingVault.balanceOf(stETH) == 0
   → revert AmountMustBeGreaterThanZero()
   → all pending user stETH withdrawal requests are frozen

5. Repeat for every queued withdrawal until uncompletedWithdrawalCount == maxUncompletedWithdrawalCount
   → NodeDelegator::initiateUnstaking() reverts with MaxUncompletedWithdrawalsReached
   → entire unstaking pipeline is frozen
``` [10](#0-9) [11](#0-10)

### Citations

**File:** contracts/NodeDelegator.sol (L293-331)
```text
    function initiateUnstaking(
        IStrategy[] calldata strategies,
        uint256[] calldata shares
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlyLRTOperator
        returns (bytes32 withdrawalRoot)
    {
        if (_getUnstakingVault().uncompletedWithdrawalCount() >= _getUnstakingVault().maxUncompletedWithdrawalCount()) {
            revert MaxUncompletedWithdrawalsReached();
        }
        if (strategies.length == 0) {
            revert ZeroLengthArray();
        }

        if (strategies.length != shares.length) {
            revert ArrayLengthMismatch();
        }

        for (uint256 i = 0; i < strategies.length; i++) {
            if (!NodeDelegatorHelper.isSupportedStrategy(lrtConfig, strategies[i])) {
                revert StrategyIsNotSetForAsset();
            }
        }

        IDelegationManager.QueuedWithdrawalParams[] memory queuedWithdrawalParams =
            new IDelegationManager.QueuedWithdrawalParams[](1);
        queuedWithdrawalParams[0] = IDelegationManagerTypes.QueuedWithdrawalParams({
            strategies: strategies, depositShares: shares, withdrawer: address(this)
        });

        bytes32[] memory withdrawalRoots = _getDelegationManager().queueWithdrawals(queuedWithdrawalParams);
        withdrawalRoot = withdrawalRoots[0];
        _getUnstakingVault().increaseUncompletedWithdrawalCount();
        emit WithdrawalQueued(_getNonce() - 1, address(this), withdrawalRoots);
    }
```

**File:** contracts/NodeDelegator.sol (L346-355)
```text
    function completeUnstaking(
        IDelegationManager.Withdrawal calldata withdrawal,
        IERC20[] calldata assets,
        bool receiveAsTokens
    )
        public
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
```

**File:** contracts/NodeDelegator.sol (L382-396)
```text
        _getDelegationManager().completeQueuedWithdrawal(withdrawal, assets, receiveAsTokens);

        _getUnstakingVault().decreaseUncompletedWithdrawalCount();

        if (receiveAsTokens) {
            for (uint256 i; i < assetCount; i++) {
                if (address(assets[i]) == LRTConstants.ETH_TOKEN) {
                    emit EthTransferred(address(_getUnstakingVault()), address(this).balance - balancesBefore[i]);
                    _getUnstakingVault().receiveFromNodeDelegator{ value: address(this).balance - balancesBefore[i] }();
                } else {
                    assets[i].safeTransfer(
                        address(_getUnstakingVault()), assets[i].balanceOf(address(this)) - balancesBefore[i]
                    );
                }
            }
```

**File:** contracts/NodeDelegator.sol (L493-502)
```text
    function transferETHToLRTUnstakingVault(uint256 amount)
        external
        nonReentrant
        whenNotPaused
        onlyAssetTransferRole
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        _getUnstakingVault().receiveFromNodeDelegator{ value: amount }();
        emit EthTransferred(address(_getUnstakingVault()), amount);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L39-40)
```text
    uint256 public uncompletedWithdrawalCount;
    uint256 public maxUncompletedWithdrawalCount;
```

**File:** contracts/LRTUnstakingVault.sol (L164-179)
```text
    function setUncompletedWithdrawalCount() external onlyLRTManager {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IDelegationManager delegationManager =
            IDelegationManager(lrtConfig.getContract(LRTConstants.EIGEN_DELEGATION_MANAGER));
        address[] memory nodeDelegatorQueue = lrtDepositPool.getNodeDelegatorQueue();
        uint256 totalQueued;
        for (uint256 i = 0; i < nodeDelegatorQueue.length; i++) {
            address nodeDelegator = nodeDelegatorQueue[i];
            (IDelegationManager.Withdrawal[] memory queuedWithdrawals,) =
                delegationManager.getQueuedWithdrawals(nodeDelegator);
            totalQueued += queuedWithdrawals.length;
        }

        uncompletedWithdrawalCount = totalQueued;

        emit UncompletedWithdrawalCountSet(totalQueued);
```

**File:** contracts/LRTUnstakingVault.sol (L184-194)
```text
    function increaseUncompletedWithdrawalCount() external onlyLRTNodeDelegator {
        uncompletedWithdrawalCount++;
    }

    /// @notice Decrease the number of uncompleted withdrawals.
    /// @dev This function is only callable by the NodeDelegator contracts during the unstaking process.
    function decreaseUncompletedWithdrawalCount() external onlyLRTNodeDelegator {
        if (uncompletedWithdrawalCount > 0) {
            uncompletedWithdrawalCount--;
        }
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L296-298)
```text

        if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();

```

**File:** contracts/LRTWithdrawalManager.sol (L846-851)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```
