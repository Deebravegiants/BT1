### Title
ETH Withdrawal Permanently Frozen for Smart Contract Users Lacking `receive` Function — (`contracts/LRTWithdrawalManager.sol`)

### Summary

`LRTWithdrawalManager._transferAsset` sends ETH to the withdrawal recipient via a low-level `.call{value:}("")`. If the recipient is a smart contract without a `receive` (or `fallback`) function, the call returns `false` and the function reverts with `EthTransferFailed()`. Because the rsETH is burned in a prior, separate transaction (`unlockQueue`), the user's rsETH is permanently destroyed while the ETH remains locked inside `LRTWithdrawalManager` with no recovery path.

### Finding Description

The withdrawal lifecycle for ETH spans two separate transactions:

**Step 1 — `unlockQueue` (operator-initiated, separate tx):** [1](#0-0) 

The operator burns the user's rsETH and calls `unstakingVault.redeem(asset, assetAmountUnlocked)`, which pushes ETH into `LRTWithdrawalManager` via `receiveFromLRTUnstakingVault`. After this transaction, the rsETH is gone and the ETH sits in the withdrawal manager.

**Step 2 — `completeWithdrawal` / `completeWithdrawalForUser` (separate tx):** [2](#0-1) 

`_processWithdrawalCompletion` calls `_transferAsset(asset, user, request.expectedAssetAmount)`: [3](#0-2) 

If `user` is a smart contract without a `receive` function, `payable(to).call{value: amount}("")` returns `(false, "")` and the function reverts with `EthTransferFailed()`. Because this is a separate transaction from `unlockQueue`, the rsETH burn is **not** rolled back — it is already finalized.

The withdrawal request remains in the queue (the revert undoes the `delete` and `unlockedWithdrawalsCount--`), so `sweepRemainingAssets` is permanently blocked by the `hasUnlockedWithdrawals` guard: [4](#0-3) 

There is no cancellation mechanism for an unlocked withdrawal request. The ETH is permanently frozen.

The operator-facing `completeWithdrawalForUser` does not help — it calls the same internal function and fails identically. The developer comment acknowledges ETH transfer issues but dismisses them as non-impactful: [5](#0-4) 

### Impact Explanation

**Critical — Permanent freezing of funds.**

After `unlockQueue` executes, the user's rsETH is irreversibly burned. If `completeWithdrawal` then reverts because the user contract has no `receive` function, the corresponding ETH is permanently locked in `LRTWithdrawalManager`. The user loses both their rsETH and the ETH it represented. No admin function can recover the ETH while the unlocked withdrawal record exists, and no mechanism exists to cancel an already-unlocked withdrawal.

### Likelihood Explanation

**Medium.** Smart contracts that interact with DeFi protocols frequently omit `receive` functions — examples include custom DAO treasury contracts, yield aggregators that only handle ERC-20 tokens, and any contract deployed without explicit ETH-acceptance logic. A contract only needs to call `initiateWithdrawal` for ETH (no special privilege required) to trigger this path. The two-transaction split between `unlockQueue` and `completeWithdrawal` is what converts a simple revert into a permanent loss.

### Recommendation

In `_processWithdrawalCompletion`, before attempting the ETH transfer, verify the recipient can accept ETH (e.g., check `to.code.length == 0` for EOAs, or use a pull-payment pattern). Alternatively, implement a pull-payment model: instead of pushing ETH to the user in `completeWithdrawal`, credit the amount to a per-user claimable balance and let the user pull it separately. This decouples the accounting finalization from the ETH delivery and eliminates the permanent-freeze risk.

### Proof of Concept

1. Deploy a smart contract `VictimContract` with no `receive` function that holds rsETH.
2. `VictimContract` calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")` — rsETH is transferred to the withdrawal manager.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned from the withdrawal manager; ETH is moved from `LRTUnstakingVault` into `LRTWithdrawalManager`.
4. `VictimContract` calls `completeWithdrawal(ETH_TOKEN, "")` — `_transferAsset` attempts `payable(VictimContract).call{value: amount}("")`, which fails because `VictimContract` has no `receive` function. Transaction reverts with `EthTransferFailed()`.
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, address(VictimContract), "")` — same revert.
6. `VictimContract`'s rsETH is permanently burned; the ETH is permanently locked in `LRTWithdrawalManager`. `sweepRemainingAssets` reverts with `PendingWithdrawalsExist()`.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L191-203)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L395-413)
```text
    function sweepRemainingAssets(address asset)
        external
        nonReentrant
        onlySupportedAsset(asset)
        onlyLRTManager
        returns (uint256 transferredAmount)
    {
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();

        uint256 balance = _getAssetBalance(asset);
        if (balance == 0) revert AmountMustBeGreaterThanZero();

        // Transfer to treasury
        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        _transferAsset(asset, treasury, balance);

        emit RemainingAssetsSwept(asset, balance, treasury);
        return balance;
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
