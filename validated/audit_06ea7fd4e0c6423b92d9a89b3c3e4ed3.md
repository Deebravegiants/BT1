Audit Report

## Title
Permanent ETH Freeze via Push-Payment to Reverting Recipient Contract — (`contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTWithdrawalManager` uses a two-transaction withdrawal lifecycle: `unlockQueue` burns rsETH and redeems ETH into the contract in one transaction, then `completeWithdrawal` pushes ETH to the user via a raw `call` in a second transaction. If the recipient is a contract that reverts on ETH receipt, the push always fails, the ETH remains in `LRTWithdrawalManager` indefinitely, and no on-chain recovery path exists — the rsETH is already permanently burned.

## Finding Description
**Step 1 — `unlockQueue`:** Burns the user's rsETH held in the contract and redeems the corresponding ETH from `LRTUnstakingVault` into `LRTWithdrawalManager`. This is an irreversible, separate transaction. [1](#0-0) 

**Step 2 — `completeWithdrawal` / `_processWithdrawalCompletion`:** Calls `_transferAsset` to push ETH to the user address. [2](#0-1) 

**The push transfer:** [3](#0-2) 

If `to` is a contract that reverts on ETH receipt, `_transferAsset` reverts, which rolls back the entire `_processWithdrawalCompletion` call — the nonce is restored to the queue, `unlockedWithdrawalsCount` is not decremented, and the ETH stays in the contract. Because the revert is deterministic (the recipient always refuses ETH), every subsequent call to `completeWithdrawal` or `completeWithdrawalForUser` will also revert. [4](#0-3) 

**`completeWithdrawalForUser` provides no rescue:** It calls the identical `_processWithdrawalCompletion` and suffers the same revert. The developer comment acknowledges this function is "not expected to be used for ETH" but incorrectly frames the risk as non-impactful gas grief — the actual consequence is permanent fund loss. [5](#0-4) 

**`sweepRemainingAssets` is permanently blocked:** It gates on `hasUnlockedWithdrawals(asset)`, which returns `true` as long as `unlockedWithdrawalsCount[asset] > 0`. Because the stuck request keeps this counter elevated, the sweep path is permanently blocked for the affected asset. [6](#0-5) [7](#0-6) 

There is no admin function to redirect ETH to an alternative address, no pull-payment fallback, and no mechanism to cancel an unlocked withdrawal request and return rsETH (which is already burned).

## Impact Explanation
**Critical — Permanent freezing of funds.** The user's rsETH is irreversibly burned in `unlockQueue`. The corresponding ETH is redeemed into `LRTWithdrawalManager` but can never be delivered to a recipient contract that refuses ETH. No alternative delivery mechanism, address-change function, or admin recovery path exists in the current contract. The ETH is permanently locked.

## Likelihood Explanation
**Medium.** The affected user must be a contract address, not an EOA. This is realistic for smart contract wallets (e.g., Gnosis Safe with a paused or misconfigured `receive`), contracts that conditionally accept ETH (e.g., require a specific caller or state), and protocol integrations that deposit rsETH on behalf of users and initiate withdrawals to a contract address. The user does not need to be malicious — a legitimate smart contract wallet with a broken fallback is sufficient. The scenario is repeatable for any such address.

## Recommendation
Replace the push-payment pattern for ETH with a pull-payment (claim) model. Instead of calling `_transferAsset` directly in `_processWithdrawalCompletion`, record the owed amount in a per-user mapping and expose a separate `claimETH()` function:

```solidity
mapping(address user => uint256 amount) public pendingETHWithdrawals;

// In _processWithdrawalCompletion, replace _transferAsset for ETH:
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

This decouples settlement (accounting) from delivery (transfer), so a recipient's refusal cannot freeze funds or block the queue.

## Proof of Concept
1. Deploy `MaliciousWallet` — a contract whose `receive()` always reverts.
2. `MaliciousWallet` calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned (`burnFrom` at L305); ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager` (L307).
4. `MaliciousWallet` calls `completeWithdrawal(ETH_TOKEN, "")`. `_transferAsset` attempts `payable(MaliciousWallet).call{value: amount}("")`. `receive()` reverts. Entire call reverts. State is rolled back; request remains in queue.
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, MaliciousWallet, "")`. Same code path, same revert.
6. `sweepRemainingAssets(ETH_TOKEN)` reverts with `PendingWithdrawalsExist` because `unlockedWithdrawalsCount[ETH_TOKEN] > 0`.
7. Result: rsETH permanently burned, ETH permanently locked in `LRTWithdrawalManager`, no on-chain recovery path.

**Foundry test sketch:**
```solidity
contract RevertingReceiver {
    receive() external payable { revert("no ETH"); }
}

function test_permanentETHFreeze() public {
    RevertingReceiver receiver = new RevertingReceiver();
    // Fund receiver with rsETH, initiate withdrawal as receiver
    vm.prank(address(receiver));
    withdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "");
    // Operator unlocks queue — rsETH burned, ETH redeemed
    vm.prank(operator);
    withdrawalManager.unlockQueue(ETH_TOKEN, ...);
    // completeWithdrawal always reverts
    vm.prank(address(receiver));
    vm.expectRevert();
    withdrawalManager.completeWithdrawal(ETH_TOKEN, "");
    // sweepRemainingAssets blocked
    vm.prank(manager);
    vm.expectRevert(PendingWithdrawalsExist.selector);
    withdrawalManager.sweepRemainingAssets(ETH_TOKEN);
    // ETH permanently stuck
    assertGt(address(withdrawalManager).balance, 0);
}
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L191-204)
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
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L395-414)
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
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L629-631)
```text
    function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
        return unlockedWithdrawalsCount[asset] > 0;
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
