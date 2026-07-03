### Title
Permanent ETH Freeze for Contract Withdrawers Without Fallback in `LRTWithdrawalManager` - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

A contract that lacks a `receive`/`fallback` function can initiate an ETH withdrawal via `initiateWithdrawal`. After the operator calls `unlockQueue` — which **irreversibly burns the rsETH** and moves ETH into the withdrawal manager — any subsequent call to `completeWithdrawal` will always revert because the ETH transfer to the contract recipient fails. The rsETH is already gone, and the allocated ETH is permanently frozen with no recovery path.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is split across three separate transactions:

**Step 1 — `initiateWithdrawal`**: The user's rsETH is transferred from `msg.sender` into the withdrawal manager. [1](#0-0) 

**Step 2 — `unlockQueue`** (operator-only): The rsETH held by the manager is **burned** and the corresponding ETH is pulled from the unstaking vault into the withdrawal manager. [2](#0-1) 

**Step 3 — `completeWithdrawal`**: The ETH is sent to the user via a low-level call. [3](#0-2) 

The critical flaw is that Steps 2 and 3 are in **separate transactions**. After Step 2 completes, the rsETH is permanently burned and the ETH is sitting in the withdrawal manager allocated to the user's request. If the user is a contract without a `receive`/`fallback` function, Step 3 will always revert with `EthTransferFailed`. The revert in Step 3 undoes the `delete withdrawalRequests[requestId]` at line 712, so the request remains in the queue — but the rsETH is already gone and the ETH can never be delivered. [4](#0-3) 

The operator-assisted path `completeWithdrawalForUser` provides no relief because it calls the same `_processWithdrawalCompletion(asset, user, referralId)` with the same non-payable `user` address. [5](#0-4) 

The only administrative escape valve, `sweepRemainingAssets`, is blocked as long as any unlocked withdrawal exists for the asset: [6](#0-5) 

Since the stuck withdrawal request is itself an unlocked withdrawal, the sweep is permanently gated. The ETH is frozen indefinitely.

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

The user's rsETH is burned (Step 2) and the corresponding ETH is irrecoverably locked in `LRTWithdrawalManager`. There is no cancellation function, no alternative recipient parameter, and no admin override that can redirect the ETH away from the non-payable contract address. Both the rsETH and the ETH value are permanently lost to the user.

---

### Likelihood Explanation

**Medium.** DeFi protocols, multisig wallets (e.g., Gnosis Safe with certain configurations), and smart contract vaults routinely hold rsETH and interact with withdrawal systems. A contract that holds rsETH and calls `initiateWithdrawal` for ETH but does not implement `receive()` will trigger this freeze. The user is given no warning at `initiateWithdrawal` time that their contract must be ETH-receivable, and the failure only manifests after the rsETH is already burned.

---

### Recommendation

1. **Preferred**: Add an optional `recipient` parameter to `initiateWithdrawal` so the user can designate a separate EOA address to receive ETH at completion time.
2. **Alternative**: Validate at `initiateWithdrawal` time that `msg.sender` can receive ETH (e.g., attempt a zero-value call and revert if it fails) when the requested asset is ETH.
3. **Fallback**: Implement a pull-payment pattern — instead of pushing ETH in `completeWithdrawal`, credit the user's claimable balance and let them pull it via a separate `claimETH()` call to an address of their choice.

---

### Proof of Concept

1. Deploy `VaultContract` — a contract with no `receive`/`fallback` that holds rsETH.
2. `VaultContract` calls `initiateWithdrawal(ETH_TOKEN, 1e18, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned at line 305; ETH is moved from `LRTUnstakingVault` to `LRTWithdrawalManager` at line 307.
4. Anyone calls `completeWithdrawal(ETH_TOKEN, "")` on behalf of `VaultContract` (or `VaultContract` calls it itself). `_transferAsset` executes `payable(VaultContract).call{value: amount}("")` — this returns `success = false` because `VaultContract` has no fallback. The call reverts with `EthTransferFailed`.
5. The withdrawal request is restored by the revert, but the rsETH burned in Step 3 is gone. Step 4 will revert identically on every future attempt. `sweepRemainingAssets` is blocked by `hasUnlockedWithdrawals`. The ETH is permanently frozen. [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L192-203)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L402-403)
```text
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
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
