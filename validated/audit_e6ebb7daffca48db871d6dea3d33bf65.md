Audit Report

## Title
`_calculatePayoutAmount` Applies One-Sided `min()` That Passes Full Price-Drop Risk to Users While Capping Their Upside — (`contracts/LRTWithdrawalManager.sol`)

## Summary

`LRTWithdrawalManager._calculatePayoutAmount` returns `min(expectedAssetAmount, currentReturn)`, where `currentReturn` is recomputed at `unlockQueue` time using fresh oracle prices. If the rsETH price falls between `initiateWithdrawal` and `unlockQueue`, the user receives strictly less than the `expectedAssetAmount` stored at initiation, while their full `rsETHUnstaked` is burned. Conversely, if the price rises, the user is capped at `expectedAssetAmount` and the protocol retains the surplus. This asymmetry means users bear all downside price risk but receive none of the upside.

## Finding Description

**Step 1 — Initiation stores a price-locked `expectedAssetAmount`.**

`initiateWithdrawal` computes `expectedAssetAmount` from the oracle price at initiation time and stores it in the `WithdrawalRequest`: [1](#0-0) 

The user's rsETH is immediately transferred to the contract and cannot be reclaimed: [2](#0-1) 

**Step 2 — `_calculatePayoutAmount` applies a one-sided `min` at unlock time.**

When `unlockQueue` is called by an operator, it fetches fresh oracle prices and passes them to `_unlockWithdrawalRequests`, which calls `_calculatePayoutAmount`: [3](#0-2) 

- If rsETH price **rose**: `currentReturn > expectedAssetAmount`, so payout is capped at `expectedAssetAmount` — protocol retains the surplus.
- If rsETH price **fell**: `currentReturn < expectedAssetAmount`, so payout is `currentReturn` — user bears the full downside.

**Step 3 — Full rsETH is burned but only `payoutAmount` is redeemed.**

In `_unlockWithdrawalRequests`, `assetsCommitted` is decremented by the original (higher) `expectedAssetAmount`, but only `payoutAmount` is redeemed from the vault and allocated to the user. The full `rsETHUnstaked` is burned: [4](#0-3) 

The gap `(expectedAssetAmount − payoutAmount)` remains in the unstaking vault. The user's `request.expectedAssetAmount` is overwritten with the lower `payoutAmount`, which is what `_processWithdrawalCompletion` ultimately transfers: [5](#0-4) 

**Step 4 — No existing guard prevents this.**

`unlockQueue` includes price-range guards (`minimumRsEthPrice` / `maximumRsEthPrice`) set by the operator at call time, but these do not protect users from price drops that occur within the accepted range. The `_validatePrices` check only prevents the operator from calling with stale or extreme prices; it does not guarantee the unlock-time price matches the initiation-time price. [6](#0-5) 

## Impact Explanation

A user who calls `initiateWithdrawal` is shown `expectedAssetAmount = rsETHUnstaked * P1 / assetPrice` as their expected return. Their rsETH is locked immediately. If rsETH price drops to P2 < P1 before `unlockQueue` is called, they receive `rsETHUnstaked * P2 / assetPrice`, which is strictly less than the stored `expectedAssetAmount`. The user cannot cancel or recover the difference. The protocol does not lose value — the shortfall remains in the vault. This matches the allowed impact: **Low — Contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation

rsETH is a yield-bearing LRT whose price reflects underlying LST valuations and EigenLayer strategy returns. Any slashing event, LST depeg, or oracle update during the ~8-day withdrawal delay can cause the rsETH price to fall. The delay is hardcoded: [7](#0-6) 

No privileged access or attacker action is required — any user initiating a withdrawal is passively exposed to this risk. The operator calling `unlockQueue` is a routine operational action, not a malicious one. The scenario is realistic and repeatable.

## Recommendation

Two options:

1. **Lock prices at initiation**: Store `rsETHPrice` and `assetPrice` in `WithdrawalRequest` at initiation time. Use those stored prices in `_calculatePayoutAmount` instead of the unlock-time prices. This guarantees the user receives exactly `expectedAssetAmount` regardless of subsequent price movement (subject to available assets in the vault).

2. **Return excess rsETH on price drop**: If `currentReturn < expectedAssetAmount` at unlock time, compute the proportional rsETH difference and return it to the user rather than burning the full `rsETHUnstaked`. This makes the user whole in rsETH terms and eliminates the asymmetry.

## Proof of Concept

```solidity
// Foundry fork test outline
// 1. Fork mainnet; deploy/configure LRTWithdrawalManager
// 2. User calls initiateWithdrawal(asset, rsETHUnstaked)
//    => expectedAssetAmount = rsETHUnstaked * P1 / assetPrice stored in request
//    => rsETH transferred to contract
// 3. Mock oracle: set rsETHPrice to P2 < P1 (simulate slashing/depeg)
// 4. Warp block.number forward by withdrawalDelayBlocks
// 5. Operator calls unlockQueue(asset, ..., P2, P2)
//    => _calculatePayoutAmount returns rsETHUnstaked * P2 / assetPrice < expectedAssetAmount
//    => request.expectedAssetAmount overwritten with lower value
//    => full rsETHUnstaked burned
// 6. User calls completeWithdrawal(asset)
//    => receives rsETHUnstaked * P2 / assetPrice
// 7. Assert: received < expectedAssetAmountAtInitiation
//    => shortfall = rsETHUnstaked * (P1 - P2) / assetPrice remains in vault
// Invariant: payout >= expectedAssetAmount stored at initiation  // FAILS
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L734-734)
```text
        _transferAsset(asset, user, request.expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L802-807)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L853-870)
```text
    function _validatePrices(
        uint256 rsETHPrice,
        uint256 assetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumRsEthPrice,
        uint256 minimumAssetPrice,
        uint256 maximumAssetPrice
    )
        internal
        pure
    {
        if (rsETHPrice < minimumRsEthPrice || rsETHPrice > maximumRsEthPrice) {
            revert RsETHPriceOutOfPriceRange(rsETHPrice);
        }
        if (assetPrice < minimumAssetPrice || assetPrice > maximumAssetPrice) {
            revert AssetPriceOutOfPriceRange(assetPrice);
        }
    }
```
