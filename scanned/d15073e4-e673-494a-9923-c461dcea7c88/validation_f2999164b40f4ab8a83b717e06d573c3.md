### Title
`_calculatePayoutAmount` Uses Unlock-Time rsETH Price, Causing Users to Receive Less Than the Amount Promised at Initiation — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager._calculatePayoutAmount` computes the user's payout as `min(expectedAssetAmount, currentReturn)`, where `currentReturn` uses the rsETH price at `unlockQueue` time. If rsETH price falls between `initiateWithdrawal` and `unlockQueue`, the user receives less than the `expectedAssetAmount` that was calculated and stored at initiation — the amount the user was shown as their promised return. The user bears the full downside of any rsETH price decrease but receives no upside if the price increases.

---

### Finding Description

**Step 1 — `initiateWithdrawal` stores a price-locked promise.**

At initiation, `expectedAssetAmount` is computed from the current oracle price and stored in the `WithdrawalRequest`: [1](#0-0) 

```solidity
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
// ...
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

`getExpectedAssetAmount` uses the oracle price at initiation time: [2](#0-1) 

The user's rsETH is immediately transferred to the contract and cannot be reclaimed: [3](#0-2) 

**Step 2 — `_calculatePayoutAmount` applies a one-sided `min` at unlock time.**

When `unlockQueue` is called (by an operator), it fetches fresh oracle prices and passes them to `_unlockWithdrawalRequests`, which calls: [4](#0-3) 

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

- If rsETH price **rose**: payout is capped at `expectedAssetAmount` — protocol keeps the upside.
- If rsETH price **fell**: payout is `currentReturn < expectedAssetAmount` — user bears the full downside.

The overwritten `request.expectedAssetAmount` (now the lower value) is what `_processWithdrawalCompletion` transfers to the user: [5](#0-4) [6](#0-5) 

**Step 3 — The difference is not returned to the user.**

`assetsCommitted` is decremented by the original (higher) `expectedAssetAmount`, but only the lower `payoutAmount` is actually redeemed from the vault and transferred: [7](#0-6) 

The gap `(expectedAtInitiation − payoutAmount)` remains in the unstaking vault — the protocol does not lose value, but the user receives less than promised.

---

### Impact Explanation

A user who calls `initiateWithdrawal` is shown `expectedAssetAmount = rsETHUnstaked * P1 / assetPrice` as their guaranteed return. Their rsETH is locked in the contract immediately. If rsETH price drops to P2 before `unlockQueue` is called, they receive `rsETHUnstaked * P2 / assetPrice`, which is strictly less than the stored `expectedAssetAmount`. The user cannot cancel or recover the difference. This matches the scoped impact: **contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

rsETH is a yield-bearing LRT token whose price is derived from underlying LST valuations and EigenLayer strategy returns. Any slashing event, LST depeg, or oracle update between initiation and unlock (the delay is ~8 days by default) can cause the rsETH price to fall. The withdrawal delay is hardcoded to `8 days / 12 seconds` blocks: [8](#0-7) 

An 8-day window is a realistic timeframe for rsETH price movement. The scenario requires no privileged access — any user initiating a withdrawal is exposed.

---

### Recommendation

Two options:

1. **Lock the price at initiation**: Store the rsETH price and asset price in `WithdrawalRequest` at initiation time, and use those stored prices in `_calculatePayoutAmount` instead of the unlock-time prices. This guarantees the user receives exactly `expectedAssetAmount` regardless of subsequent price movement (subject to available assets).

2. **Return excess rsETH on price drop**: If `currentReturn < expectedAssetAmount` at unlock time, return the proportional rsETH difference to the user rather than burning the full `rsETHUnstaked` amount. This makes the user whole in rsETH terms.

---

### Proof of Concept

```solidity
// Scenario: rsETH price drops from P1 to P2 between initiation and unlock
// Preconditions: assetPrice stable, withdrawalDelayBlocks passed

// 1. User initiates withdrawal at price P1
// expectedAssetAmount = rsETHUnstaked * P1 / assetPrice  (stored in request)
// rsETH transferred to contract

// 2. rsETH oracle price drops to P2 < P1

// 3. Operator calls unlockQueue
// _calculatePayoutAmount:
//   currentReturn = rsETHUnstaked * P2 / assetPrice
//   payoutAmount  = min(rsETHUnstaked * P1 / assetPrice, rsETHUnstaked * P2 / assetPrice)
//                 = rsETHUnstaked * P2 / assetPrice   <-- user receives this

// 4. User calls completeWithdrawal
// receives rsETHUnstaked * P2 / assetPrice
// shortfall = rsETHUnstaked * (P1 - P2) / assetPrice  <-- stays in vault

// Invariant broken: payout < expectedAssetAmount stored at initiation
// assert(payout >= rsETHUnstaked * P1 / assetPrice)  // FAILS
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

**File:** contracts/LRTWithdrawalManager.sol (L593-594)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
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
