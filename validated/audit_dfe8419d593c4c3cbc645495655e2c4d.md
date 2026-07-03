### Title
ETH Instant Withdrawal Permanently DoS'd When Fee Recipient Cannot Receive ETH - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

In `LRTWithdrawalManager.instantWithdrawal()`, when the asset is native ETH and a fee is charged, the fee is forwarded to `instantWithdrawalFeeRecipient` (or the default `PROTOCOL_TREASURY`) via a raw `.call{value}`. If that recipient is a contract without a `receive()` or `fallback()` function, the transfer reverts and **every** ETH instant withdrawal is permanently blocked for all users.

---

### Finding Description

`instantWithdrawal` is a public, unprivileged function that lets any rsETH holder burn their tokens and receive ETH immediately. When `fee > 0`, the code routes the fee to `feeRecipient` before sending the user their share:

```solidity
// contracts/LRTWithdrawalManager.sol  lines 240-250
address feeRecipient = instantWithdrawalFeeRecipient;
if (feeRecipient == address(0)) {
    feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
}
if (fee > 0) {
    _transferAsset(asset, feeRecipient, fee);   // <-- reverts here
    emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
}
_transferAsset(asset, msg.sender, userAmount);
``` [1](#0-0) 

The internal helper `_transferAsset` sends ETH with a raw low-level call and hard-reverts on failure:

```solidity
// contracts/LRTWithdrawalManager.sol  lines 876-883
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
``` [2](#0-1) 

`instantWithdrawalFeeRecipient` is an arbitrary address set by the LRT Manager:

```solidity
// contracts/LRTWithdrawalManager.sol  lines 384-388
function setInstantWithdrawalFeeRecipient(address feeRecipient) external onlyLRTManager {
    UtilLib.checkNonZeroAddress(feeRecipient);
    instantWithdrawalFeeRecipient = feeRecipient;
    emit InstantWithdrawalFeeRecipientUpdated(feeRecipient);
}
``` [3](#0-2) 

When `instantWithdrawalFeeRecipient` is zero (the default), the fallback is `PROTOCOL_TREASURY` from `lrtConfig` — also an arbitrary address. Neither address is validated to be capable of receiving ETH.

If either address is a contract without a `receive()` / `fallback()` (e.g., a DAO treasury, a pure ERC-20 multisig, or any contract that explicitly reverts on ETH receipt), the `_transferAsset` call reverts with `EthTransferFailed`, rolling back the entire `instantWithdrawal` transaction.

---

### Impact Explanation

**Temporary (potentially permanent) freezing of funds.**

Every user who calls `instantWithdrawal` with `asset == ETH_TOKEN` while `instantWithdrawalFee > 0` will have their transaction revert. The rsETH is burned at the start of the function:

```solidity
// contracts/LRTWithdrawalManager.sol  line 229
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
``` [4](#0-3) 

Because the burn happens before the fee transfer, a revert on the fee transfer rolls back the burn too (same transaction), so no rsETH is lost. However, the instant-withdrawal path is completely blocked for all ETH withdrawers until the fee recipient is changed to an ETH-accepting address. Users are forced to wait for the standard queued-withdrawal path (8-day delay), constituting a temporary freeze of their ability to access funds on demand.

---

### Likelihood Explanation

Protocol fee recipients and treasuries are routinely implemented as smart contracts — Gnosis Safe multisigs, DAO governance contracts, or custom treasury contracts. Many such contracts are deployed to handle ERC-20 tokens only and do not include a `receive()` function. The LRT Manager can set `instantWithdrawalFeeRecipient` to any non-zero address without any on-chain check that the address can accept ETH. The default fallback to `PROTOCOL_TREASURY` carries the same risk. A single misconfiguration silently breaks ETH instant withdrawals for the entire user base.

---

### Recommendation

1. **Wrap ETH to WETH before sending fees.** Convert the fee amount to WETH and transfer the ERC-20 token instead of raw ETH. This is the well-known "send WETH instead" pattern referenced in the original report.
2. **Alternatively, use a pull-payment pattern.** Accumulate fees in the contract and let the fee recipient claim them via a separate `claimFees()` function, removing the push-ETH dependency from the user-facing withdrawal path.
3. **At minimum, validate the recipient.** Before setting `instantWithdrawalFeeRecipient`, perform a small test transfer or require the address to implement a known interface that guarantees ETH acceptance.

---

### Proof of Concept

1. Manager calls `setInstantWithdrawalFee(100)` (1%) and `setInstantWithdrawalFeeRecipient(address(new EthRejecter()))` where `EthRejecter` has `receive() external payable { revert(); }`.
2. Any user calls `instantWithdrawal(ETH_TOKEN, rsETHAmount, "")`.
3. Inside `instantWithdrawal`, `fee > 0`, so `_transferAsset(ETH_TOKEN, feeRecipient, fee)` is called.
4. `payable(feeRecipient).call{value: fee}("")` returns `(false, ...)`.
5. `if (!sent) revert EthTransferFailed()` fires.
6. The entire transaction reverts; the user cannot withdraw ETH instantly.
7. The same outcome occurs with the default `PROTOCOL_TREASURY` path if that address is a non-ETH-accepting contract. [2](#0-1) [1](#0-0)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L229-229)
```text
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L240-252)
```text
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
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L384-388)
```text
    function setInstantWithdrawalFeeRecipient(address feeRecipient) external onlyLRTManager {
        UtilLib.checkNonZeroAddress(feeRecipient);
        instantWithdrawalFeeRecipient = feeRecipient;
        emit InstantWithdrawalFeeRecipientUpdated(feeRecipient);
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
