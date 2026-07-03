### Title
ETH Withdrawal Permanently Frozen When Recipient Smart Contract Cannot Receive ETH - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager._transferAsset` sends native ETH to the withdrawing user via a low-level `.call{value:}`. If the recipient is a smart contract whose `receive()` function is absent or reverts, the call fails, the transaction reverts, and the user's withdrawal is permanently unclaimable. Because rsETH is burned during `unlockQueue` (before the user ever calls `completeWithdrawal`), the user loses their rsETH with no path to recover the corresponding ETH.

---

### Finding Description

`_transferAsset` is the single ETH-dispatch helper used by every ETH withdrawal path in the contract:

```solidity
// contracts/LRTWithdrawalManager.sol  L876-L883
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
``` [1](#0-0) 

It is called from `_processWithdrawalCompletion`, which is invoked by both `completeWithdrawal` (user-triggered) and `completeWithdrawalForUser` (operator-triggered):

```solidity
// L734
_transferAsset(asset, user, request.expectedAssetAmount);
``` [2](#0-1) 

The critical ordering problem is in `unlockQueue`. rsETH is **burned** and ETH is **redeemed from the unstaking vault into the withdrawal manager** before any user ever calls `completeWithdrawal`:

```solidity
// L305-L307
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [3](#0-2) 

After `unlockQueue` executes:
- The user's rsETH is **permanently burned**.
- The corresponding ETH now sits inside `LRTWithdrawalManager`.

When the user (a smart contract without a payable `receive()`) calls `completeWithdrawal`, `_transferAsset` attempts `.call{value:}` to the user's address. The call fails, the entire transaction reverts, and the withdrawal request is restored to the queue. Every subsequent attempt — including `completeWithdrawalForUser` by an operator — also sends ETH to the same non-accepting address and reverts identically.

The `sweepRemainingAssets` escape hatch is blocked because it requires `hasUnlockedWithdrawals(asset) == false`:

```solidity
// L403
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
``` [4](#0-3) 

As long as the stuck withdrawal exists, `unlockedWithdrawalsCount[asset] > 0`, so the sweep is permanently blocked for that asset. There is no other admin rescue path for ETH held in the withdrawal manager.

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

The user's rsETH is burned irreversibly during `unlockQueue`. The ETH equivalent is locked inside `LRTWithdrawalManager` with no reachable code path to deliver it to an alternative address or return it to the user. The funds are permanently lost to the user and inaccessible to the protocol.

---

### Likelihood Explanation

**Medium.**

Smart-contract callers of the withdrawal system are realistic and common in DeFi: multisig treasuries (Gnosis Safe), DAO vaults, yield aggregators, and wrapper contracts routinely hold rsETH and initiate withdrawals. Many such contracts lack a `receive()` function or have one that reverts (e.g., to prevent accidental ETH acceptance). A single such caller permanently bricks their own withdrawal and, via the `sweepRemainingAssets` guard, can also delay treasury sweeps for the entire ETH asset queue.

---

### Recommendation

1. **Allow the user to specify an alternative ETH recipient** at `completeWithdrawal` time, or store a user-configurable `ethRecipient` address at `initiateWithdrawal` time.
2. **Alternatively**, if the ETH transfer fails, do not revert — instead credit the amount to a claimable mapping so the user can pull it later via a separate `claimETH()` function (pull-over-push pattern).
3. **Do not burn rsETH in `unlockQueue`** until the ETH has been successfully delivered, or implement a refund path that re-mints rsETH if delivery permanently fails.

---

### Proof of Concept

1. Smart-contract wallet `VaultA` (no `receive()`) holds rsETH and calls:
   ```solidity
   withdrawalManager.initiateWithdrawal(ETH_TOKEN, 1e18, "ref");
   ```
   rsETH is transferred to `LRTWithdrawalManager`. [5](#0-4) 

2. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned; ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`. [3](#0-2) 

3. `VaultA` calls `completeWithdrawal(ETH_TOKEN, "ref")`. Inside `_processWithdrawalCompletion`, `_transferAsset` executes:
   ```solidity
   (bool sent,) = payable(VaultA).call{ value: amount }("");
   // sent == false → revert EthTransferFailed
   ```
   Transaction reverts; state is fully restored. [6](#0-5) 

4. Operator calls `completeWithdrawalForUser(ETH_TOKEN, VaultA, "ref")` — same ETH destination, same revert. [7](#0-6) 

5. `unlockedWithdrawalsCount[ETH_TOKEN] > 0` forever → `sweepRemainingAssets` reverts for all callers. [4](#0-3) 

`VaultA`'s rsETH is gone; the ETH is permanently locked in `LRTWithdrawalManager` with no recovery path.

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

**File:** contracts/LRTWithdrawalManager.sol (L403-403)
```text
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
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
