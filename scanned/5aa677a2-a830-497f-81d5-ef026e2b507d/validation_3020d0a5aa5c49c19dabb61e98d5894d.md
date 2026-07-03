### Title
ETH Withdrawal Completion Blocked by Reverting Aave External Call in `_processWithdrawalCompletion` - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

When Aave integration is enabled, `completeWithdrawal()` (and `completeWithdrawalForUser()`) internally calls `aaveWETHGateway.withdrawETH()` — an external call to Aave's WETH Gateway — to source ETH for the user's payout. If this external call reverts for any reason (Aave pool paused, insufficient liquidity, governance action, etc.), the entire withdrawal completion transaction reverts, permanently blocking the user from receiving their unlocked ETH.

---

### Finding Description

In `LRTWithdrawalManager._processWithdrawalCompletion()`, when `isAaveIntegrationEnabled` is `true` and the contract's native ETH balance is insufficient to cover a user's withdrawal, the function calls `_withdrawFromAave(amountNeeded)`:

```solidity
// LRTWithdrawalManager.sol lines 719–731
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);   // <-- external call, can revert
        ...
    }
}
```

`_withdrawFromAave` at line 917 makes an unchecked external call:

```solidity
aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```

If `aaveWETHGateway.withdrawETH` reverts — due to Aave being paused, the pool having insufficient WETH liquidity, a supply cap being hit, or any other Aave-side condition — the revert propagates all the way up through `_processWithdrawalCompletion`, causing `completeWithdrawal` to revert. The user's withdrawal request has already been dequeued (line 705, `popFront()`) and the request record deleted (line 712, `delete withdrawalRequests[requestId]`), but the ETH is never transferred. The user is left with no withdrawal request on record and no ETH received.

**Compounding factor — no viable admin escape hatch**: The admin cannot easily unblock users by disabling Aave integration, because `setAaveIntegrationEnabled(false)` itself calls `_withdrawFromAave()` at line 495, which would also revert if Aave is broken. Similarly, `emergencyWithdrawFromAave()` at line 560 also calls `_withdrawFromAave()`. All three admin remediation paths share the same broken external call.

**Contrast with `unlockQueue`**: The developers already applied a `try/catch` pattern for Aave *deposits* in `unlockQueue` (lines 311–316), explicitly acknowledging that Aave calls can fail silently. The same defensive pattern was not applied to the withdrawal path. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

**Medium — Temporary (potentially extended) freezing of user ETH withdrawal funds.**

Any user with an unlocked ETH withdrawal request is unable to complete it while Aave is unavailable. Because the withdrawal request is dequeued and deleted before the Aave call is attempted, a revert leaves the user in a state where their request no longer exists in storage but they have not received their ETH. They cannot re-queue a new request (their rsETH was already burned at `initiateWithdrawal` time). The freeze persists until either Aave recovers or an admin successfully disables the integration — but as noted, the admin escape hatches also depend on the same broken Aave call. [4](#0-3) 

---

### Likelihood Explanation

**Medium.** Aave v3 pools can be paused by Aave governance or the Aave guardian in response to market stress, exploits, or risk events. The Aave WETH pool on Ethereum mainnet has historically been paused. The condition is triggered whenever: (1) Aave integration is enabled (an explicit admin opt-in), (2) the withdrawal manager's idle ETH balance is less than the user's withdrawal amount (the normal operating state when ETH is deployed to Aave), and (3) Aave is temporarily unavailable. All three conditions can realistically coincide. [5](#0-4) [6](#0-5) 

---

### Recommendation

Apply the same `try/catch` defensive pattern already used in `unlockQueue` to the Aave withdrawal call inside `_processWithdrawalCompletion`. If the Aave withdrawal fails, the function should either:

1. Fall back to serving the user from whatever idle ETH balance is available (partial or full), or
2. Revert with a clear error *before* dequeuing and deleting the withdrawal request, so the user's request remains intact and can be retried later.

The critical fix is to ensure the withdrawal request record is not deleted until the ETH transfer to the user is guaranteed to succeed, preserving the user's ability to retry. [7](#0-6) 

---

### Proof of Concept

1. Admin enables Aave integration via `setAaveIntegrationEnabled(true)`.
2. Operator calls `unlockQueue(ETH_TOKEN, ...)`, which unlocks Alice's withdrawal request and deposits the ETH into Aave via `_depositToAave`. Alice's request is now marked as unlocked.
3. Alice calls `completeWithdrawal(ETH_TOKEN, "")`.
4. Inside `_processWithdrawalCompletion`:
   - Line 705: Alice's nonce is popped from `userAssociatedNonces` (dequeued).
   - Line 712: `delete withdrawalRequests[requestId]` — request record erased.
   - Line 717: `unlockedWithdrawalsCount[asset]--`.
   - Line 720–724: `isAaveIntegrationEnabled` is `true`, contract ETH balance is 0 (all in Aave), so `_withdrawFromAave(amountNeeded)` is called.
   - Line 917: `aaveWETHGateway.withdrawETH(...)` reverts because Aave pool is paused.
5. The entire transaction reverts. Alice's withdrawal request is gone from storage, her rsETH was burned at step 2 (`initiateWithdrawal`), and she receives no ETH. She cannot re-initiate a withdrawal. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

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

**File:** contracts/LRTWithdrawalManager.sol (L486-505)
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
    }
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
