### Title
Push-Only Withdrawal Pattern Causes Permanent Fund Freeze After rsETH Is Burned — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` separates rsETH burning from asset delivery across two distinct operator/user steps. rsETH is irreversibly burned in `unlockQueue` before the user ever receives their underlying asset. If the subsequent `completeWithdrawal` push transfer permanently reverts — because the recipient is a contract that cannot accept ETH, or is blacklisted in an LST — the user's rsETH is gone and their entitled assets are frozen in the contract with no recovery path.

---

### Finding Description

The withdrawal lifecycle has three stages:

**Stage 1 — `initiateWithdrawal`**: The user transfers rsETH to `LRTWithdrawalManager`. rsETH is held, not yet burned. [1](#0-0) 

**Stage 2 — `unlockQueue` (operator-called)**: rsETH is burned and the corresponding asset amount is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`. This is irreversible. [2](#0-1) 

**Stage 3 — `completeWithdrawal` / `completeWithdrawalForUser`**: The asset is pushed to the user via `_transferAsset`. [3](#0-2) 

`_transferAsset` for ETH uses a raw `.call{value: amount}("")` and reverts on failure. For ERC20 LSTs it uses `safeTransfer`, which reverts on blacklisted recipients. [4](#0-3) 

If the push in Stage 3 always reverts, the entire `_processWithdrawalCompletion` transaction reverts, restoring the queue state — but the rsETH burned in Stage 2 is **not** restored. The assets sit in `LRTWithdrawalManager` indefinitely. [5](#0-4) 

There is no cancellation mechanism, no pull-pattern alternative, and no way for the user to recover their rsETH. The only escape valve, `sweepRemainingAssets`, is gated behind `!hasUnlockedWithdrawals(asset)`, which remains `true` as long as `unlockedWithdrawalsCount[asset] > 0` — which it will be, since the stuck request was counted in `unlockQueue` and can never be decremented. [6](#0-5) 

`completeWithdrawalForUser` (operator path) calls the same internal function and suffers the same failure. [7](#0-6) 

---

### Impact Explanation

A user whose address cannot receive the withdrawn asset (ETH or LST) loses both their rsETH (burned in Stage 2) and their entitled underlying asset (frozen in `LRTWithdrawalManager` with no recovery path). This constitutes **permanent freezing of funds**. The `unlockedWithdrawalsCount` counter for that asset can never reach zero, so `sweepRemainingAssets` is also permanently blocked for all other users of that asset, compounding the impact.

**Impact: Critical — Permanent freezing of funds.**

---

### Likelihood Explanation

Two realistic trigger conditions exist:

1. **ETH withdrawal to a non-payable contract**: Any smart contract (DeFi vault, DAO treasury, multisig without ETH receive support) that calls `initiateWithdrawal(ETH_TOKEN, ...)` but lacks a `receive()` function will permanently fail Stage 3. This is a realistic integration pattern.
2. **LST blacklist**: Tokens such as stETH implement operator-controlled transfer restrictions. If a user address is blacklisted in the LST after Stage 2 completes, `safeTransfer` will always revert.

Neither condition requires admin compromise or governance capture — both are reachable by an ordinary depositor/withdrawer interacting through the supported withdrawal path.

**Likelihood: Low** (edge-case conditions, but zero-trust recovery path makes impact irreversible when triggered).

---

### Recommendation

Implement a pull pattern for asset delivery. After `unlockQueue` redeems assets into `LRTWithdrawalManager`, record the entitled amount in a per-user mapping (e.g., `claimableAssets[user][asset]`) instead of pushing immediately. Expose a separate `claimAsset(asset)` function that lets the user pull their allocation at any time. This decouples rsETH burning from asset delivery and eliminates the permanent-freeze risk.

---

### Proof of Concept

```
1. Victim is a smart contract (no receive()) holding rsETH.
2. Victim calls initiateWithdrawal(ETH_TOKEN, 1e18, "").
   → rsETH transferred to LRTWithdrawalManager; withdrawal request queued.

3. Operator calls unlockQueue(ETH_TOKEN, ...).
   → _unlockWithdrawalRequests marks victim's request as unlocked,
     increments unlockedWithdrawalsCount[ETH_TOKEN].
   → Line 305: IRSETH.burnFrom(address(this), rsETHBurned)  ← rsETH destroyed.
   → Line 307: unstakingVault.redeem(ETH_TOKEN, amount)     ← ETH now in LRTWithdrawalManager.

4. Victim calls completeWithdrawal(ETH_TOKEN, "").
   → _processWithdrawalCompletion reaches line 734:
     _transferAsset(ETH_TOKEN, victim, amount)
     → payable(victim).call{value: amount}("") returns false
     → revert EthTransferFailed()
   → Entire tx reverts; queue state restored, but rsETH remains burned.

5. Victim retries indefinitely — always reverts.
   unlockedWithdrawalsCount[ETH_TOKEN] never reaches 0.
   sweepRemainingAssets reverts with PendingWithdrawalsExist().

Result: Victim's rsETH is permanently destroyed.
        ETH is permanently frozen in LRTWithdrawalManager.
        No on-chain recovery path exists.
```

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
