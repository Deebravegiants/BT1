### Title
`_processWithdrawalCompletion` Uses Mutable Global `withdrawalDelayBlocks` After Unlock, Temporarily Freezing Already-Unlocked User Funds - (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager._processWithdrawalCompletion` re-evaluates the withdrawal delay using the current global `withdrawalDelayBlocks` at claim time, not the value that was in effect when the request was unlocked. Because `withdrawalDelayBlocks` is a mutable parameter that the LRT manager can increase at any time, a request that was legitimately unlocked (rsETH already burned, asset already redeemed from the vault) can be rendered uncompletable until the new, longer delay elapses — temporarily freezing user funds.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` has two distinct phases:

**Phase 1 — Unlock** (`unlockQueue` → `_unlockWithdrawalRequests`):

```solidity
// contracts/LRTWithdrawalManager.sol:795
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

When this check passes, the operator advances `nextLockedNonce[asset]`, burns the user's rsETH, and redeems the underlying asset from `LRTUnstakingVault` into the `LRTWithdrawalManager` contract.

**Phase 2 — Completion** (`completeWithdrawal` → `_processWithdrawalCompletion`):

```solidity
// contracts/LRTWithdrawalManager.sol:707
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
...
// contracts/LRTWithdrawalManager.sol:715
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

The first check confirms the request is unlocked (permanent). The second check re-reads the **current** `withdrawalDelayBlocks` — a global parameter that the LRT manager can change at any time via:

```solidity
// contracts/LRTWithdrawalManager.sol:338-344
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;
    ...
}
```

The `WithdrawalRequest` struct stores only `withdrawalStartBlock` — it does **not** snapshot the delay at unlock time:

```solidity
// contracts/interfaces/ILRTWithdrawalManager.sol:39-43
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
}
```

This means the "unlocked" state (nonce < `nextLockedNonce`) is permanent, but the ability to complete the withdrawal is not — it depends on a mutable global that can be changed after the fact.

**Contrast with `KernelDepositPool`**, which correctly snapshots the delay at initiation time:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:330
uint256 unlockTime = block.timestamp + withdrawalDelay;
withdrawals[withdrawalId] = Withdrawal({ ..., unlockTime: unlockTime, ... });
```

`KernelDepositPool.claimWithdrawal` then checks `block.timestamp < withdrawal.unlockTime` — immune to any future change of `withdrawalDelay`.

---

### Impact Explanation

When `withdrawalDelayBlocks` is increased after a request has been unlocked:

1. The user's rsETH has already been burned (irreversible).
2. The underlying asset has already been redeemed from `LRTUnstakingVault` and is sitting in `LRTWithdrawalManager`.
3. `_processWithdrawalCompletion` reverts with `WithdrawalDelayNotPassed` because `block.number < request.withdrawalStartBlock + NEW_withdrawalDelayBlocks`.
4. The user cannot receive their asset until `block.number >= withdrawalStartBlock + NEW_withdrawalDelayBlocks`, which can be up to 16 days from initiation.

The funds are not permanently lost (they remain in `LRTWithdrawalManager` and `sweepRemainingAssets` is blocked while `unlockedWithdrawalsCount > 0`), but they are **temporarily frozen** beyond the delay the user agreed to when initiating the withdrawal.

**Impact**: Temporary freezing of user funds — Medium per the allowed impact scope.

---

### Likelihood Explanation

The LRT manager role can call `setWithdrawalDelayBlocks` at any time for legitimate operational reasons (e.g., aligning with EigenLayer's own withdrawal delay changes after a protocol upgrade). This is not a malicious-admin scenario; it is a routine parameter update whose interaction with already-unlocked requests is unhandled. Likelihood is **Low** (requires a manager action that coincides with pending unlocked withdrawals), but the severity is meaningful because rsETH is already burned at that point.

---

### Recommendation

Snapshot `withdrawalDelayBlocks` at the time of **unlocking** (not initiation) and store it in the `WithdrawalRequest` struct. `_processWithdrawalCompletion` should then compare against the stored value:

```diff
 struct WithdrawalRequest {
     uint256 rsETHUnstaked;
     uint256 expectedAssetAmount;
     uint256 withdrawalStartBlock;
+    uint256 withdrawalDelayBlocksAtUnlock;
 }
```

In `_unlockWithdrawalRequests`, when advancing `nextLockedNonce`:

```diff
+ request.withdrawalDelayBlocksAtUnlock = withdrawalDelayBlocks;
  unlockedWithdrawalsCount[asset]++;
```

In `_processWithdrawalCompletion`:

```diff
- if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
+ if (block.number < request.withdrawalStartBlock + request.withdrawalDelayBlocksAtUnlock) revert WithdrawalDelayNotPassed();
```

This mirrors the correct pattern used in `KernelDepositPool`, where `unlockTime` is fixed at the time of the state transition.

---

### Proof of Concept

1. `withdrawalDelayBlocks` = `D` (e.g., 57,600 blocks ≈ 8 days).
2. User calls `initiateWithdrawal` at block `B`. rsETH is transferred to `LRTWithdrawalManager`.
3. At block `B + D`, operator calls `unlockQueue`:
   - `_unlockWithdrawalRequests` passes the check `block.number < B + D` → false.
   - rsETH is burned; asset is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`.
   - `nextLockedNonce[asset]` is incremented; `unlockedWithdrawalsCount[asset]++`.
4. LRT manager calls `setWithdrawalDelayBlocks(D')` where `D' > D` (e.g., `D' = 2D`).
5. User calls `completeWithdrawal` at block `B + D`:
   - First check passes: `usersFirstWithdrawalRequestNonce < nextLockedNonce[asset]` ✓
   - Second check **fails**: `block.number < request.withdrawalStartBlock + withdrawalDelayBlocks` → `B + D < B + D'` → **reverts `WithdrawalDelayNotPassed`**.
6. User's rsETH is already burned. Their asset is locked in `LRTWithdrawalManager` until block `B + D'`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L338-344)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L714-715)
```text
        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

**File:** contracts/LRTWithdrawalManager.sol (L793-795)
```text

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L39-43)
```text
    struct WithdrawalRequest {
        uint256 rsETHUnstaked;
        uint256 expectedAssetAmount;
        uint256 withdrawalStartBlock;
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L330-334)
```text
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
```
