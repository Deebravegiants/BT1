Audit Report

## Title
Bootstrap DoS: `highestRsethPrice == 0` Permanently Blocks Non-Manager `updateRSETHPrice()` When `pricePercentageLimit > 0` — (`contracts/LRTOracle.sol`)

## Summary
After deployment, `rsETHPrice` and `highestRsethPrice` are both `0`. Once `pricePercentageLimit` is set to a non-zero value and rsETH has been minted, the `highestRsethPrice == 0` guard at line 224 is a no-op (it assigns `rsETHPrice = 0` back to `highestRsethPrice`). Every subsequent call to the public `updateRSETHPrice()` by a non-manager reverts with `PriceAboveDailyThreshold` because `newRsETHPrice > 0 = highestRsethPrice` always exceeds the threshold of `pricePercentageLimit.mulWad(0) = 0`. The only escape is the manager-gated `updateRSETHPriceAsManager()`, leaving `rsETHPrice` stuck at `0` until manager intervention.

## Finding Description
**Root cause:** The bootstrap guard at lines 224–226 assigns `highestRsethPrice = rsETHPrice`, but `rsETHPrice` is still `0` at that point (it is only written at line 313, after the threshold check). This makes the guard a no-op.

**Exact code path:**

1. `rsethSupply > 0` → the early-return at lines 218–222 is skipped.
2. Lines 224–226: `highestRsethPrice = rsETHPrice = 0` — no change.
3. Line 250: `newRsETHPrice = totalETHInProtocol.divWad(rsethSupply)` — a positive value (~1e18).
4. Line 252: `newRsETHPrice > highestRsethPrice (0)` → `true`.
5. Line 254: `priceDifference = newRsETHPrice − 0 = newRsETHPrice`.
6. Line 257: `pricePercentageLimit.mulWad(0) = 0`; `isPriceIncreaseOffLimit = (pricePercentageLimit > 0) && (newRsETHPrice > 0)` → `true`.
7. Lines 263–264: non-manager caller → `revert PriceAboveDailyThreshold()`.

Because the revert rolls back all state changes (including the no-op assignment at line 225), the contract returns to the identical `rsETHPrice = 0 / highestRsethPrice = 0` state. Every subsequent non-manager call repeats this path identically.

**Why existing checks fail:** The `highestRsethPrice == 0` guard was intended to seed the peak price, but it reads `rsETHPrice` (still `0`) instead of the freshly computed `newRsETHPrice` (positive). The threshold check at line 257 then compares against `0`, making any positive price "infinitely above the limit."

## Impact Explanation
**Medium. Temporary freezing of funds.**

While `rsETHPrice = 0`, any protocol component that reads it (withdrawal share math, fee calculations via `previousTVL = rsethSupply.mulWad(rsETHPrice) = 0`) operates on a zero/stale price. The permissionless price-update guarantee — the entire purpose of the public function — is broken. The freeze is temporary because `updateRSETHPriceAsManager()` provides a manager escape hatch; once called, `highestRsethPrice` is seeded with a positive value and non-manager calls resume normally.

## Likelihood Explanation
No attacker action is required. The sequence is the normal deployment flow: deploy → admin calls `setPricePercentageLimit(nonZero)` → users deposit (minting rsETH) → any public caller invokes `updateRSETHPrice()` before the manager has ever called `updateRSETHPriceAsManager()`. This is a latent initialization bug that activates automatically on the first real-world call to the public function. It is repeatable on every deployment until the manager bootstraps the price.

## Recommendation
In the `highestRsethPrice == 0` branch, seed with `newRsETHPrice` (computed after the guard) rather than the stale `rsETHPrice`. One approach: move the guard to after `newRsETHPrice` is computed, or skip the threshold check entirely when `highestRsethPrice == 0`:

```solidity
// After computing newRsETHPrice at line 250:
if (highestRsethPrice == 0) {
    highestRsethPrice = newRsETHPrice; // seed with real price, not stale 0
}
```

Alternatively, require `initialize`/`reinitialize` to set `highestRsethPrice` to a non-zero sentinel (e.g., `1 ether`) so the bootstrap state is never `0`.

## Proof of Concept
```
Preconditions:
  rsETHPrice = 0, highestRsethPrice = 0 (post-deployment defaults)
  pricePercentageLimit = 1e16 (1%, set by admin)
  rsethSupply > 0 (users have deposited)
  Caller: any non-manager EOA

Call: updateRSETHPrice()
  → _updateRsETHPrice()
  → rsethSupply > 0: skip early-return (lines 218-222)
  → highestRsethPrice == 0: highestRsethPrice = rsETHPrice = 0 (no-op, lines 224-226)
  → newRsETHPrice = totalETHInProtocol / rsethSupply ≈ 1e18 (line 250)
  → newRsETHPrice (1e18) > highestRsethPrice (0): true (line 252)
  → priceDifference = 1e18 - 0 = 1e18 (line 254)
  → pricePercentageLimit.mulWad(0) = 0 (line 257)
  → isPriceIncreaseOffLimit = true (1e18 > 0) (line 257)
  → caller lacks MANAGER role → revert PriceAboveDailyThreshold (lines 263-264)

State after revert: rsETHPrice = 0, highestRsethPrice = 0 (unchanged)
→ Every subsequent non-manager call repeats identically

Foundry test plan:
  1. Deploy LRTOracle with mock lrtConfig
  2. Set pricePercentageLimit = 1e16
  3. Mint rsETH supply > 0 via mock
  4. Call updateRSETHPrice() from non-manager EOA
  5. Assert revert with PriceAboveDailyThreshold
  6. Assert rsETHPrice == 0 and highestRsethPrice == 0 post-revert
  7. Call updateRSETHPriceAsManager() from manager
  8. Assert rsETHPrice > 0 and highestRsethPrice > 0
  9. Call updateRSETHPrice() from non-manager EOA again
  10. Assert success
```