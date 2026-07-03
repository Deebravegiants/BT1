### Title
Aave v3 Pool Pause Permanently Blocks ETH Withdrawal Completion and Prevents Integration Disablement — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` integrates with Aave v3 to earn yield on idle ETH held for pending withdrawals. When Aave v3 is paused, every code path that attempts to withdraw ETH from Aave reverts with no fallback. Because the admin's only recovery mechanism (`setAaveIntegrationEnabled(false)`) also calls `_withdrawFromAave` internally, the integration cannot be disabled while Aave is paused. The result is a temporary but unresolvable freeze of all pending ETH withdrawals for as long as Aave remains paused.

---

### Finding Description

`LRTWithdrawalManager` deposits idle ETH into Aave v3 via `_depositToAave` (called from `unlockQueue`). Notably, the deposit path uses a `try/catch` to silently absorb Aave failures: [1](#0-0) 

However, the withdrawal path in `_processWithdrawalCompletion` has no such protection. When a user calls `completeWithdrawal` for ETH and the contract's idle balance is insufficient, it calls `_withdrawFromAave` directly: [2](#0-1) 

`_withdrawFromAave` calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))`, which internally calls the Aave v3 pool's `withdraw`. Aave v3 pools have a guardian-controlled pause mechanism; when paused, `withdraw` reverts unconditionally. This causes `completeWithdrawal` to revert for every affected user. [3](#0-2) 

The admin's only recovery path is `setAaveIntegrationEnabled(false)`, but this function also calls `_collectInterestToTreasury()` and then `_withdrawFromAave` before clearing the flag: [4](#0-3) 

`_collectInterestToTreasury` itself calls `aaveWETHGateway.withdrawETH`: [5](#0-4) 

So `setAaveIntegrationEnabled(false)` also reverts when Aave is paused, leaving the integration permanently enabled and the withdrawal path permanently broken for the duration of the Aave pause.

The `emergencyWithdrawFromAave` function, intended as a last-resort recovery, also calls `_withdrawFromAave` and therefore also reverts: [6](#0-5) 

---

### Impact Explanation

All users who have unlocked ETH withdrawal requests that require funds from Aave (i.e., the contract's idle ETH balance is less than the requested amount) cannot call `completeWithdrawal` successfully. Their rsETH has already been burned during `unlockQueue`, and their ETH is locked in Aave. The admin cannot disable the Aave integration to restore the fallback path. This constitutes a **temporary freezing of user funds** for the duration of the Aave v3 pause.

Impact: **Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

Aave v3 pools have a documented guardian role that can pause the pool in response to security incidents or oracle anomalies. This is a known, exercised operational feature (Aave v2 was paused in production). The `LRTWithdrawalManager` actively deposits ETH into Aave, so a non-trivial portion of withdrawal liquidity may reside there at any given time. The scenario is realistic and has precedent.

---

### Recommendation

1. Wrap the `_withdrawFromAave` call inside `_processWithdrawalCompletion` in a `try/catch`. If the withdrawal fails, revert with a descriptive error (e.g., `AaveWithdrawalFailed`) so users know to retry later, but do not permanently block the path.

2. Refactor `setAaveIntegrationEnabled(false)` to skip the `_withdrawFromAave` call (or wrap it in `try/catch`) so the flag can be cleared even when Aave is paused. Funds can be recovered separately once Aave unpauses.

3. Similarly, `emergencyWithdrawFromAave` should use a try/catch or a direct low-level call so it does not revert when Aave is paused.

---

### Proof of Concept

1. Protocol operator calls `unlockQueue(ETH, ...)`. ETH is redeemed from `LRTUnstakingVault` and deposited into Aave v3 via `depositToAaveExternal`. `totalETHDepositedToAave` increases; the contract's idle ETH balance is near zero.
2. Aave v3 guardian pauses the pool.
3. User calls `completeWithdrawal(ETH, ...)`. `_processWithdrawalCompletion` checks `address(this).balance < request.expectedAssetAmount` → true. It calls `_withdrawFromAave(amountNeeded)`.
4. `_withdrawFromAave` calls `aaveWETHGateway.withdrawETH(aavePool, ...)`. The Aave pool is paused → reverts.
5. `completeWithdrawal` reverts. All ETH withdrawal completions are blocked.
6. Admin calls `setAaveIntegrationEnabled(false)`. It calls `_collectInterestToTreasury()` → `aaveWETHGateway.withdrawETH(...)` → reverts. Admin cannot disable the integration.
7. Admin calls `emergencyWithdrawFromAave(type(uint256).max)`. It calls `_withdrawFromAave(...)` → `aaveWETHGateway.withdrawETH(...)` → reverts. Emergency recovery also fails.
8. Funds remain frozen in Aave for the entire duration of the pause with no admin escape hatch.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L310-316)
```text
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L486-504)
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

        isAaveIntegrationEnabled = enabled;
        emit AaveIntegrationEnabled(enabled);
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

**File:** contracts/LRTWithdrawalManager.sol (L905-921)
```text
    function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
        if (amount == 0) return 0;

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;

        emit ETHWithdrawnFromAave(withdrawnAmount, totalETHDepositedToAave);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L954-958)
```text
        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        (bool sent,) = payable(treasury).call{ value: interestAmount }("");
        if (!sent) revert TreasuryTransferFailed();
```
