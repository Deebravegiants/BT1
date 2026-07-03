### Title
Unbounded ETH Transfer to User-Controlled Address Permanently Freezes Withdrawn ETH - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager._transferAsset` sends ETH to a user-controlled address via an uncapped `.call{value: amount}("")`. Because the ETH unlock step (`unlockQueue`) and the ETH delivery step (`completeWithdrawal`) are separate transactions, a contract recipient whose `receive()` reverts will permanently freeze the already-unlocked ETH with no admin recovery path.

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is split across two independent transactions:

**Step 1 – `unlockQueue` (operator-only):**
rsETH is burned from the contract and ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`. [1](#0-0) 

**Step 2 – `completeWithdrawal` / `completeWithdrawalForUser`:**
ETH is forwarded to the user via `_transferAsset`. [2](#0-1) 

The ETH transfer uses an uncapped low-level call: [3](#0-2) 

If the recipient (`user`) is a contract whose `receive()` or fallback reverts, the call at line 878 fails, `_transferAsset` reverts with `EthTransferFailed`, and the entire `_processWithdrawalCompletion` transaction is rolled back. [4](#0-3) 

Because the rsETH burn happened in a **prior, already-finalized** `unlockQueue` transaction, the revert of `completeWithdrawal` cannot undo it. The ETH sits in `LRTWithdrawalManager` indefinitely. The only potential recovery function, `sweepRemainingAssets`, is gated on `hasUnlockedWithdrawals(asset) == false`: [5](#0-4) 

But `unlockedWithdrawalsCount[asset]` remains > 0 for the stuck request (the decrement at line 717 is reverted along with the failed transfer), so `sweepRemainingAssets` is permanently blocked too.

The protocol team's own comment at line 191 acknowledges gas-grief awareness for `completeWithdrawalForUser` but incorrectly dismisses it as "non-impactful for ETH": [6](#0-5) 

There is no code restriction preventing ETH withdrawals from being processed through `completeWithdrawalForUser`, and the permanent-freeze scenario is distinct from (and more severe than) mere gas grief.

### Impact Explanation

After `unlockQueue` finalizes, the rsETH is irreversibly burned and the corresponding ETH is held in `LRTWithdrawalManager`. If the beneficiary address cannot accept ETH, that ETH is permanently locked with no admin escape hatch. This constitutes **permanent freezing of funds** (Critical).

### Likelihood Explanation

Smart-contract wallets, multisigs, and protocol-owned accounts that do not implement a `receive()` function are common depositors in LRT protocols. Any such account that initiates an ETH withdrawal will trigger this freeze once the operator runs `unlockQueue`. No special attacker capability is required beyond deploying or using a contract without a payable fallback.

### Recommendation

1. **Cap gas on the ETH transfer** (e.g., `call{value: amount, gas: 2300}`) so a malicious fallback cannot consume all gas, and treat a failed transfer as a pull-payment credit rather than a hard revert.
2. **Adopt a pull-payment pattern**: record the owed ETH amount per user and let them claim it separately, decoupling delivery failure from the accounting state.
3. **Add an admin ETH recovery function** that can force-credit a stuck withdrawal to an alternate address when the primary recipient is provably unable to receive ETH.

### Proof of Concept

1. Attacker deploys `MaliciousWallet` with:
   ```solidity
   receive() external payable { revert(); }
   ```
2. `MaliciousWallet` calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned; ETH is moved from `LRTUnstakingVault` into `LRTWithdrawalManager`. This transaction succeeds and is final.
4. `MaliciousWallet` calls `completeWithdrawal(ETH_TOKEN, "")`. `_processWithdrawalCompletion` reaches `_transferAsset` → `payable(MaliciousWallet).call{value: amount}("")` → `receive()` reverts → entire tx reverts.
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, MaliciousWallet, "")`. Same revert.
6. `sweepRemainingAssets(ETH_TOKEN)` reverts because `unlockedWithdrawalsCount[ETH_TOKEN] > 0`.
7. ETH is permanently locked. rsETH is permanently burned. Funds are frozen with no recovery path.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L191-191)
```text
    /// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
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
