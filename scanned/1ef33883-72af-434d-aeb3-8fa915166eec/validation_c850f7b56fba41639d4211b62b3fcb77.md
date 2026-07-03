### Title
Aave Pool Pause Causes Denial of Service in ETH Withdrawal Completion - (`contracts/LRTWithdrawalManager.sol`)

### Summary

`LRTWithdrawalManager._processWithdrawalCompletion()` unconditionally calls `_withdrawFromAave()` → `aaveWETHGateway.withdrawETH()` when the Aave integration is enabled and the contract's ETH balance is insufficient to cover a user's withdrawal. If the Aave v3 pool is paused (a standard Aave guardian action), this external call reverts, permanently blocking all ETH `completeWithdrawal()` calls that require Aave liquidity — even though the user's rsETH was already burned in the prior `unlockQueue()` step.

### Finding Description

When the Aave integration is active, the ETH withdrawal lifecycle is:

1. **`initiateWithdrawal()`** — user deposits rsETH, a withdrawal request is recorded.
2. **`unlockQueue()`** — operator unlocks requests; rsETH is burned from the contract (`burnFrom` at line 305).
3. **`completeWithdrawal()`** → `_processWithdrawalCompletion()` — user claims ETH.

Inside `_processWithdrawalCompletion()`, if the contract's native ETH balance is below the user's `expectedAssetAmount`, the code calls `_withdrawFromAave()`: [1](#0-0) 

`_withdrawFromAave()` then calls the external Aave gateway without any error handling: [2](#0-1) 

The Aave v3 pool has a well-documented guardian-controlled pause mechanism. When the pool is paused, all operations — including `withdrawETH` — revert. There is no try/catch or fallback in `_processWithdrawalCompletion()`, so the entire `completeWithdrawal()` transaction reverts.

Contrast this with `unlockQueue()`, which correctly wraps its Aave deposit call in a try/catch: [3](#0-2) 

The same defensive pattern is absent on the withdrawal side.

The `emergencyWithdrawFromAave()` escape hatch also calls `_withdrawFromAave()` internally and would equally revert while the pool is paused: [4](#0-3) 

### Impact Explanation

**Temporary freezing of funds (Medium).** Users whose ETH withdrawal requests require Aave liquidity cannot call `completeWithdrawal()` while the Aave pool is paused. Their rsETH was already burned in `unlockQueue()` and cannot be recovered. The ETH remains locked in Aave until the pool is unpaused. Because Aave pauses are typically temporary (guardian-controlled), this is a temporary rather than permanent freeze, but it directly blocks user fund access with no protocol-side workaround available during the pause.

### Likelihood Explanation

Aave v3 pool pauses are a real, exercised mechanism — the Aave guardian has paused pools on mainnet in response to security incidents. The Aave integration is explicitly enabled by the protocol (`isAaveIntegrationEnabled`), and ETH is the primary asset for which Aave is used. Any ETH withdrawer whose request was unlocked while Aave held the liquidity is affected for the duration of the pause.

### Recommendation

Apply the same try/catch pattern used in `unlockQueue()` to the `_withdrawFromAave` call inside `_processWithdrawalCompletion()`. If the Aave withdrawal fails, the function should either revert with a clear error (allowing the user to retry later) or — preferably — skip the Aave withdrawal and revert with `InsufficientLiquidityForWithdrawal` only if the contract balance is still insufficient after the failed attempt:

```diff
 if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
     uint256 contractBalance = address(this).balance;
     if (contractBalance < request.expectedAssetAmount) {
         uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
-        _withdrawFromAave(amountNeeded);
+        try this.withdrawFromAaveExternal(amountNeeded) { } catch { }
         uint256 balanceAfter = address(this).balance;
         if (balanceAfter < request.expectedAssetAmount) {
             revert InsufficientLiquidityForWithdrawal();
         }
     }
 }
```

This mirrors the existing `depositToAaveExternal` pattern and ensures a paused Aave pool does not permanently block user withdrawals.

### Proof of Concept

1. Aave integration is enabled; ETH depositors have funds sitting in Aave (`totalETHDepositedToAave > 0`).
2. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned from the contract, withdrawal requests are unlocked.
3. Aave guardian pauses the Aave v3 pool (e.g., in response to a security incident).
4. User calls `completeWithdrawal(ETH_TOKEN, ...)`.
5. `_processWithdrawalCompletion` checks `address(this).balance < request.expectedAssetAmount` → true (ETH is in Aave).
6. `_withdrawFromAave(amountNeeded)` calls `aaveWETHGateway.withdrawETH(aavePool, ...)`.
7. Aave pool reverts because it is paused.
8. The entire `completeWithdrawal` transaction reverts.
9. The user's rsETH is already burned; they cannot withdraw their ETH for the duration of the pause. [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L309-317)
```text
        // If Aave integration is enabled and asset is ETH, deposit to Aave
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L551-562)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
```

**File:** contracts/LRTWithdrawalManager.sol (L699-738)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;

        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
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

        _transferAsset(asset, user, request.expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(user, asset, request.rsETHUnstaked, request.expectedAssetAmount);
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

**File:** contracts/interfaces/aave/IWrappedTokenGatewayV3.sol (L1-8)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

interface IWrappedTokenGatewayV3 {
    function depositETH(address pool, address onBehalfOf, uint16 referralCode) external payable;

    function withdrawETH(address pool, uint256 amount, address to) external;
}
```
