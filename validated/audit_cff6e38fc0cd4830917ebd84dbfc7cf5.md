Audit Report

## Title
`_updateRsETHPrice()` Downside Circuit-Breaker Compares Against All-Time-High Instead of Previous Price, Enabling Unprivileged Protocol-Wide Pause — (File: `contracts/LRTOracle.sol`)

## Summary

`LRTOracle._updateRsETHPrice()` uses `highestRsethPrice` (the all-time high) as the baseline for its downside circuit-breaker, rather than `previousPrice` (the last stored price). Because `updateRSETHPrice()` is `public`, any unprivileged caller can trigger an atomic pause of `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` whenever normal LST oracle fluctuations cause the computed rsETH price to fall below the ATH by more than `pricePercentageLimit`. Unpausing requires separate `onlyLRTAdmin` calls on each contract.

## Finding Description

In `contracts/LRTOracle.sol`, `_updateRsETHPrice()` computes `previousPrice = rsETHPrice` at line 228 but never uses it for the downside guard. Instead, lines 270–274 compare `newRsETHPrice` against `highestRsethPrice`:

```solidity
// line 228 — previousPrice captured but unused in downside check
uint256 previousPrice = rsETHPrice;
...
// lines 270–274 — baseline is ATH, not previousPrice
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

`highestRsethPrice` is the all-time high, updated only upward (line 294–296). rsETH accrues staking rewards so its price grows over time, meaning `highestRsethPrice` will always be at or above the current price. Any intraday dip in an underlying LST oracle (stETH/ETH, cbETH/ETH, etc.) that causes `newRsETHPrice` to fall below `highestRsethPrice` by more than `pricePercentageLimit` triggers lines 278–281:

```solidity
if (!lrtDepositPool.paused()) lrtDepositPool.pause();
if (!withdrawalManager.paused()) withdrawalManager.pause();
_pause();
return;
```

The entry point has no access control:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The upside guard (lines 252–266) reverts non-manager callers but does not pause. The downside guard has no such revert path — it always pauses. The manager bypass `updateRSETHPriceAsManager()` (line 94) is irrelevant here because the pause is triggered before the manager can intervene, and unpausing requires `onlyLRTAdmin` on three separate contracts.

## Impact Explanation

**Medium — Temporary freezing of funds.** When the pause fires:
- All deposits via `LRTDepositPool` are blocked (`whenNotPaused` guards deposit functions).
- All withdrawals via `LRTWithdrawalManager` are blocked.
- `LRTOracle.updateRSETHPrice()` itself becomes blocked, preventing further price updates by public callers.

Users cannot deposit or withdraw until an admin manually calls `unpause()` on each of the three contracts. This is a concrete, temporary freeze of user funds matching the allowed Medium impact category.

## Likelihood Explanation

Likelihood is **medium-high**:

1. `pricePercentageLimit` is a single value shared for both upside and downside checks. A value tight enough to be meaningful for the upside guard (e.g., 1% = `1e16`) is structurally too tight for the downside guard because the baseline is the ATH, not the last price.
2. rsETH's computed price is the sum of `totalAssetAmt * assetPrice` across all supported LSTs. A 1–2% intraday tick on any one Chainlink feed (normal volatility for stETH/ETH) can push the computed price below `highestRsethPrice` by more than `pricePercentageLimit`.
3. `updateRSETHPrice()` requires no privileges — any EOA or contract can call it.
4. The condition is repeatable: after admin unpauses, the same oracle conditions can re-trigger the pause on the next public call.

## Recommendation

Replace `highestRsethPrice` with `previousPrice` as the baseline for the downside circuit-breaker, so the check measures deviation from the last stored price rather than the ATH:

```solidity
if (newRsETHPrice < previousPrice) {
    uint256 diff = previousPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(previousPrice);
    ...
}
```

Alternatively, introduce a separate `priceDecreaseLimit` parameter (wider than `pricePercentageLimit`) measured against `previousPrice`, mirroring the fix pattern of widening the threshold from a tight upside guard to a realistic downside guard.

## Proof of Concept

1. Protocol operates normally; rsETH price grows to `1.05e18`. `highestRsethPrice = 1.05e18`, `rsETHPrice = 1.05e18`.
2. Admin sets `pricePercentageLimit = 1e16` (1%).
3. stETH/ETH Chainlink feed ticks down ~1.1% intraday (normal volatility). Computed `newRsETHPrice ≈ 1.0385e18`.
4. `diff = 1.05e18 - 1.0385e18 = 0.0115e18`. `pricePercentageLimit.mulWad(highestRsethPrice) = 0.01 * 1.05e18 = 0.0105e18`. `0.0115e18 > 0.0105e18` → `isPriceDecreaseOffLimit = true`.
5. Any unprivileged user calls `updateRSETHPrice()`. Lines 278–281 execute: `LRTDepositPool.pause()`, `LRTWithdrawalManager.pause()`, `LRTOracle._pause()`.
6. All deposits and withdrawals are frozen. Admin must call `unpause()` on all three contracts separately to restore functionality.

**Foundry fork test plan:** Deploy against a mainnet fork with `highestRsethPrice` set above current price by >1%. Call `updateRSETHPrice()` from `address(0xdead)`. Assert `lrtDepositPool.paused() == true`, `withdrawalManager.paused() == true`, `lrtOracle.paused == true`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L228-228)
```text
        uint256 previousPrice = rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
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

**File:** contracts/LRTOracle.sol (L294-296)
```text
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```
