### Title
stETH Rebasing Causes `completeWithdrawal()` to Permanently Revert for Last Queued Users - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager` supports stETH as a withdrawal asset. stETH is a rebasing token whose balance can decrease due to Lido validator slashing. After `unlockQueue()` transfers a fixed amount of stETH from `LRTUnstakingVault` to the withdrawal manager, a negative rebase reduces the contract's actual stETH balance below the sum of all committed `expectedAssetAmount` values. The last user(s) to call `completeWithdrawal()` will receive a revert from `safeTransfer`, permanently freezing their stETH until manual operator intervention.

### Finding Description
stETH is initialized as a core supported asset in `LRTConfig.initialize()`. [1](#0-0) 

The withdrawal lifecycle proceeds as follows:

**Step 1 — `initiateWithdrawal()`**: A user submits a withdrawal request. `expectedAssetAmount` is computed from oracle prices and stored in `withdrawalRequests[requestId]`. `assetsCommitted[stETH]` is incremented by this amount. [2](#0-1) 

**Step 2 — `unlockQueue()`**: An operator calls `unlockQueue()`. `_createUnlockParams()` reads `unstakingVault.balanceOf(stETH)` as the available asset amount at that instant. [3](#0-2) 

`_unlockWithdrawalRequests()` iterates over pending requests, sets each `request.expectedAssetAmount = payoutAmount`, and accumulates `assetAmountToUnlock` as the exact sum of all payout amounts. [4](#0-3) 

`unstakingVault.redeem(asset, assetAmountUnlocked)` then transfers exactly `assetAmountUnlocked` stETH tokens from the vault to the withdrawal manager. [5](#0-4) 

At this point, the withdrawal manager holds exactly `assetAmountUnlocked` stETH, and the sum of all unlocked `request.expectedAssetAmount` values equals `assetAmountUnlocked`.

**Step 3 — Negative stETH rebase**: Between `unlockQueue()` and `completeWithdrawal()`, a Lido slashing event causes a negative rebase. The withdrawal manager's stETH balance decreases below `assetAmountUnlocked`, but all stored `request.expectedAssetAmount` values remain unchanged.

**Step 4 — `completeWithdrawal()` reverts**: `_processWithdrawalCompletion()` unconditionally calls: [6](#0-5) 

`_transferAsset` calls `IERC20(asset).safeTransfer(to, amount)`. [7](#0-6) 

Because the contract's stETH balance is now less than the sum of all pending `expectedAssetAmount` values, the last user(s) in the queue will receive a revert. There is no fallback, no partial-fill path, and no mechanism to reduce `expectedAssetAmount` post-unlock to match the actual balance.

### Impact Explanation
**Medium — Temporary freezing of funds.** Users whose unlocked stETH withdrawal requests cannot be fulfilled are stuck: their rsETH has already been burned (during `unlockQueue()`), and their stETH cannot be transferred out. Recovery requires manual operator action (e.g., topping up the contract with additional stETH or re-running `unlockQueue()` after the balance is restored), which is not guaranteed to happen promptly.

### Likelihood Explanation
**Low-Medium.** stETH is a first-class supported asset. Lido slashing events are rare but have occurred on mainnet. The window of exposure is the `withdrawalDelayBlocks` period (default 8 days) between `unlockQueue()` and `completeWithdrawal()`. Any negative rebase during this window, however small, will cause the last user's transfer to fail if the contract holds no excess stETH buffer.

### Recommendation
In `_processWithdrawalCompletion()`, before transferring stETH, check the contract's actual balance and cap the transfer to `min(request.expectedAssetAmount, contractBalance)`. Alternatively, after `unlockQueue()` transfers stETH from the vault, record the actual received balance and distribute it proportionally among unlocked requests rather than using fixed `expectedAssetAmount` values. A simpler mitigation is to always leave a small stETH buffer in the vault and re-read the live balance at completion time.

### Proof of Concept
1. 10 users each call `initiateWithdrawal(stETH, X)`. Each request stores `expectedAssetAmount = A`. `assetsCommitted[stETH] = 10A`.
2. Operator calls `unlockQueue(stETH, ...)`. `unstakingVault.balanceOf(stETH)` returns `10A`. `_unlockWithdrawalRequests` sets each request's `expectedAssetAmount = A` and `assetAmountToUnlock = 10A`. `unstakingVault.redeem(stETH, 10A)` transfers exactly `10A` stETH to the withdrawal manager.
3. A Lido slashing event causes a 0.1% negative rebase. The withdrawal manager now holds `9.99A` stETH.
4. Users 1–9 call `completeWithdrawal(stETH)` successfully, each receiving `A` stETH. The contract now holds `9.99A - 9A = 0.99A` stETH.
5. User 10 calls `completeWithdrawal(stETH)`. `_transferAsset` attempts `safeTransfer(user10, A)` but the contract only holds `0.99A`. The call reverts. User 10's rsETH is already burned; their stETH is frozen in the contract. [8](#0-7)

### Citations

**File:** contracts/LRTConfig.sol (L54-57)
```text
        _setToken(LRTConstants.ST_ETH_TOKEN, stETH);
        _setToken(LRTConstants.ETHX_TOKEN, ethX);
        _addNewSupportedAsset(stETH, 100_000 ether);
        _addNewSupportedAsset(ethX, 100_000 ether);
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L798-808)
```text
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

```

**File:** contracts/LRTWithdrawalManager.sol (L837-851)
```text
    function _createUnlockParams(
        ILRTOracle lrtOracle,
        ILRTUnstakingVault unstakingVault,
        address asset
    )
        internal
        view
        returns (UnlockParams memory)
    {
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
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
