### Title
Aave Integration Pause Permanently Blocks ETH Withdrawal Completion With No Recovery Path - (File: contracts/LRTWithdrawalManager.sol)

### Summary
When the Aave V3 pool is paused, users with unlocked ETH withdrawal requests cannot complete their withdrawals. Every admin escape hatch (`emergencyWithdrawFromAave`, `setAaveIntegrationEnabled(false)`, `configureAaveIntegration`) also calls `_withdrawFromAave` internally and reverts under the same condition, leaving the integration impossible to disable and user ETH permanently stuck.

### Finding Description
`LRTWithdrawalManager` optionally deposits idle ETH into Aave V3 to earn yield. When `isAaveIntegrationEnabled` is `true` and the contract's native ETH balance is insufficient to cover a user's unlocked withdrawal, `_processWithdrawalCompletion` calls `_withdrawFromAave` to pull the shortfall from Aave. [1](#0-0) 

`_withdrawFromAave` unconditionally calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))`. [2](#0-1) 

If the Aave V3 pool is paused, `withdrawETH` reverts, propagating the revert through `_processWithdrawalCompletion` and blocking `completeWithdrawal` and `completeWithdrawalForUser` for every ETH withdrawal request.

The three intended recovery paths all share the same fatal flaw — each one calls `_withdrawFromAave` before it can disable the integration:

1. **`emergencyWithdrawFromAave`** — calls `_withdrawFromAave(amount)` directly. [3](#0-2) 

2. **`setAaveIntegrationEnabled(false)`** — calls `_withdrawFromAave(aaveBalance)` before clearing the flag. [4](#0-3) 

3. **`configureAaveIntegration`** — calls `_withdrawFromAave` on the old pool before accepting new addresses. [5](#0-4) 

There is no code path that sets `isAaveIntegrationEnabled = false` without first successfully withdrawing from Aave. When Aave is paused, none of these paths can complete, and the integration cannot be disabled.

### Impact Explanation
**Medium — Temporary freezing of funds; Critical if Aave is permanently deprecated.**

All ETH that was deposited into Aave via `unlockQueue → depositToAaveExternal` is inaccessible while Aave is paused. Every user whose unlocked ETH withdrawal requires a drawdown from Aave has their funds frozen. If Aave is permanently paused or deprecated, those funds are permanently locked and all pending ETH withdrawal requests become uncompletable.

### Likelihood Explanation
Aave V3 has a documented pause mechanism and has been paused on mainnet in the past (e.g., during the Euler Finance exploit in March 2023). The Aave integration is an explicit, enabled feature of `LRTWithdrawalManager`. The protocol's own audit scope acknowledges third-party pausability as in-scope. The trigger (Aave pause) is a realistic, precedented event, not a theoretical edge case.

### Recommendation
1. In `_processWithdrawalCompletion`, wrap `_withdrawFromAave` in a `try/catch`; if the withdrawal fails, revert with a descriptive error so the operator knows to disable the integration first, or allow partial fulfillment from the contract's native balance.
2. Separate the "disable flag" from the "withdraw funds" step in `setAaveIntegrationEnabled(false)`. Allow the flag to be cleared even when Aave is paused, so that `completeWithdrawal` can fall back to native ETH balance only.
3. Add a `forceDisableAaveIntegration()` function (callable by `PAUSER_ROLE`) that sets `isAaveIntegrationEnabled = false` without attempting any Aave withdrawal, to be used when Aave is paused.

### Proof of Concept
1. Manager calls `setAaveIntegrationEnabled(true)` and `configureAaveIntegration(...)`.
2. Operator calls `unlockQueue(ETH_TOKEN, ...)` — ETH is unlocked and auto-deposited to Aave via `depositToAaveExternal`.
3. User calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, ...)` — request is queued.
4. Operator calls `unlockQueue` again — user's request is unlocked; ETH is in Aave, not in the contract.
5. Aave V3 pool is paused (governance action or emergency).
6. User calls `completeWithdrawal(ETH_TOKEN, referralId)`.
7. `_processWithdrawalCompletion` checks `address(this).balance < request.expectedAssetAmount` → true.
8. `_withdrawFromAave(amountNeeded)` is called → `aaveWETHGateway.withdrawETH(aavePool, ...)` reverts.
9. User's `completeWithdrawal` reverts. Funds are frozen.
10. Pauser calls `emergencyWithdrawFromAave(type(uint256).max)` → also calls `_withdrawFromAave` → also reverts.
11. Manager calls `setAaveIntegrationEnabled(false)` → tries `_withdrawFromAave` → also reverts.
12. No recovery path exists. ETH remains locked in Aave until Aave is unpaused.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L438-453)
```text
        if (address(aaveAWETH) != address(0) && address(aaveWETHGateway) != address(0) && aavePool != address(0)) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw all remaining principal from old Aave pool
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }

            // Revoke approval for old aWETH token
            IERC20(address(aaveAWETH)).forceApprove(address(aaveWETHGateway), 0);
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L486-501)
```text
        if (!enabled) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw remaining principal from Aave back to contract
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }

            // Revoke approval for aWETH token to Aave WETH Gateway
            _revokeApprovalToAaveWETHGateway();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L551-563)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L720-732)
```text
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L917-918)
```text
        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;
```
