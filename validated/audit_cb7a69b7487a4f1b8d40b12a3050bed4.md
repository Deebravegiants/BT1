### Title
Contract Without `receive()` Can Initiate ETH Withdrawal But Permanently Freeze Funds — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` implements a two-step withdrawal flow. Step 1 (`initiateWithdrawal`) accepts rsETH from any caller, including contracts that cannot receive native ETH. Step 2 (`completeWithdrawal`) delivers ETH via a raw `call{value}`, which permanently reverts for any contract without a `receive()` fallback. Because withdrawal requests are bound to `msg.sender` with no mechanism to redirect them, a contract depositor that lacks `receive()` will have its rsETH burned by the operator's `unlockQueue` call and then be permanently unable to collect the corresponding ETH.

---

### Finding Description

**Step 1 — `initiateWithdrawal` (permissive):**

`initiateWithdrawal` pulls rsETH from the caller via `safeTransferFrom` and records a withdrawal request keyed to `msg.sender`. This succeeds for any address, including contracts that have no `receive()` function. [1](#0-0) 

**Operator step — `unlockQueue` burns rsETH irrevocably:**

When an operator calls `unlockQueue`, the rsETH held by the manager is burned and ETH is redeemed from the unstaking vault. This happens in bulk across all queued requests; the operator cannot selectively skip one user's request without blocking all subsequent ones. [2](#0-1) 

**Step 2 — `completeWithdrawal` (restrictive):**

`_processWithdrawalCompletion` calls `_transferAsset`, which for ETH uses a raw `call{value}`. If the recipient contract has no `receive()` function, this call returns `false` and the function reverts with `EthTransferFailed`. [3](#0-2) 

**No redirect mechanism exists:**

`completeWithdrawalForUser` (the operator-assisted path) still routes the ETH to the original `user` address — it does not accept an alternative recipient. [4](#0-3) 

**`sweepRemainingAssets` is blocked:**

The ETH cannot be recovered via `sweepRemainingAssets` because that function requires `unlockedWithdrawalsCount[asset] == 0`. The stuck, unlocked-but-uncompletable request keeps this counter permanently non-zero. [5](#0-4) 

---

### Impact Explanation

A contract without `receive()` that holds rsETH and calls `initiateWithdrawal(ETH_TOKEN, ...)` will:

1. Transfer rsETH to the manager (irreversible from the user's side).
2. Have its rsETH burned by the operator's `unlockQueue` call.
3. Be permanently unable to collect the corresponding ETH — every call to `completeWithdrawal` or `completeWithdrawalForUser` reverts.
4. Indirectly block `sweepRemainingAssets` for the ETH asset, preventing protocol-level cleanup.

The user's rsETH is destroyed and the ETH is permanently frozen inside `LRTWithdrawalManager`. This matches **Critical — Permanent freezing of funds**.

---

### Likelihood Explanation

Smart-contract integrators (DeFi vaults, aggregators, multisigs without ETH receive hooks) routinely hold liquid restaking tokens and interact with withdrawal managers. Any such contract that omits a `receive()` function and requests an ETH withdrawal will trigger this path. No privileged role or special configuration is required — only a standard `initiateWithdrawal` call from an unprivileged depositor.

---

### Recommendation

Allow the caller to specify a separate `receiver` address at withdrawal-completion time, mirroring the alternative mitigation proposed in the referenced report:

```solidity
function completeWithdrawal(
    address asset,
    address receiver,   // <-- new parameter
    string calldata referralId
) external nonReentrant whenNotPaused {
    _processWithdrawalCompletion(asset, msg.sender, receiver, referralId);
}
```

`_processWithdrawalCompletion` would then send assets to `receiver` rather than hard-coding `user`. This lets a contract that cannot receive ETH designate an EOA or a contract with `receive()` to collect on its behalf, eliminating the permanent freeze.

---

### Proof of Concept

1. Deploy `VaultNoReceive` — a contract that holds rsETH but has no `receive()` function.
2. `VaultNoReceive` approves `LRTWithdrawalManager` and calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to the manager. ✅
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned; ETH is redeemed from the unstaking vault. ✅
4. `VaultNoReceive` calls `completeWithdrawal(ETH_TOKEN, "")`. `_transferAsset` executes `payable(VaultNoReceive).call{value: amount}("")` → returns `false` → reverts with `EthTransferFailed`. ❌
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, address(VaultNoReceive), "")`. Same revert. ❌
6. `unlockedWithdrawalsCount[ETH_TOKEN]` remains `> 0`; `sweepRemainingAssets(ETH_TOKEN)` reverts with `PendingWithdrawalsExist`. ETH is permanently frozen. [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-176)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

```

**File:** contracts/LRTWithdrawalManager.sol (L192-204)
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

**File:** contracts/LRTWithdrawalManager.sol (L876-880)
```text
    function _transferAsset(address asset, address to, uint256 amount) internal {
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
```
