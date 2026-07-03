Audit Report

## Title
ETH Transfer Failure to Reverting-Receive Contract Permanently Freezes User Withdrawal Queue — (`contracts/LRTWithdrawalManager.sol`)

## Summary

In `_processWithdrawalCompletion`, `popFront()` is called before `_transferAsset()`. If the ETH push-transfer to a contract recipient reverts, the entire transaction rolls back — restoring the nonce to the front of the queue. Because rsETH is already burned in a prior, separate `unlockQueue` transaction, the user permanently loses their rsETH and can never receive the corresponding ETH. No admin or operator path exists to skip the stuck nonce or redirect the funds.

## Finding Description

`_processWithdrawalCompletion` executes in this order:

1. `popFront()` removes the front nonce from `userAssociatedNonces[asset][user]` (line 705)
2. `delete withdrawalRequests[requestId]` (line 712)
3. `unlockedWithdrawalsCount[asset]--` (line 717)
4. `_transferAsset(asset, user, request.expectedAssetAmount)` (line 734) [1](#0-0) 

`_transferAsset` for ETH performs a low-level call and reverts on failure:

```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
``` [2](#0-1) 

If `to` is a contract whose `receive()` reverts, `sent == false` and `EthTransferFailed()` is thrown. This reverts the entire transaction, rolling back all four state mutations above — including `popFront()`. The nonce is restored to the front of the queue.

rsETH is burned in a **prior, separate** `unlockQueue` transaction:

```solidity
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [3](#0-2) 

By the time `completeWithdrawal` is called, the rsETH is already gone and the ETH already sits in the withdrawal manager. Every subsequent call to complete the withdrawal reverts identically. The operator-callable `completeWithdrawalForUser` routes through the same `_processWithdrawalCompletion` and suffers the identical revert. [4](#0-3) 

The NatSpec on `completeWithdrawalForUser` (line 191) states "potential gas grief scenarios are non-impactful for ETH," which is incorrect: the impact is not gas grief but permanent fund loss, and it affects the user's own `completeWithdrawal` call equally. [5](#0-4) 

No rescue path exists: `sweepRemainingAssets` requires `hasUnlockedWithdrawals(asset) == false`, but since the revert restores `unlockedWithdrawalsCount`, this condition is never met for the stuck asset. There is no skip-nonce, redirect-recipient, or admin-rescue function. [6](#0-5) 

## Impact Explanation

- The user's rsETH is permanently burned (occurred in `unlockQueue`).
- The corresponding ETH is permanently inaccessible to the user (stuck in the withdrawal manager).
- The front nonce is never consumed, so all subsequent ETH withdrawal requests for this user are also permanently blocked (FIFO queue enforced by `popFront`).

**Impact: Critical — Permanent freezing of funds**, matching the allowed scope.

## Likelihood Explanation

Any smart contract wallet (multisig, DAO treasury, proxy without a `receive` function) that initiates an ETH withdrawal triggers this path. No special permissions are required; `initiateWithdrawal` is open to any address. The condition is deterministic and repeatable — every completion attempt reverts identically. Smart contract depositors without ETH receive capability are a realistic and common pattern for institutional and DAO users. **Likelihood: Medium.**

## Recommendation

Replace the push-payment model for ETH with a pull-payment (withdrawal) pattern: store the owed ETH amount in a claimable mapping and let the user pull it in a separate transaction. Alternatively, wrap ETH as WETH before transferring to the recipient, which never reverts on receipt. At minimum, if the ETH transfer fails, do not revert the entire transaction — instead consume the nonce, emit an event, and store the owed amount in a separate claimable mapping so the user can retrieve it via an alternative path.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RejectETH {
    receive() external payable { revert("no ETH"); }

    function initiateWithdrawal(address wm, address ethToken, uint256 rsETHAmount) external {
        IERC20(rsETH).approve(wm, rsETHAmount);
        ILRTWithdrawalManager(wm).initiateWithdrawal(ethToken, rsETHAmount, "");
    }

    function tryComplete(address wm, address ethToken) external {
        // Always reverts with EthTransferFailed
        ILRTWithdrawalManager(wm).completeWithdrawal(ethToken, "");
    }
}

// Test sequence (Foundry fork test):
// 1. Deploy RejectETH, fund with rsETH
// 2. RejectETH.initiateWithdrawal(ETH, amount) — succeeds, rsETH locked in manager
// 3. operator calls unlockQueue(ETH, ...) — rsETH burned, ETH moved to manager
// 4. RejectETH.tryComplete(ETH) — reverts with EthTransferFailed every time
// 5. Assert: userAssociatedNonces[ETH][RejectETH].front() == original nonce (never consumed)
// 6. Assert: withdrawalRequests[requestId] still exists (restored by revert)
// 7. Assert: rsETH balance of manager == 0 (already burned, unrecoverable)
// 8. Assert: address(withdrawalManager).balance >= amount (ETH stuck forever)
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L191-191)
```text
    /// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
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

**File:** contracts/LRTWithdrawalManager.sol (L705-734)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L877-879)
```text
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
```
