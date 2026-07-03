Audit Report

## Title
`instantWithdrawal` Drains `LRTUnstakingVault` Without Respecting `assetsCommitted`, Freezing Queued Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

## Summary

`LRTWithdrawalManager` maintains two unsynchronized accounting variables for protecting queued-withdrawal liquidity: `assetsCommitted[asset]` (in `LRTWithdrawalManager`) and `queuedWithdrawalsBuffer[asset]` (in `LRTUnstakingVault`). The `instantWithdrawal` path checks only `queuedWithdrawalsBuffer`, which defaults to zero, and never reads or updates `assetsCommitted`. Instant withdrawers can therefore drain the entire `LRTUnstakingVault` balance — including assets already reserved for queued withdrawal users — leaving those users' rsETH locked in the withdrawal manager with no vault assets available to fulfill their requests.

## Finding Description

**Queued path — `initiateWithdrawal`:** [1](#0-0) 

Each queued request increments `assetsCommitted[asset]`, reserving that amount against `getAvailableAssetAmount`, which computes `lrtDepositPool.getTotalAssetDeposits(asset) - assetsCommitted[asset]` across all protocol assets. [2](#0-1) 

**Instant path — `instantWithdrawal`:** [3](#0-2) 

The only guard is `getAssetsAvailableForInstantWithdrawal`, which returns `vaultBalance - queuedWithdrawalsBuffer[asset]`: [4](#0-3) 

`queuedWithdrawalsBuffer` is a mapping that defaults to zero for every asset and must be explicitly set by an operator: [5](#0-4) 

`instantWithdrawal` never reads `assetsCommitted` and never updates it. It simply drains the vault up to `vaultBalance - queuedWithdrawalsBuffer`.

**Queue fulfillment — `unlockQueue`:**

`_createUnlockParams` sets `totalAvailableAssets` directly from the vault balance: [6](#0-5) 

If the vault has been drained by instant withdrawals, `unlockQueue` immediately reverts: [7](#0-6) 

Even if the vault has a non-zero but insufficient balance, `_unlockWithdrawalRequests` exits the loop without unlocking any request: [8](#0-7) 

`assetsCommitted` is only decremented inside `_unlockWithdrawalRequests` at L802, which is never reached when the vault is empty. The desync `assetsCommitted[asset] > LRTUnstakingVault.balanceOf(asset)` is therefore a reachable and persistent state.

## Impact Explanation

Users who called `initiateWithdrawal` have already transferred their rsETH to the withdrawal manager. If the vault is subsequently drained by instant withdrawers, `unlockQueue` cannot process their requests. Their rsETH remains locked in the contract until an operator manually replenishes the vault by completing a new EigenLayer unstaking cycle — a multi-day process. This constitutes **temporary freezing of funds (Medium)**.

## Likelihood Explanation

- `isInstantWithdrawalEnabled[asset]` must be `true` — an operator-enabled feature, realistic in production.
- `queuedWithdrawalsBuffer[asset]` defaults to `0` for every asset; it must be explicitly set by an operator to provide any protection. If never set, or set too low, the vulnerability is fully exposed.
- Any rsETH holder can call `instantWithdrawal` permissionlessly once the feature is enabled.
- No special knowledge is required: a user simply calls `instantWithdrawal` for the full vault balance while queued withdrawal requests exist.

**Likelihood: Medium.**

## Recommendation

Synchronize the two accounting mechanisms. In `instantWithdrawal`, check that the requested asset amount does not exceed assets not already committed to queued users. Concretely, `getAssetsAvailableForInstantWithdrawal` should be made aware of `assetsCommitted` — for example, by having the vault query the withdrawal manager's `assetsCommitted[asset]` and using `max(queuedWithdrawalsBuffer[asset], assetsCommitted[asset])` as the reserved buffer. Alternatively, `instantWithdrawal` itself should enforce `assetAmountUnlocked <= getAvailableAssetAmount(asset) - assetsCommitted[asset]` before calling `unstakingVault.redeem`. The single source of truth for "how much of the vault is reserved" should be `assetsCommitted`, not a separately maintained manual buffer.

## Proof of Concept

```
State: LRTUnstakingVault holds 100 ETH. queuedWithdrawalsBuffer[ETH] = 0.
       isInstantWithdrawalEnabled[ETH] = true.

1. Alice calls initiateWithdrawal(ETH, rsETH_A)
   → assetsCommitted[ETH] += 80 ETH
   → Alice's rsETH (worth 80 ETH) is locked in LRTWithdrawalManager

2. Bob calls instantWithdrawal(ETH, rsETH_B)
   → getAssetsAvailableForInstantWithdrawal = 100 - 0 = 100 ETH  ✓
   → unstakingVault.redeem(ETH, 100 ETH)  — vault drained to 0
   → assetsCommitted[ETH] unchanged = 80 ETH

3. Operator calls unlockQueue(ETH, ...)
   → totalAvailableAssets = unstakingVault.balanceOf(ETH) = 0
   → reverts with AmountMustBeGreaterThanZero()
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
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

**File:** contracts/LRTUnstakingVault.sol (L235-238)
```text
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```
