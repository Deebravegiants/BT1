### Title
ETH Withdrawal Permanently Frozen When Recipient Contract Refuses ETH — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` uses a push-payment pattern to deliver ETH to withdrawing users. If the recipient address is a contract that reverts on ETH receipt, `completeWithdrawal` always reverts. Because rsETH is burned in a prior, separate `unlockQueue` transaction, the user's rsETH is permanently gone while their ETH is permanently stuck in the contract with no recovery path.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is split across two separate transactions:

**Step 1 — `unlockQueue` (operator-called):** Burns the user's rsETH and redeems the corresponding ETH from `LRTUnstakingVault` into the `LRTWithdrawalManager` contract. [1](#0-0) 

**Step 2 — `completeWithdrawal` (user-called):** Calls `_processWithdrawalCompletion`, which pushes ETH to the user via `_transferAsset`. [2](#0-1) 

The ETH transfer is a raw `call`:

```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
``` [3](#0-2) 

If `to` is a contract that reverts on ETH receipt, `_transferAsset` reverts, which rolls back the entire `_processWithdrawalCompletion` call. The withdrawal request remains in the queue, `unlockedWithdrawalsCount` is not decremented, and the ETH stays in the contract. [4](#0-3) 

The operator-callable `completeWithdrawalForUser` calls the same `_processWithdrawalCompletion` and suffers the same revert — it cannot rescue the user. [5](#0-4) 

The developer comment on `completeWithdrawalForUser` acknowledges the issue but dismisses it: *"Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH."* This is incorrect — the rsETH is already burned before the ETH push is attempted, making the freeze permanent. [6](#0-5) 

There is no admin recovery function in `LRTWithdrawalManager` for stuck ETH. `sweepRemainingAssets` is gated by `hasUnlockedWithdrawals(asset)`, which returns `true` while the stuck request exists, permanently blocking that path too. [7](#0-6) 

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

The user's rsETH is irreversibly burned in `unlockQueue`. The corresponding ETH is redeemed into `LRTWithdrawalManager` but can never be delivered to a recipient contract that refuses ETH. There is no alternative recipient, no address-change mechanism, and no admin recovery path. The ETH is permanently locked in the contract.

---

### Likelihood Explanation

**Medium.** The affected user must be a contract address (not an EOA). This is realistic for:
- Smart contract wallets (e.g., Gnosis Safe) that have a paused or broken `receive` function
- Contracts that conditionally accept ETH (e.g., require a specific caller or state)
- Protocol integrations that deposit rsETH on behalf of users and initiate withdrawals to a contract address

The user does not need to be malicious — a legitimate smart contract wallet with a bug in its fallback is sufficient to trigger permanent loss.

---

### Recommendation

Replace the push-payment pattern for ETH with a pull-payment (claim) model. Record the owed ETH amount in a mapping and allow the user (or any address they designate) to claim it separately:

```solidity
mapping(address user => uint256 amount) public pendingETHWithdrawals;

// In _processWithdrawalCompletion, instead of _transferAsset:
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

This mirrors the fix recommended in the external report: decouple settlement from delivery so that a recipient's refusal cannot freeze funds.

---

### Proof of Concept

1. Attacker deploys `MaliciousWallet` — a contract whose `receive()` function reverts by default.
2. `MaliciousWallet` calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned; ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`.
4. `MaliciousWallet` calls `completeWithdrawal(ETH_TOKEN, "")`. `_transferAsset` attempts `payable(MaliciousWallet).call{value: amount}("")`. `MaliciousWallet.receive()` reverts. The entire call reverts.
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, MaliciousWallet, "")`. Same revert.
6. rsETH is permanently burned. ETH is permanently locked in `LRTWithdrawalManager`. No recovery path exists. [8](#0-7) [2](#0-1)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L191-191)
```text
    /// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
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
