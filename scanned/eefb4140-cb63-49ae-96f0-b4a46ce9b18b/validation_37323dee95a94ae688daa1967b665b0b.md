### Title
ETH Permanently Frozen When Withdrawal Recipient Is a Contract That Rejects ETH — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

A smart contract that initiates an ETH withdrawal can have its rsETH burned irreversibly during `unlockQueue`, yet find that every subsequent call to `completeWithdrawal` and `completeWithdrawalForUser` permanently reverts because `_transferAsset` unconditionally pushes ETH to the original `user` address with no alternative recipient path. The ETH is permanently frozen inside `LRTWithdrawalManager` with no admin recovery mechanism.

---

### Finding Description

**Step 1 — `initiateWithdrawal`**

`initiateWithdrawal` has no EOA check. Any smart contract can call it. rsETH is transferred from the caller to the withdrawal manager (not burned yet). [1](#0-0) 

**Step 2 — `unlockQueue` burns rsETH irreversibly**

When an operator calls `unlockQueue`, rsETH held by the contract is burned via `burnFrom(address(this), rsETHBurned)`. After this point, the rsETH is gone permanently. [2](#0-1) 

**Step 3 — `_transferAsset` hard-reverts on ETH send failure**

`_transferAsset` performs a bare low-level call to `payable(to)` and reverts with `EthTransferFailed` if the call returns `false`. If `to` is a contract whose `receive()` reverts, this always fails. [3](#0-2) 

**Step 4 — Both completion paths route ETH to the original `user` with no override**

`completeWithdrawal` passes `msg.sender` as `user`, and `completeWithdrawalForUser` passes the original requester address. Both call `_processWithdrawalCompletion(asset, user, ...)`, which calls `_transferAsset(asset, user, ...)`. There is no parameter to redirect ETH to a different recipient. [4](#0-3) [5](#0-4) 

The NatSpec on `completeWithdrawalForUser` even acknowledges this is not expected to be used for ETH: [6](#0-5) 

**Step 5 — No admin recovery path**

`sweepRemainingAssets` is gated by `hasUnlockedWithdrawals(asset)`. Since every `completeWithdrawal` call reverts atomically (restoring `unlockedWithdrawalsCount` and the nonce queue), the unlocked withdrawal count never reaches zero, permanently blocking the sweep. [7](#0-6) 

There is no admin function to forcibly cancel a withdrawal request and reclaim the ETH.

---

### Impact Explanation

**Critical. Permanent freezing of funds.**

- rsETH is burned in `unlockQueue` — irreversible.
- ETH is moved from the unstaking vault into `LRTWithdrawalManager` — it sits there.
- Every call to `completeWithdrawal` / `completeWithdrawalForUser` reverts.
- `sweepRemainingAssets` is permanently blocked.
- No admin escape hatch exists.

The user loses both their rsETH (burned) and their ETH (frozen), with zero recovery path.

---

### Likelihood Explanation

**Medium.** Smart contract wallets (multisigs, DAO treasuries, smart accounts) are common DeFi participants. A contract that does not implement `receive()` or has a reverting fallback — whether by design, upgrade, or bug — can trigger this. The protocol does not restrict `initiateWithdrawal` to EOAs. The scenario is realistic and requires no privileged access or external compromise.

---

### Recommendation

1. **Add a `recipient` parameter** to `completeWithdrawal` (or a separate `claimTo(address recipient)` function) so the user can redirect ETH to an address capable of receiving it.
2. **Alternatively**, wrap the ETH transfer in a pull-payment pattern: credit the user's claimable balance and let them pull it separately, avoiding push-to-contract failures.
3. **Add an admin escape hatch** (e.g., a manager-callable function) to cancel a stuck unlocked withdrawal, return the ETH to the treasury, and decrement `unlockedWithdrawalsCount`, so `sweepRemainingAssets` can eventually clear the contract.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RevertingReceiver {
    // Rejects all ETH
    receive() external payable { revert("no ETH"); }

    function doInitiate(address withdrawalManager, uint256 rsETHAmount) external {
        // Approve rsETH first, then initiate
        IERC20(rsETH).approve(withdrawalManager, rsETHAmount);
        ILRTWithdrawalManager(withdrawalManager)
            .initiateWithdrawal(ETH_TOKEN, rsETHAmount, "");
    }
}

// Test sequence (Foundry fork test):
// 1. Deploy RevertingReceiver, fund it with rsETH
// 2. Call doInitiate() → rsETH transferred to WithdrawalManager
// 3. Operator calls unlockQueue(ETH_TOKEN, ...) → rsETH burned, ETH moved in
// 4. vm.roll(block.number + withdrawalDelayBlocks + 1)
// 5. RevertingReceiver calls completeWithdrawal(ETH_TOKEN, "") → REVERTS (EthTransferFailed)
// 6. Operator calls completeWithdrawalForUser(ETH_TOKEN, address(revertingReceiver), "") → REVERTS
// 7. Assert: address(withdrawalManager).balance > 0 (ETH stuck)
// 8. Assert: rsETH.totalSupply() decreased (rsETH burned, unrecoverable)
// 9. Assert: sweepRemainingAssets(ETH_TOKEN) reverts with PendingWithdrawalsExist
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L183-204)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }

    /// @notice Allows operators to complete a user's withdrawal process
    /// @param asset The asset address the user wishes to withdraw
    /// @param user The address of the user whose withdrawal to complete
    /// @param referralId The referral identifier for tracking
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

**File:** contracts/LRTWithdrawalManager.sol (L734-734)
```text
        _transferAsset(asset, user, request.expectedAssetAmount);
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
