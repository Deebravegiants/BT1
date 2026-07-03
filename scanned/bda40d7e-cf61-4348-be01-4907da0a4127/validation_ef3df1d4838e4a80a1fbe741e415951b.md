### Title
Stale `rsETHPrice` Used After Protocol Unpause When Price-Drop Circuit Breaker Fires - (File: contracts/LRTOracle.sol)

### Summary

In `LRTOracle._updateRsETHPrice()`, when the computed new price falls below `highestRsethPrice` by more than `pricePercentageLimit`, the function pauses the protocol and **returns early without updating `rsETHPrice`**. The stale (pre-drop) price persists in storage. When the admin later unpauses the protocol, there is no on-chain enforcement that `updateRSETHPrice()` must be called before the deposit pool and withdrawal manager are re-enabled, so the stale price is used for all deposit and withdrawal calculations during that window.

### Finding Description

`LRTOracle._updateRsETHPrice()` computes `newRsETHPrice` from the current TVL, then checks whether the price has dropped beyond the configured threshold:

```solidity
// contracts/LRTOracle.sol lines 270-282
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;   // <-- early return, rsETHPrice is NOT updated
    }
    ...
}
...
rsETHPrice = newRsETHPrice;  // line 313 — never reached on the early-return path
```

The out-of-bounds `newRsETHPrice` is computed but discarded. `rsETHPrice` retains the old (higher) value from before the price drop.

`LRTOracle.unpause()` only clears the `paused` flag:

```solidity
// contracts/LRTOracle.sol lines 143-146
function unpause() external whenPaused onlyLRTAdmin {
    paused = false;
    emit Unpaused(msg.sender);
}
```

It does not update `rsETHPrice`. After unpausing the oracle, the admin must separately unpause `LRTDepositPool` and `LRTWithdrawalManager`. There is no on-chain requirement that `updateRSETHPrice()` be called in between. If the admin unpauses the withdrawal manager before calling `updateRSETHPrice()`, the stale (inflated) price is immediately available for withdrawal calculations.

`LRTWithdrawalManager._createUnlockParams()` reads the stored price directly:

```solidity
// contracts/LRTWithdrawalManager.sol lines 846-848
return UnlockParams({
    rsETHPrice: lrtOracle.rsETHPrice(),   // reads stale value
    ...
});
```

And `_calculatePayoutAmount()` uses it to compute user payouts:

```solidity
// contracts/LRTWithdrawalManager.sol line 833
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
```

Similarly, `LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()`:

```solidity
// contracts/LRTDepositPool.sol line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

### Impact Explanation

The stale `rsETHPrice` is **higher** than the actual post-drop price. During the window between unpausing the withdrawal manager and the next successful `updateRSETHPrice()` call:

- **Withdrawers** receive `rsETHUnstaked × stalePriceHigh / assetPrice` — more ETH than their rsETH is actually worth. This constitutes direct theft of funds from the protocol.
- **Depositors** receive fewer rsETH than they should (`amount × assetPrice / stalePriceHigh`), suffering a loss relative to the true exchange rate.

The net effect is protocol insolvency risk proportional to the magnitude of the price drop and the volume of withdrawals processed before the price is corrected.

**Impact: High — Theft of funds / protocol insolvency during the unpause window.**

### Likelihood Explanation

The price-drop circuit breaker is a designed safety mechanism intended to fire during real adverse events (e.g., EigenLayer slashing). Every time it fires and the admin subsequently unpauses the protocol, this window exists. There is no on-chain guard enforcing the correct unpause ordering (`oracle.unpause()` → `updateRSETHPrice()` → `withdrawalManager.unpause()`). A single operational misstep — or a front-running withdrawer who acts in the same block as the withdrawal manager unpause — is sufficient to exploit the stale price.

**Likelihood: Medium** — Requires the circuit breaker to have fired and the admin to not atomically update the price before re-enabling withdrawals, which is a realistic operational scenario with no code-level prevention.

### Recommendation

Update `rsETHPrice` to `newRsETHPrice` **before** pausing and returning, so that the stored price always reflects the most recently computed value:

```solidity
if (isPriceDecreaseOffLimit) {
    rsETHPrice = newRsETHPrice;  // store the out-of-bounds price before pausing
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

Alternatively, require that `updateRSETHPrice()` is called (and succeeds) as part of the unpause flow, or add an `unpauseAndUpdatePrice()` function that atomically unpauses and refreshes `rsETHPrice`.

### Proof of Concept

1. `pricePercentageLimit` is set to `5e16` (5%).
2. `rsETHPrice` is `1.10 ETH` (stored), `highestRsethPrice` is `1.10 ETH`.
3. An EigenLayer slashing event reduces TVL. `_updateRsETHPrice()` computes `newRsETHPrice = 1.03 ETH` — a 6.4% drop, exceeding the 5% limit.
4. The function pauses the deposit pool, withdrawal manager, and oracle, then **returns**. `rsETHPrice` remains `1.10 ETH`.
5. Admin calls `LRTOracle.unpause()`, then `LRTWithdrawalManager.unpause()` (without calling `updateRSETHPrice()` in between).
6. A withdrawer who had queued a request for `100 rsETH` calls the unlock function. `_createUnlockParams()` reads `rsETHPrice = 1.10 ETH`.
7. `currentReturn = 100 × 1.10 / 1.0 = 110 ETH` — but the true value is only `103 ETH`. The withdrawer extracts `7 ETH` of excess value from the protocol. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L143-146)
```text
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTOracle.sol (L269-282)
```text
        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTWithdrawalManager.sol (L846-848)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
