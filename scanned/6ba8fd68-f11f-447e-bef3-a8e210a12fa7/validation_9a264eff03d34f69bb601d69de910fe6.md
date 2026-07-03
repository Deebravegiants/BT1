### Title
ETH Withdrawal Permanently Frozen When Recipient Contract Cannot Receive ETH - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager._transferAsset()` pushes native ETH directly to the withdrawal recipient via `.call{value:}` and unconditionally reverts on failure. If the recipient is a smart contract without a `receive()`/`fallback()` function (or one that reverts on ETH receipt), `completeWithdrawal` will always revert. Because rsETH is already burned from the contract's balance during `unlockQueue`, the user's ETH becomes permanently frozen with no recovery path.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is:

1. **`initiateWithdrawal`** — user's rsETH is transferred into the withdrawal manager.
2. **`unlockQueue`** — rsETH is burned from the withdrawal manager (`burnFrom(address(this), rsETHBurned)`) and ETH is redeemed from `LRTUnstakingVault` into the withdrawal manager.
3. **`completeWithdrawal`** — ETH is pushed to the user via `_transferAsset`.

The critical transfer occurs in `_transferAsset`:

```solidity
// contracts/LRTWithdrawalManager.sol lines 876–883
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();   // <-- unconditional revert
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
```

This is called from `_processWithdrawalCompletion` at line 734:

```solidity
// contracts/LRTWithdrawalManager.sol line 734
_transferAsset(asset, user, request.expectedAssetAmount);
```

If `user` is a smart contract that cannot receive ETH, the `.call` returns `sent = false`, and `EthTransferFailed` is thrown. The entire transaction reverts, preserving the withdrawal request state. However, the user will face the same revert on every subsequent attempt. Meanwhile, the rsETH that was burned in step 2 is gone permanently — it was burned from the withdrawal manager's own balance, not rolled back by the revert in step 3.

The operator path `completeWithdrawalForUser` also calls `_processWithdrawalCompletion(asset, user, referralId)` and sends ETH to `user`, so it provides no escape.

There is no admin recovery function for individual user ETH balances. `sweepRemainingAssets` is blocked while `unlockedWithdrawalsCount[asset] > 0`, which remains true as long as the stuck withdrawal exists.

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

After `unlockQueue` executes:
- The user's rsETH is irreversibly burned from the withdrawal manager.
- The corresponding ETH sits in the withdrawal manager.
- `completeWithdrawal` and `completeWithdrawalForUser` both revert for this user.
- No admin sweep or recovery path exists.

The user permanently loses their rsETH value with no recourse.

---

### Likelihood Explanation

**Medium.** Smart contracts routinely hold and manage rsETH — DeFi protocols, multisigs, vaults, and aggregators are common depositors. Many such contracts lack a `receive()` function (e.g., pure ERC20 vaults, proxy contracts with no ETH handling). Any such contract that initiates an ETH withdrawal triggers this freeze. The path requires no privileged access and is reachable by any depositor.

---

### Recommendation

Replace the push-ETH pattern with a **pull-payment** (claimable balance) model for ETH withdrawals, or wrap ETH to WETH before delivery so the transfer is always an ERC20 `safeTransfer`. At minimum, store the ETH in a per-user claimable mapping when the direct push fails, rather than reverting:

```solidity
// Instead of reverting on failed ETH push:
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) {
    pendingEthClaims[to] += amount;  // allow user to pull later
}
```

---

### Proof of Concept

1. Deploy a smart contract `Victim` with no `receive()` function that holds rsETH.
2. `Victim` calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned from the withdrawal manager, ETH is redeemed into it.
4. `Victim` calls `completeWithdrawal(ETH_TOKEN, "")` → `_processWithdrawalCompletion` → `_transferAsset(ETH_TOKEN, Victim, amount)` → `.call{value:}` returns `false` → `revert EthTransferFailed()`.
5. Step 4 reverts every time. rsETH is gone. ETH is stuck in the withdrawal manager forever.

Relevant lines: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L183-204)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }

    /// @notice Allows operators to complete a user's withdrawal process
    /// @param asset The asset address the user wishes to withdraw
    /// @param user The address of the user whose withdrawal to complete
    /// @param referralId The referral identifier for tracking
    /// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
    function completeWithdrawalForUser(
        address asset,
        address user,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
        _processWithdrawalCompletion(asset, user, referralId);
        emit AssetWithdrawalCompletedBy(msg.sender);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L301-307)
```text
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
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

**File:** contracts/LRTWithdrawalManager.sol (L876-883)
```text
    function _transferAsset(address asset, address to, uint256 amount) internal {
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
            IERC20(asset).safeTransfer(to, amount);
        }
    }
```
