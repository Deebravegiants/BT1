### Title
ETH Permanently Frozen in `LRTWithdrawalManager` When Withdrawing User Contract Lacks `receive()` - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
The ETH withdrawal completion flow in `LRTWithdrawalManager` sends ETH to the user via a low-level `.call`. If the user is a contract without a `receive()` or `payable fallback`, the ETH transfer always reverts. Because the user's rsETH was already burned in a prior, separate `unlockQueue` transaction, the ETH becomes permanently frozen in `LRTWithdrawalManager` with no recovery path.

### Finding Description
The ETH withdrawal lifecycle spans two separate transactions:

**Step 1 — `unlockQueue` (operator-initiated):** Burns the user's rsETH and pulls ETH from `LRTUnstakingVault` into `LRTWithdrawalManager`. [1](#0-0) 

**Step 2 — `completeWithdrawal` (user-initiated):** Calls `_processWithdrawalCompletion`, which attempts to send ETH to the user via `_transferAsset`. [2](#0-1) 

The ETH transfer at line 878 uses a raw `.call`:

```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

If `to` is a contract without a `receive()` or `payable fallback`, this call returns `false` and the entire `_processWithdrawalCompletion` reverts. The revert undoes all state mutations within that call (the `popFront`, `delete withdrawalRequests[requestId]`, and `unlockedWithdrawalsCount[asset]--`), so the withdrawal request remains in the queue. [3](#0-2) 

However, the rsETH burn from Step 1 occurred in a completely separate transaction and **cannot be reverted**. The ETH now sits in `LRTWithdrawalManager`, reserved for a user who can never receive it.

Neither `completeWithdrawal` nor `completeWithdrawalForUser` can redirect the ETH to a different address — both call `_processWithdrawalCompletion` with the original `user` address. [4](#0-3) 

The only admin sweep function, `sweepRemainingAssets`, is gated by `hasUnlockedWithdrawals(asset)`, which returns `true` as long as the stuck request exists — permanently blocking the sweep path. [5](#0-4) 

### Impact Explanation
**Critical — Permanent freezing of funds.** The user's rsETH has been irreversibly burned. The corresponding ETH is locked in `LRTWithdrawalManager` with no mechanism to redirect it or recover it. The user suffers a total loss of their withdrawal value.

### Likelihood Explanation
**Low-Medium.** The affected user must be a contract without a `receive()` or `payable fallback`. This is realistic for:
- Smart contract wallets (e.g., Safe multisigs configured without ETH acceptance)
- Protocol-level integrators or aggregators that call `initiateWithdrawal` on behalf of users
- Any contract that interacts with the withdrawal system but was not designed to receive raw ETH

The protocol explicitly supports contract callers (the `completeWithdrawalForUser` operator path implies non-EOA users are expected).

### Recommendation
Adopt a **pull-payment pattern** for ETH withdrawals: instead of pushing ETH to the user in `_processWithdrawalCompletion`, record the claimable amount in a mapping and let the user (or any address they designate) pull it. Alternatively, allow the user to specify a `recipient` address at `completeWithdrawal` time, or add an admin function to redirect a stuck ETH withdrawal to a user-specified address.

### Proof of Concept
1. Deploy `NoReceive` — a contract with no `receive()` or `payable fallback`.
2. `NoReceive` holds rsETH and calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned; ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`.
4. `NoReceive` calls `completeWithdrawal(ETH_TOKEN, "")`. Inside `_processWithdrawalCompletion`, `_transferAsset` attempts `payable(NoReceive).call{value: amount}("")`, which returns `false`. The call reverts with `EthTransferFailed`.
5. All state changes in step 4 are rolled back; the withdrawal request remains in the queue.
6. Every future call to `completeWithdrawal` or `completeWithdrawalForUser` for this user reverts identically.
7. `sweepRemainingAssets` reverts with `PendingWithdrawalsExist` because `unlockedWithdrawalsCount[ETH_TOKEN] > 0`.
8. The ETH is permanently frozen. The rsETH is permanently burned.

### Citations

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
