### Title
FIFO Queue Head-of-Line Blocking via Oversized Withdrawal Request - (`contracts/LRTWithdrawalManager.sol`)

### Summary

The `_unlockWithdrawalRequests` loop processes the withdrawal queue strictly in FIFO order and breaks immediately when the vault balance is insufficient to cover the front-of-queue request. Because `initiateWithdrawal` validates the requested amount against the **total protocol TVL** (including assets staked in EigenLayer/validators), while `unlockQueue` sources `availableAssetAmount` from the **vault's idle balance only**, an attacker can legitimately queue a request whose `payoutAmount` far exceeds the vault's typical balance, stalling `nextLockedNonce` and blocking every subsequent user's withdrawal until the vault accumulates enough assets.

---

### Finding Description

**Entry point — `initiateWithdrawal`:**

`expectedAssetAmount` is validated against `getAvailableAssetAmount`:

```solidity
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
``` [1](#0-0) 

`getAvailableAssetAmount` returns `totalAssets - assetsCommitted`, where `totalAssets` is the **entire protocol TVL** — deposit pool + NDCs + EigenLayer strategies + unstaking vault:

```solidity
uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
``` [2](#0-1) 

`getTotalAssetDeposits` sums all locations including EigenLayer-staked and unstaking assets:

```solidity
return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
        + assetLyingUnstakingVault);
``` [3](#0-2) 

**Unlock gate — `_unlockWithdrawalRequests`:**

`availableAssetAmount` is sourced from `unstakingVault.balanceOf(asset)` — only the vault's **idle balance**:

```solidity
totalAvailableAssets: unstakingVault.balanceOf(asset)
``` [4](#0-3) 

The loop breaks immediately if the front-of-queue request exceeds this balance:

```solidity
if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
``` [5](#0-4) 

`nextLockedNonce` is only written back after the loop, so if the loop never advances, the nonce is frozen:

```solidity
nextLockedNonce[asset] = nextLockedNonce_;
``` [6](#0-5) 

**The gap:** In a live restaking protocol, the vast majority of assets are deployed in EigenLayer strategies/validators. The vault holds only a small fraction. An attacker can therefore pass the `initiateWithdrawal` guard with `expectedAssetAmount ≈ totalTVL`, while the vault balance is orders of magnitude smaller. There is no mechanism to skip or bypass a head-of-queue request that cannot be covered.

---

### Impact Explanation

Every user whose withdrawal request has a nonce **greater than** the attacker's is blocked from completing their withdrawal. Their rsETH was already transferred to the contract at `initiateWithdrawal` time:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
``` [7](#0-6) 

`completeWithdrawal` enforces the nonce ordering:

```solidity
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
``` [8](#0-7) 

Affected users cannot recover their rsETH or receive their assets until the vault accumulates enough to cover the attacker's request. The impact is **temporary freezing of funds** (Medium). It is not permanent because the protocol can, in principle, unstake validators to accumulate the required vault balance — but this may require extraordinary operational measures and could persist for a very long time depending on the attacker's request size relative to the vault's accumulation rate.

---

### Likelihood Explanation

- `initiateWithdrawal` is permissionless; any rsETH holder can call it.
- The attacker only needs to be at the current `nextLockedNonce` position (front of the unprocessed queue) — achievable for a new asset or by timing the submission.
- The attacker's cost is proportional to the blocking effect: they must lock their own rsETH in the contract, but they do not lose it — they merely delay their own withdrawal alongside everyone else's.
- No admin compromise, oracle manipulation, or governance capture is required.

---

### Recommendation

1. **Skip-on-insufficient-funds**: Instead of `break`ing when `availableAssetAmount < payoutAmount`, `continue` to the next nonce. This allows smaller requests behind a large one to be processed. Track skipped nonces separately so they are revisited when more assets arrive.
2. **Alternatively, cap `expectedAssetAmount` at unlock time** against the vault balance rather than total TVL, or enforce a per-request maximum relative to the vault's current balance.
3. **Add a maximum withdrawal amount** per request (e.g., a fraction of the vault's current balance) to prevent any single request from monopolizing the queue.

---

### Proof of Concept

```
Setup:
  - Protocol has 1000 stETH total TVL; vault holds 10 stETH idle.
  - assetsCommitted[stETH] = 0.

Step 1 (Attacker):
  - Attacker holds rsETH equivalent to 900 stETH.
  - Calls initiateWithdrawal(stETH, rsETH_for_900_stETH).
  - expectedAssetAmount = 900 stETH.
  - getAvailableAssetAmount = 1000 - 0 = 1000 stETH. Check passes.
  - Attacker gets nonce N (current nextLockedNonce).

Step 2 (Victims):
  - 100 users each call initiateWithdrawal for 1 stETH each.
  - They get nonces N+1 ... N+100.

Step 3 (Operator calls unlockQueue):
  - totalAvailableAssets = unstakingVault.balanceOf(stETH) = 10 stETH.
  - Loop starts at nonce N (attacker's request).
  - payoutAmount = 900 stETH > 10 stETH → break immediately.
  - nextLockedNonce stays at N.

Step 4 (Victims attempt completeWithdrawal):
  - All revert with WithdrawalLocked() because their nonces >= nextLockedNonce.

Assert: nextLockedNonce never advances past N; all 100 victims cannot withdraw.
Resolution requires vault to accumulate 900 stETH — nearly the entire protocol TVL.
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L170-170)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```

**File:** contracts/LRTWithdrawalManager.sol (L601-602)
```text
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
```

**File:** contracts/LRTWithdrawalManager.sol (L707-707)
```text
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/LRTWithdrawalManager.sol (L815-815)
```text
        nextLockedNonce[asset] = nextLockedNonce_;
```

**File:** contracts/LRTWithdrawalManager.sol (L849-849)
```text
            totalAvailableAssets: unstakingVault.balanceOf(asset)
```

**File:** contracts/LRTDepositPool.sol (L394-396)
```text
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
```
