### Title
ETH Withdrawal to Non-Payable Contract Address Permanently Freezes Funds — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

A smart contract that holds rsETH and lacks a `receive()` or `fallback()` function can call `initiateWithdrawal` for ETH. After an operator calls `unlockQueue` (which irreversibly burns the rsETH and moves ETH into `LRTWithdrawalManager`), every subsequent attempt to complete the withdrawal — via either `completeWithdrawal` or `completeWithdrawalForUser` — permanently reverts. The ETH is frozen inside `LRTWithdrawalManager` with no on-chain recovery path.

---

### Finding Description

**Step 1 — Initiation.** A non-payable smart contract calls `initiateWithdrawal(ETH_TOKEN, amount, ...)`. rsETH is pulled from the caller and the request is registered under `msg.sender`. [1](#0-0) 

**Step 2 — Unlock (point of no return).** An operator calls `unlockQueue`. This burns the rsETH held by the withdrawal manager and redeems the corresponding ETH from the unstaking vault into `LRTWithdrawalManager`. Both actions are irreversible. [2](#0-1) 

**Step 3 — Completion always reverts.** `_processWithdrawalCompletion` unconditionally calls `_transferAsset(asset, user, ...)`, where `user` is always the original requesting address. [3](#0-2) 

`_transferAsset` uses a low-level call. If `to` is a non-payable contract, `sent` is `false` and the function reverts with `EthTransferFailed`. [4](#0-3) 

**Step 4 — `completeWithdrawalForUser` provides no escape.** The operator-callable variant also routes ETH to the same `user` address — it cannot redirect to a different recipient. [5](#0-4) 

The NatDoc comment even acknowledges this path is "not expected to be used for ETH," but provides no alternative. [6](#0-5) 

**Step 5 — No admin recovery path exists.** `sweepRemainingAssets` is gated by `hasUnlockedWithdrawals(asset)`, which returns `true` as long as the stuck withdrawal exists, so it reverts with `PendingWithdrawalsExist`. There is no cancel, rescue, or recipient-change function anywhere in the contract. [7](#0-6) 

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

- The rsETH is burned during `unlockQueue` and cannot be recovered.
- The corresponding ETH is held in `LRTWithdrawalManager` and can never be transferred out (every completion call reverts; sweep is blocked; no rescue function exists).
- Both assets are permanently lost to the user with zero on-chain recourse.

---

### Likelihood Explanation

**Medium-High.** Smart contracts routinely hold and manage liquid staking tokens (multisigs, DAOs, DeFi vaults, yield aggregators). Many such contracts intentionally omit `receive()`/`fallback()` to prevent accidental ETH acceptance. Any such contract that calls `initiateWithdrawal` for ETH triggers this path deterministically. No special permissions, front-running, or external compromise is required.

---

### Recommendation

1. **Preferred fix:** Add a `recipient` parameter to `initiateWithdrawal` (defaulting to `msg.sender`) and store it in `WithdrawalRequest`. `_processWithdrawalCompletion` then sends ETH to the stored recipient rather than the requesting address.
2. **Minimal fix:** Add an admin/operator function that allows updating the recipient address of an unlocked-but-uncompleted withdrawal request, enabling recovery when the original address is non-payable.
3. **Complementary:** Remove or correct the misleading NatDoc on `completeWithdrawalForUser` that implies ETH cases are safe to ignore.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// NonPayableWithdrawer: no receive() / fallback()
contract NonPayableWithdrawer {
    ILRTWithdrawalManager wm;
    IERC20 rsETH;

    constructor(address _wm, address _rsETH) {
        wm = ILRTWithdrawalManager(_wm);
        rsETH = IERC20(_rsETH);
    }

    function doInitiate(uint256 amount) external {
        rsETH.approve(address(wm), amount);
        wm.initiateWithdrawal(ETH_TOKEN, amount, "");
    }
}

// Test (Foundry, fork or local):
function testPermanentFreeze() public {
    // 1. Deploy non-payable contract and fund it with rsETH
    NonPayableWithdrawer victim = new NonPayableWithdrawer(address(wm), address(rsETH));
    deal(address(rsETH), address(victim), 1 ether);

    // 2. Initiate withdrawal from non-payable contract
    vm.prank(address(victim));
    victim.doInitiate(1 ether);

    // 3. Operator unlocks the queue — rsETH burned, ETH moved into LRTWithdrawalManager
    vm.prank(operator);
    wm.unlockQueue(ETH_TOKEN, type(uint256).max, 0, 0, type(uint256).max, type(uint256).max);

    // 4. completeWithdrawal always reverts
    vm.prank(address(victim));
    vm.expectRevert(LRTWithdrawalManager.EthTransferFailed.selector);
    wm.completeWithdrawal(ETH_TOKEN, "");

    // 5. completeWithdrawalForUser also always reverts
    vm.prank(operator);
    vm.expectRevert(LRTWithdrawalManager.EthTransferFailed.selector);
    wm.completeWithdrawalForUser(ETH_TOKEN, address(victim), "");

    // 6. ETH is permanently stuck — rsETH already burned
    assertGt(address(wm).balance, 0); // ETH locked forever
    assertEq(rsETH.balanceOf(address(victim)), 0); // rsETH gone
}
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-176)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

```

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

**File:** contracts/LRTWithdrawalManager.sol (L403-403)
```text
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

**File:** contracts/LRTWithdrawalManager.sol (L734-734)
```text
        _transferAsset(asset, user, request.expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L877-879)
```text
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
```
