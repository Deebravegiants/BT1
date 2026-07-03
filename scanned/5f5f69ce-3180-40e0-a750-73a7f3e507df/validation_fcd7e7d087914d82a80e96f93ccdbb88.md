### Title
Missing ETH Receivability Validation in `initiateWithdrawal` Causes Permanent Fund Freeze - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager::initiateWithdrawal` accepts rsETH from `msg.sender` for ETH-asset withdrawals without first verifying that `msg.sender` can receive native ETH. After the operator later calls `unlockQueue` — which irreversibly burns the rsETH held in the contract — any subsequent call to `completeWithdrawal` by a contract beneficiary that lacks a `payable` fallback/receive function will always revert. The user's rsETH is permanently destroyed and the corresponding ETH is permanently locked inside `LRTWithdrawalManager`.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is a three-step process:

**Step 1 — `initiateWithdrawal`:** The user (potentially a smart contract) calls this function. rsETH is pulled from `msg.sender` into the withdrawal manager. No check is performed to verify that `msg.sender` can receive ETH. [1](#0-0) 

**Step 2 — `unlockQueue` (operator-only):** The operator unlocks queued requests. rsETH held in the contract is **permanently burned** at line 305, and the corresponding ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager` at line 307. [2](#0-1) 

**Step 3 — `completeWithdrawal`:** The user calls this to receive their ETH. Internally, `_processWithdrawalCompletion` calls `_transferAsset`, which performs a low-level call: [3](#0-2) 

If `to` is a contract without a `payable` fallback or `receive` function, `payable(to).call{value: amount}("")` returns `false`, and the function reverts with `EthTransferFailed`. Because the entire transaction reverts, the withdrawal request record is restored — but the rsETH burned in Step 2 is **not** restored. The ETH remains in `LRTWithdrawalManager` indefinitely.

There is no admin escape hatch: `sweepRemainingAssets` is gated on `hasUnlockedWithdrawals(asset) == false`, but the stuck withdrawal keeps `unlockedWithdrawalsCount[asset] > 0`, blocking the sweep. [4](#0-3) 

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

Once `unlockQueue` burns the rsETH (Step 2), the user's claim is represented solely by the withdrawal request record. If `completeWithdrawal` always reverts for that user (because their contract cannot receive ETH), both the rsETH (burned) and the ETH (locked in the manager) are permanently unrecoverable without a contract upgrade. There is no alternative redemption path for the affected user.

---

### Likelihood Explanation

**Low-Medium.** The affected user must be a smart contract that:
1. Holds rsETH and calls `initiateWithdrawal` for the ETH asset, and
2. Does not implement a `payable` `receive()` or `fallback()` function.

This is a realistic scenario for protocol integrators, vaults, or any contract that interacts with the withdrawal manager programmatically without anticipating ETH receipt. The condition is not exotic — it mirrors exactly the class of contracts that caused the Ignite bug.

---

### Recommendation

Add a zero-value ETH receivability check inside `initiateWithdrawal` when `asset == LRTConstants.ETH_TOKEN`, mirroring the pattern used in the Ignite fix:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    (bool canReceive,) = msg.sender.call("");
    if (!canReceive) revert RecipientCannotReceiveETH();
}
```

This must be placed **before** the rsETH transfer so that no state change occurs if the check fails. Because this introduces an external call, also verify that `nonReentrant` (already present) covers this path — it does, since `initiateWithdrawal` already carries the modifier. [5](#0-4) 

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.15;

import "forge-std/Test.sol";

// Simulates a contract integrator that holds rsETH but has no receive() function
contract NoReceiveContract {
    // No receive() or fallback() — cannot accept ETH
}

contract TestFreezePoC is Test {
    address noReceive;

    function setUp() public {
        noReceive = address(new NoReceiveContract());
    }

    function test_cannotReceiveETH() external {
        // Zero-value call to a contract without receive() fails
        (bool success,) = noReceive.call{value: 0}("");
        assertEq(success, false); // Demonstrates the root condition

        // In the real protocol:
        // 1. NoReceiveContract calls initiateWithdrawal(ETH_TOKEN, rsETHAmount) — succeeds, rsETH locked
        // 2. Operator calls unlockQueue — rsETH burned, ETH moved to WithdrawalManager
        // 3. NoReceiveContract calls completeWithdrawal — _transferAsset reverts here
        // Result: rsETH gone, ETH permanently locked in LRTWithdrawalManager
    }
}
```

The `_transferAsset` call at line 878 of `LRTWithdrawalManager` will always revert for such a beneficiary, permanently freezing the ETH that was moved from `LRTUnstakingVault` in Step 2. [6](#0-5)

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
