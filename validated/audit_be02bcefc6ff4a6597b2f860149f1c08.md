Audit Report

## Title
ETH Permanently Frozen When Recipient Contract Reverts on ETH Receipt — (`contracts/LRTWithdrawalManager.sol`)

## Summary

`LRTWithdrawalManager` uses a two-phase withdrawal: `unlockQueue` burns the user's rsETH and redeems ETH into the contract, then `completeWithdrawal` pushes ETH to the user via a raw `.call`. If the user is a contract that reverts on ETH receipt, the push always fails, the ETH remains in `LRTWithdrawalManager` with no alternative delivery path, and the already-burned rsETH is unrecoverable. This constitutes permanent freezing of funds.

## Finding Description

**Phase 1 — `unlockQueue`:** Burns rsETH and redeems the corresponding ETH from `LRTUnstakingVault` into `LRTWithdrawalManager` in a single atomic transaction. [1](#0-0) 

After this call, rsETH is gone and ETH sits in the contract.

**Phase 2 — `completeWithdrawal` / `_processWithdrawalCompletion`:** Delivers ETH to the user via `_transferAsset`. [2](#0-1) 

`_transferAsset` uses a raw low-level call: [3](#0-2) 

If `to` is a contract whose `receive()` reverts, `_transferAsset` reverts, which rolls back the entire `_processWithdrawalCompletion` call — including the `popFront`, `delete withdrawalRequests[requestId]`, and `unlockedWithdrawalsCount[asset]--` at lines 705, 712, and 717. The request is restored to the queue, `unlockedWithdrawalsCount` remains positive, and the ETH stays in the contract. [4](#0-3) 

**`completeWithdrawalForUser` provides no rescue:** The operator-callable function calls the identical `_processWithdrawalCompletion(asset, user, referralId)` with the same `user` address, hitting the same revert. [5](#0-4) 

The developer comment on line 191 acknowledges ETH is not the expected use case but incorrectly dismisses the risk — rsETH is already burned before the push is attempted.

**`sweepRemainingAssets` is permanently blocked:** While the stuck request keeps `unlockedWithdrawalsCount[asset] > 0`, the sweep guard reverts: [6](#0-5) 

There is no mechanism to redirect ETH to an alternate address, no pull-payment fallback, and no admin recovery function for stuck ETH.

## Impact Explanation

**Critical — Permanent freezing of funds.** The user's rsETH is irreversibly burned in `unlockQueue`. The corresponding ETH is redeemed into `LRTWithdrawalManager` but can never be delivered to a recipient contract that refuses ETH. No alternative recipient, no address-change mechanism, and no admin recovery path exist. The ETH is permanently locked in the contract.

## Likelihood Explanation

**Medium.** The affected user must be a contract address. This is realistic for smart contract wallets (e.g., Gnosis Safe) with a paused or broken `receive` function, contracts that conditionally accept ETH (e.g., require a specific caller or state), and protocol integrations that deposit rsETH on behalf of users and initiate withdrawals to a contract address. The user does not need to be malicious — a legitimate smart contract wallet with a bug in its fallback is sufficient to trigger permanent loss.

## Recommendation

Replace the push-payment pattern for ETH with a pull-payment (claim) model. Record the owed ETH amount in a mapping and allow the user (or any address they designate) to claim it separately:

```solidity
mapping(address user => uint256 amount) public pendingETHWithdrawals;

// In _processWithdrawalCompletion, instead of _transferAsset for ETH:
pendingETHWithdrawals[user] += request.expectedAssetAmount;

// New public function:
function claimETH() external nonReentrant {
    uint256 amount = pendingETHWithdrawals[msg.sender];
    if (amount == 0) revert NothingToClaim();
    pendingETHWithdrawals[msg.sender] = 0;
    (bool sent,) = payable(msg.sender).call{value: amount}("");
    if (!sent) revert EthTransferFailed();
}
```

This decouples settlement from delivery so that a recipient's refusal cannot freeze funds.

## Proof of Concept

1. Deploy `MaliciousWallet` — a contract whose `receive()` always reverts.
2. `MaliciousWallet` calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager` and a withdrawal request is recorded under `MaliciousWallet`'s address.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned at line 305; ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager` at line 307.
4. `MaliciousWallet` calls `completeWithdrawal(ETH_TOKEN, "")`. `_transferAsset` attempts `payable(MaliciousWallet).call{value: amount}("")`. `MaliciousWallet.receive()` reverts. The entire call reverts; the request remains in the queue.
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, MaliciousWallet, "")`. Same revert — `user` is still `MaliciousWallet`.
6. `sweepRemainingAssets` reverts because `hasUnlockedWithdrawals(ETH_TOKEN)` returns `true`.
7. rsETH is permanently burned. ETH is permanently locked in `LRTWithdrawalManager`. No recovery path exists.

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

**File:** contracts/LRTWithdrawalManager.sol (L301-307)
```text
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

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
