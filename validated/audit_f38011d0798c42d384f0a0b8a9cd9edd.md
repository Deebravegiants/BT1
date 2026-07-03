### Title
Direct Fee Transfer to Potentially-Zero `feeRecipient` Blocks Instant Withdrawals for ERC20 Assets - (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.instantWithdrawal` transfers the protocol fee directly to `feeRecipient` inline with the user's withdrawal, before the user receives their assets. When `instantWithdrawalFeeRecipient` is unset (zero, its default storage value) and `PROTOCOL_TREASURY` is not configured in `LRTConfig`, `feeRecipient` resolves to `address(0)`. For ERC20 assets (LSTs), `safeTransfer` to `address(0)` reverts, permanently blocking all instant withdrawals for those assets while `instantWithdrawalFee > 0`.

---

### Finding Description

In `instantWithdrawal`, the fee recipient is resolved as follows:

```solidity
address feeRecipient = instantWithdrawalFeeRecipient;
if (feeRecipient == address(0)) {
    feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
}
if (fee > 0) {
    _transferAsset(asset, feeRecipient, fee);   // ← fee sent BEFORE user receives assets
    emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
}
_transferAsset(asset, msg.sender, userAmount);  // ← user transfer comes after
``` [1](#0-0) 

`instantWithdrawalFeeRecipient` is initialized to `address(0)` (unset storage). `setInstantWithdrawalFeeRecipient` correctly guards against zero: [2](#0-1) 

However, the fallback path — `lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY)` — has no zero-address guard at the point of use. If `PROTOCOL_TREASURY` is not registered in `LRTConfig`, it returns `address(0)`, making `feeRecipient = address(0)`.

OpenZeppelin's `safeTransfer` (used by `_transferAsset` for ERC20 assets) reverts on transfer to `address(0)`. This causes the entire `instantWithdrawal` call to revert. Because rsETH is burned at line 229 before the fee transfer, the burn is also reverted (atomically), so no rsETH is permanently lost — but users are completely unable to execute instant withdrawals for any ERC20 asset while this condition holds. [3](#0-2) 

The same structural pattern (fee to treasury before user transfer) appears in `KernelMerkleDistributor._processClaim` and `KernelTop100MerkleDistributor.claim`, where `kernel.safeTransfer(protocolTreasury, fee)` executes before the user's token transfer: [4](#0-3) [5](#0-4) 

---

### Impact Explanation

**Temporary freezing of funds (Medium).** All instant withdrawals for ERC20 assets (LSTs such as stETH, cbETH) are blocked for every user while `instantWithdrawalFee > 0` and `feeRecipient` resolves to `address(0)`. Users who have already burned rsETH in the same transaction are protected by atomicity (the burn reverts too), but the instant-withdrawal path is entirely unavailable. The standard queued-withdrawal path is unaffected.

---

### Likelihood Explanation

Low. The condition requires two simultaneous states: (1) `instantWithdrawalFee` set to a non-zero value by LRTManager, and (2) `PROTOCOL_TREASURY` not yet registered in `LRTConfig` (or `instantWithdrawalFeeRecipient` not explicitly set). This is a realistic misconfiguration window during deployment or contract upgrades, not a deliberate attack.

---

### Recommendation

Add a zero-address guard on `feeRecipient` before the transfer, or adopt the withdrawal-pattern fix from the referenced report: accumulate fees in a state variable and let the treasury pull them separately, decoupling fee collection from user withdrawals.

```solidity
address feeRecipient = instantWithdrawalFeeRecipient;
if (feeRecipient == address(0)) {
    feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
}
require(feeRecipient != address(0), "Fee recipient not configured");
```

Or, preferably, accumulate fees and allow the treasury to withdraw them independently so a misconfigured recipient can never block user withdrawals.

---

### Proof of Concept

1. Deploy `LRTWithdrawalManager` without setting `PROTOCOL_TREASURY` in `LRTConfig` (or before it is set).
2. LRTManager calls `setInstantWithdrawalFee(50)` (0.5% fee).
3. `instantWithdrawalFeeRecipient` remains `address(0)` (never explicitly set).
4. User calls `instantWithdrawal(stETH, rsETHAmount, "")`.
5. Execution reaches line 243: `feeRecipient = lrtConfig.getContract(PROTOCOL_TREASURY)` → returns `address(0)`.
6. `fee > 0`, so `_transferAsset(stETH, address(0), fee)` is called.
7. OpenZeppelin `safeTransfer` reverts: `"ERC20: transfer to the zero address"`.
8. Entire transaction reverts. User cannot instant-withdraw. All other users calling `instantWithdrawal` for any ERC20 asset face the same revert. [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L229-250)
```text
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L384-387)
```text
    function setInstantWithdrawalFeeRecipient(address feeRecipient) external onlyLRTManager {
        UtilLib.checkNonZeroAddress(feeRecipient);
        instantWithdrawalFeeRecipient = feeRecipient;
        emit InstantWithdrawalFeeRecipientUpdated(feeRecipient);
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L331-336)
```text
        // Transfer tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
        kernel.safeTransfer(user, amountToSend);

```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
