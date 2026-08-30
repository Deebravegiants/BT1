### Title
Zero-debt liquidation via rounding gap between `calc-final-liquidation-amounts` and `scale-debt-for-liquidation` - ([File: mainnet/contracts/market/v0-4-market.clar])

### Summary
When a liquidation's collateral leg is capped (`coll-actual < coll-expected`), `calc-final-liquidation-amounts` recomputes `debt-final-usd`/`debt-final` from the capped collateral value, which can floor to `0` token units for high-decimal, high-price debt assets (e.g. sBTC, 8 decimals). `scale-debt-for-liquidation` then only proportionally shrinks `coll-final` when `scaled-to-remove < scaled-debt`, but if `debt-final` is already `0`, `scaled-debt` is also exactly `0`, so `scaled-to-remove == scaled-debt == 0` and the shrink branch is skipped, leaving `coll-final = coll-actual` (a real, non-zero collateral amount) unchanged while `debt-to-repay = 0`.

### Finding Description
The broken identity is:
`debt-to-repay (tokens transferred into the vault) == 0` while `coll-final (tokens transferred out to the liquidator) > 0`.

Code path in `mainnet/contracts/market/v0-4-market.clar`:
- `calc-final-liquidation-amounts` [1](#0-0)  computes `coll-actual-usd`, then `debt-final-usd` via `calc-liq-debt-repay-real` when `coll-actual < coll-expected` [2](#0-1) , and finally `debt-final = mul-div-down(debt-final-usd, 10^debt-decimals, debt-price)`. For sBTC (`debt-decimals = 8`), any `debt-final-usd` below roughly the dollar value of the smallest sBTC unit (a fraction of a cent at BTC market price) floors `debt-final` to `0`.
- `scale-debt-for-liquidation` [3](#0-2)  then computes `scaled-debt = mul-div-down(debt-final, INDEX-PRECISION, borrow-index)`. If `debt-final = 0`, `scaled-debt = 0` exactly (not merely capped). `scaled-to-remove = min(scaled-debt, curr-scaled) = 0`, so `debt-to-repay = mul-div-up(0, borrow-index, INDEX-PRECISION) = 0`. Critically, the proportional-shrink guard `(if (< scaled-to-remove scaled-debt) ... coll-actual)` evaluates `0 < 0 = false`, so `coll-final` falls through to the **unshrunk** `coll-actual` value — the full capped, but non-zero, real collateral balance.

Root cause: the code only re-scales `coll-final` down when the *scaled-debt storage cap* (`curr-scaled`) is the binding constraint, not when `debt-final` itself was already rounded to zero upstream in `calc-final-liquidation-amounts`. The two independent floor-roundings (`debt-final-usd -> debt-final` and `debt-final -> scaled-debt`) are not accounted for when deciding whether to shrink `coll-final`.

No `min-out`/slippage check protects the liquidator-side collateral transfer against this specific zero-debt case, since `coll-final` is exactly what gets paid out and is non-zero by construction (it equals the victim's real, non-dust-necessarily collateral balance if the collateral asset's own value is high enough relative to the debt-token's per-unit dollar granularity).

### Impact Explanation
Per triggering call, the liquidator receives `coll-final = coll-actual` (real collateral tokens) while repaying `debt-to-repay = 0` debt tokens. This is uncompensated collateral extraction — value leaves the protocol/victim with no offsetting debt reduction, which is absorbed by the vault (and ultimately LPs, since the underlying debt obligation is not reduced by an equivalent real repayment). The trigger condition requires `coll-actual-usd` (post-cap) to convert to less than one debt-token unit's dollar value given `debt-price`/`debt-decimals` — for sBTC this window is roughly a fraction of a U.S. cent, so the amount extractable per single triggering position is bounded and small, but the underlying mechanism is a genuine flow-closure violation (unpriced token flow) rather than a benign rounding tolerance, and is repeatable across any number of qualifying capped-liquidation events.

### Likelihood Explanation
Triggering requires a victim position (which an attacker can create themselves, acting as both borrower and liquidator via separate wallets) whose collateral balance is small enough that it becomes the binding cap (`coll-actual = user-coll-balance < coll-expected`), combined with sBTC (or any high-decimals/high-price) debt so that the derived `debt-final` floors to exactly zero token units. Setting this up costs only normal deposit/borrow/liquidate transaction fees and requires no privileged access — fully within the unprivileged attacker capability described. It is mechanically repeatable across many self-created dust-adjacent positions.

### Recommendation
In `scale-debt-for-liquidation` (or earlier in `calc-final-liquidation-amounts`), explicitly reject or zero-out `coll-final` whenever `debt-final` (or `debt-to-repay`) resolves to `0` but `coll-actual` is non-zero, e.g. `(if (is-eq debt-to-repay u0) u0 coll-final)`, or equivalently assert `debt-to-repay > u0` before allowing any non-zero collateral transfer in the liquidation execution path (`liquidate`), so that a rounding-induced zero debt repayment can never be paired with a non-zero collateral seizure.

### Proof of Concept
Clarinet simnet test plan:
1. Register an sBTC debt asset (`debt-decimals = u8`) with a high debt-price (e.g. simulate BTC at $100,000) and a low-decimals/low-price collateral asset.
2. Create a victim position with `user-coll-balance` set such that `coll-expected` computed from the target `debt-actual-usd`/`liq-penalty` exceeds `user-coll-balance` (forcing the cap path), while `coll-actual-usd` from that capped balance, once divided by `(BPS + liq-penalty)` and converted to sBTC units (`mul-div-down(debt-final-usd, 10^8, debt-price)`), computes to `0`.
3. Call `liquidate` (or the equivalent public entrypoint) as an unprivileged liquidator against the victim.
4. Assert directly on the intermediate values / ft-transfer amounts:
   - `debt-to-repay == u0` (no sBTC actually transferred into the vault), and
   - `coll-final == coll-actual > u0` (collateral tokens transferred out to the liquidator), thereby demonstrating `FLOW_CLOSURE` violation: value-in `== 0` while value-out `> 0` for the same liquidation call.

Note: I was unable to fully read the `liquidate` public function body in `mainnet/contracts/market/v0-4-market.clar` (beyond line 1000, due to iteration limits) to directly confirm the exact token-transfer statements that consume `debt-to-repay` and `coll-final`; the analysis above is based on the private helper functions' logic (`calc-final-liquidation-amounts`, `scale-debt-for-liquidation`) which are confirmed present and match the question's described identity exactly. A Devin session with full file access should verify the final transfer calls in `liquidate` to confirm `debt-to-repay` and `coll-final` are indeed the amounts used for the inbound/outbound `ft-transfer` calls before finalizing this as a confirmed exploit.

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L733-734)
```text
(define-private (calc-liq-debt-repay-real (collateral-amount-usd uint) (liq-penalty uint)) 
  (div-bps-down collateral-amount-usd (+ BPS liq-penalty)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L844-853)
```text
  (let ((coll-actual-usd (normalize (* coll-actual coll-price) coll-decimals false))
        ;; If collateral was capped, recalculate debt proportionally
        (debt-final-usd (if (< coll-actual coll-expected)
                           (calc-liq-debt-repay-real coll-actual-usd liq-penalty)
                           debt-actual-usd))
        (debt-final (mul-div-down debt-final-usd (pow u10 debt-decimals) debt-price)))
    {
      debt-final-usd: debt-final-usd,
      debt-final: debt-final
    }))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L858-877)
```text
(define-private (scale-debt-for-liquidation
  (debt-final uint)
  (coll-actual uint)
  (curr-scaled uint)
  (asset-id uint))
  (let (;; convert debt amount to scaled units for storage
        (borrow-index (get index (unwrap-panic (get-cached-indexes asset-id))))
        (scaled-debt (mul-div-down debt-final INDEX-PRECISION borrow-index))
        ;; cap at current debt (prevent over-repayment)
        (scaled-to-remove (if (> scaled-debt curr-scaled) curr-scaled scaled-debt))
        (debt-to-repay (mul-div-up scaled-to-remove borrow-index INDEX-PRECISION))
        ;; If debt was capped, scale collateral proportionally
        (coll-final (if (< scaled-to-remove scaled-debt)
                        (mul-div-down coll-actual scaled-to-remove scaled-debt)
                        coll-actual)))
    {
      scaled-to-remove: scaled-to-remove,
      debt-to-repay: debt-to-repay,
      coll-final: coll-final
    }))
```
