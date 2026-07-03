### Title
Permanent ETH Freezing for Smart Contract Withdrawers with Reverting `receive()` — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

A smart contract user that initiates an ETH withdrawal, has its rsETH burned during `unlockQueue`, and whose `receive()` function always reverts will find that every subsequent call to `completeWithdrawal` and `completeWithdrawalForUser` permanently reverts. The ETH is locked in `LRTWithdrawalManager` with no admin rescue path.

---

### Finding Description

The withdrawal flow has three distinct phases:

**Phase 1 — `initiateWithdrawal`**: rsETH is pulled from the user into `LRTWithdrawalManager`. [1](#0-0) 

**Phase 2 — `unlockQueue`**: rsETH held by the contract is burned permanently and the corresponding ETH is redeemed from the unstaking vault into `LRTWithdrawalManager`. [2](#0-1) 

**Phase 3 — `completeWithdrawal` / `completeWithdrawalForUser`**: Both routes call `_processWithdrawalCompletion`, which ends with `_transferAsset(asset, user, request.expectedAssetAmount)`. [3](#0-2) 

`_transferAsset` for ETH uses a bare low-level call and hard-reverts on failure: [4](#0-3) 

Because the revert unwinds the entire transaction, the `popFront`, `delete withdrawalRequests`, and `unlockedWithdrawalsCount--` state changes are also rolled back. The request remains in the unlocked queue forever, but every attempt to claim it reverts again — an infinite loop.

`completeWithdrawalForUser` does **not** redirect ETH to the calling operator; it still sends to `user`: [5](#0-4) 

The developer comment on that function even acknowledges the ETH issue but incorrectly dismisses it as non-impactful: [6](#0-5) 

**No recovery path exists:**
- `sweepRemainingAssets` requires `!hasUnlockedWithdrawals(asset)`, which is never satisfied while the stuck request exists. [7](#0-6) 

- There is no admin function to redirect a pending withdrawal to an alternate address.
- `emergencyWithdrawFromAave` only handles Aave-deposited ETH, not idle contract ETH. [8](#0-7) 

---

### Impact Explanation

**Critical — Permanent freezing of funds.** The user's rsETH is burned (supply reduced, value destroyed for the user) and the corresponding ETH is permanently locked inside `LRTWithdrawalManager` with no mechanism to recover it. The invariant "every unlocked withdrawal must be claimable by its owner" is broken.

---

### Likelihood Explanation

Smart contracts routinely hold and manage LST/LRT positions: multisigs (Gnosis Safe), vaults, DAOs, and yield aggregators. Many of these do not implement `receive()` or implement it with a revert guard. Any such contract that calls `initiateWithdrawal` for ETH is permanently affected once `unlockQueue` processes its request. No privileged action or unusual configuration is required — only a normal user interaction.

---

### Recommendation

Replace the hard-revert pattern in `_transferAsset` with a pull-payment model for ETH:

1. Instead of pushing ETH in `_processWithdrawalCompletion`, credit `pendingEthWithdrawals[user] += amount` and emit an event.
2. Add a separate `claimEth()` function that lets the user (or a nominated recipient) pull their ETH.
3. Alternatively, allow `completeWithdrawalForUser` to accept an explicit `recipient` address so an operator can redirect ETH to an EOA controlled by the same user.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract RevertingReceiver {
    // Always reverts on ETH receipt
    receive() external payable { revert("no ETH"); }

    function doInitiate(address wm, address asset, uint256 amt) external {
        IERC20(rsETH).approve(wm, amt);
        ILRTWithdrawalManager(wm).initiateWithdrawal(asset, amt, "");
    }

    function doComplete(address wm, address asset) external {
        // This will always revert with EthTransferFailed
        ILRTWithdrawalManager(wm).completeWithdrawal(asset, "");
    }
}

// Test (Foundry fork test):
// 1. Deploy RevertingReceiver, fund with rsETH
// 2. receiver.doInitiate(wm, ETH_TOKEN, 1 ether rsETH)
// 3. operator calls unlockQueue(ETH_TOKEN, ...) → rsETH burned, ETH in WM
// 4. receiver.doComplete(wm, ETH_TOKEN) → reverts with EthTransferFailed every time
// 5. operator calls completeWithdrawalForUser(ETH_TOKEN, address(receiver), "") → same revert
// 6. Assert: rsETH totalSupply decreased, WM ETH balance unchanged, no recovery path
``` [4](#0-3) [9](#0-8)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L191-191)
```text
    /// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
```

**File:** contracts/LRTWithdrawalManager.sol (L202-202)
```text
        _processWithdrawalCompletion(asset, user, referralId);
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L403-403)
```text
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

**File:** contracts/LRTWithdrawalManager.sol (L551-563)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
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
