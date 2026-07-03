Audit Report

## Title
`instantWithdrawal` Drains `LRTUnstakingVault` Without Respecting `assetsCommitted`, Freezing Queued Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

## Summary
`LRTWithdrawalManager` maintains two independent accounting variables: `assetsCommitted[asset]` (tracking assets promised to queued withdrawal users) and `queuedWithdrawalsBuffer[asset]` (a manually-set vault-side reserve). The `instantWithdrawal` function checks only `queuedWithdrawalsBuffer` — which defaults to zero — and never reads or decrements `assetsCommitted`. An unprivileged rsETH holder can therefore drain the entire `LRTUnstakingVault` balance, including assets already committed to queued withdrawal users, causing `unlockQueue` to revert and leaving those users' rsETH locked in the withdrawal manager until the vault is manually replenished.

## Finding Description

**Queued path — `initiateWithdrawal`** ( [1](#0-0) ):
Each queued request increments `assetsCommitted[asset]` by the expected payout, reserving that amount against the total protocol asset balance via `getAvailableAssetAmount`.

**Instant path — `instantWithdrawal`** ( [2](#0-1) ):
The only guard is `assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)`. This function returns `vaultBalance - queuedWithdrawalsBuffer[asset]` ( [3](#0-2) ). `queuedWithdrawalsBuffer` is a `mapping` that defaults to zero for every asset ( [4](#0-3) ), so the check reduces to `assetAmountUnlocked > vaultBalance`. `assetsCommitted` is never read or modified in this path.

**Queue fulfillment — `unlockQueue`**:
`_createUnlockParams` sets `totalAvailableAssets = unstakingVault.balanceOf(asset)` ( [5](#0-4) ). If the vault has been drained by instant withdrawals, `totalAvailableAssets == 0` and `unlockQueue` reverts immediately with `AmountMustBeGreaterThanZero` ( [6](#0-5) ), before `_unlockWithdrawalRequests` is ever called. Even with a non-zero but insufficient vault balance, `_unlockWithdrawalRequests` breaks at the first request it cannot cover ( [7](#0-6) ). `assetsCommitted` is only decremented inside `_unlockWithdrawalRequests` ( [8](#0-7) ), so it remains inflated, creating the desync: `assetsCommitted[asset] > LRTUnstakingVault.balanceOf(asset)`.

The two accounting variables are never reconciled: `assetsCommitted` lives in `LRTWithdrawalManager` and is updated only by the queued path; `queuedWithdrawalsBuffer` lives in `LRTUnstakingVault` and is set manually by an operator. There is no mechanism that automatically sets `queuedWithdrawalsBuffer` to at least `assetsCommitted`.

## Impact Explanation
Users who called `initiateWithdrawal` have already transferred their rsETH to `LRTWithdrawalManager`. If the vault is subsequently drained by instant withdrawers, `unlockQueue` cannot process their requests. Their rsETH remains locked in the contract until an operator replenishes the vault by completing a new EigenLayer unstaking cycle — a multi-day, operator-dependent process. This is a **temporary freezing of funds (Medium)**.

## Likelihood Explanation
- `isInstantWithdrawalEnabled[asset]` must be `true` — a realistic production configuration.
- `queuedWithdrawalsBuffer[asset]` defaults to `0` for every asset; protection requires an explicit operator action that is not enforced by the protocol.
- Any rsETH holder can call `instantWithdrawal` permissionlessly once the feature is enabled.
- No special knowledge or privileged access is required; the attacker simply calls `instantWithdrawal` for the full vault balance while queued requests exist.

**Likelihood: Medium.**

## Recommendation
Synchronize the two accounting mechanisms. In `instantWithdrawal`, add a check that the requested amount does not exceed `getAvailableAssetAmount(asset)` minus the portion already committed to queued users, or make `getAssetsAvailableForInstantWithdrawal` automatically use `max(queuedWithdrawalsBuffer[asset], ILRTWithdrawalManager.assetsCommitted(asset))` as the reserved amount. The single source of truth for "how much of the vault is reserved for queued users" should be `assetsCommitted`, not a separately maintained manual buffer.

## Proof of Concept

```
State:
  LRTUnstakingVault holds 100 ETH
  queuedWithdrawalsBuffer[ETH] = 0  (default)
  isInstantWithdrawalEnabled[ETH] = true

1. Alice calls initiateWithdrawal(ETH, rsETH_A)
   → assetsCommitted[ETH] += 80 ETH
   → Alice's rsETH (worth 80 ETH) locked in LRTWithdrawalManager

2. Bob calls instantWithdrawal(ETH, rsETH_B)
   → getAssetsAvailableForInstantWithdrawal = 100 - 0 = 100 ETH  ✓
   → unstakingVault.redeem(ETH, 100 ETH)  — vault drained to 0
   → assetsCommitted[ETH] unchanged = 80 ETH

3. Operator calls unlockQueue(ETH, ...)
   → totalAvailableAssets = unstakingVault.balanceOf(ETH) = 0
   → unlockQueue reverts: AmountMustBeGreaterThanZero
   → Alice's request remains locked; her rsETH is stuck in the manager

Result:
  assetsCommitted[ETH] = 80 ETH
  LRTUnstakingVault.balanceOf(ETH) = 0
  Alice cannot complete her withdrawal until the vault is replenished
  by a new EigenLayer unstaking cycle (days of delay, operator-dependent).
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L168-173)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L228-235)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L297-297)
```text
        if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/LRTWithdrawalManager.sol (L802-802)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```

**File:** contracts/LRTUnstakingVault.sol (L43-43)
```text
    mapping(address asset => uint256 buffer) public queuedWithdrawalsBuffer;
```

**File:** contracts/LRTUnstakingVault.sol (L235-237)
```text
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
```
