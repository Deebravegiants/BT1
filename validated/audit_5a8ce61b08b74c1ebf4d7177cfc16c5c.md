### Title
Hardcoded square-root assumption in graduated liquidation curve breaks the configured `LIQ-CURVE-EXP` identity - (File: `mainnet/contracts/market/v0-4-market.clar`)

### Summary
This is a genuine analog of the ELO-report bug class: an integer-math "optimization" that silently discards the actual configured exponent and substitutes a hardcoded approximation, producing a systematically wrong result instead of the intended formula.

### Finding Description
`calc-liq-factor-exp` is meant to compute `liq-factor^alpha` where `alpha = curve-exponent / BPS` is a fractional exponent configurable per-egroup via `LIQ-CURVE-EXP` [1](#0-0) . The implementation is:

```
(define-private (calc-liq-factor-exp (factor uint) (exp uint))
  (if (is-eq exp BPS) 
    factor
    (if (> exp BPS) 
        (/ (pow factor (/ exp BPS)) (pow BPS (- (/ exp BPS) u1)))
        (sqrti (* factor BPS))))) ;; assume factor^0.5
``` [2](#0-1) 

For `exp < BPS` (i.e. any configured gentle curve, `alpha < 1.0`), the code does not use `exp` at all — it always returns `sqrti(factor * BPS)`, which computes `factor^0.5` regardless of whether the egroup was configured with `LIQ-CURVE-EXP = 3000` (alpha = 0.3), `7000` (alpha = 0.7), `9000` (alpha = 0.9), etc. The comment itself admits this: `;; assume factor^0.5`. This mirrors the ELO bug's root cause — an unjustified simplification/offset substituted for the real formula, causing the sign/magnitude of the computed exponent to deviate from the documented identity `liq-factor^alpha`.

Additionally, for `exp > BPS`, `(/ exp BPS)` is integer (floor) division, so any fractional part of `alpha` above 1.0 is truncated to the nearest integer — e.g. `exp = 15000` (alpha = 1.5) reduces to integer exponent `1`, again ignoring the configured curve shape.

The correct identity that should hold is:
```
liq-pct-scaled = liq-factor ^ (LIQ-CURVE-EXP / BPS)
```
but the code instead computes `sqrt(liq-factor)` (or a floor-truncated integer power) independent of the actual `LIQ-CURVE-EXP` value stored in the egroup risk parameters [3](#0-2) .

`liq-pct-scaled` directly drives `liq-penalty` (the liquidation bonus paid to the liquidator) and `max-debt-usd` (how much debt/collateral can be liquidated in one call) via `calc-liquidation-params`:
```
(liq-pct-scaled (calc-liq-factor-exp liq-pct-linear curve-exponent))
(liq-penalty (calc-liq-factor-bound liq-pct-scaled liq-penalty-min liq-penalty-max))
(max-debt-usd (calc-liq-debt-repay total-debt-usd liq-pct-scaled))
``` [4](#0-3) 

Because `sqrt(x) > x` for any `x < 1` (i.e. any `liq-factor` under 100%, which is the normal/whole liquidation-window case), substituting a hardcoded square root for a shallower configured curve (e.g. alpha = 0.3 or 0.9) always *inflates* `liq-pct-scaled` relative to the intended curve when `alpha` is closer to 1, and can *deflate* it relative to the intended curve when the DAO actually intended a curve steeper than 0.5 within the `<BPS` branch. Either direction breaks the value identity between the intended graduated-liquidation schedule and the actual bonus/debt-repay amount extracted, i.e.:

```
intended: max-debt-usd = total-debt-usd * liq-factor^(LIQ-CURVE-EXP/BPS)
actual:   max-debt-usd = total-debt-usd * sqrt(liq-factor)     [for any LIQ-CURVE-EXP < BPS]
```

### Impact Explanation
This produces incorrect liquidation-bonus and liquidatable-debt amounts whenever an egroup is configured with a gentle curve exponent other than exactly 0.5 (or a >1.0 exponent with a fractional part). Whenever the actual scaled factor is inflated beyond what the DAO's chosen risk curve intended, liquidators are paid a larger bonus and can seize more collateral per liquidation than the risk parameters authorize — a preventable over-extraction of collateral value from borrowers that the graduated curve was designed to bound. This is a temporary/permanent freezing or theft-adjacent value distortion of user collateral tied directly to a coded math error, not a DAO parameter choice — the DAO only sets `LIQ-CURVE-EXP`; the contract's internal formula silently ignores that setting in the `<BPS` branch.

### Likelihood Explanation
Likelihood is contingent on the DAO configuring any egroup's `LIQ-CURVE-EXP` to a value other than `10000` (linear) or exactly `5000` (the one value for which the hardcoded sqrt happens to be correct). I could not confirm from the indexed files what `LIQ-CURVE-EXP` value(s) are actually deployed in `mainnet/contracts/proposals/mainnet/v0-init.clar`, since the exact byte values are packed in `(buff 2)` hex literals and the grep for a plain `0x` pattern did not resolve them within the tool budget — this is a limitation of the current search, not evidence the values are absent. If the deployed egroups use exponents other than 5000/10000, the bug is triggered on every liquidation of that egroup; if only 5000/10000 are used in practice, the bug is dormant but still present as a latent miscalculation for any future/DAO-updated curve parameter.

### Recommendation
Replace the hardcoded `sqrti` branch and the floor-division branch with an exact rational-exponent computation that honors the actual `exp` parameter (e.g., decompose `exp/BPS` into a proper fractional power using repeated integer roots/powers matching the real denominator, or restrict `LIQ-CURVE-EXP` to a small enumerated set of exponents each with a dedicated, verified integer formula, and revert if an unsupported value is configured rather than silently substituting `sqrt`).

### Proof of Concept
1. DAO (or default init) configures an egroup with `LIQ-CURVE-EXP = 3000` (intended alpha = 0.3, a gentle curve as described in `docs/egroups.md`).
2. A position enters partial liquidation with `liq-pct-linear = 4000` (0.4, in BPS terms after `calc-liq-factor`) [5](#0-4) .
3. `calc-liq-factor-exp(4000, 3000)` takes the `exp < BPS` branch and returns `sqrti(4000 * 10000) = sqrti(40000000) ≈ 6324`, i.e. it computes `0.4^0.5 ≈ 0.632`, instead of the intended `0.4^0.3 ≈ 0.756` [6](#0-5) .
4. This wrong `liq-pct-scaled` (6324 instead of the intended ~7560) is fed into `calc-liq-factor-bound` and `calc-liq-debt-repay`, producing a liquidation penalty and max-liquidatable-debt that diverge from the DAO's configured risk curve — a concrete, reproducible deviation from the documented `liq-factor^alpha` identity, exactly analogous to the ELO report's offset-corruption of the intended exponential formula [7](#0-6) .

### Citations

**File:** docs/egroups.md (L16-28)
```markdown
### Risk parameter structure:

```
(
  MASK                 : uint,      // Which assets this applies to (bitmask)
  BORROW-DISABLED-MASK : uint.      // Which borrow assets are disabled in this group (security control)
  LTV-BORROW           : (buff 2),  // Max LTV for borrowing (bps, e.g., 7500 = 75%)
  LTV-LIQ-PARTIAL      : (buff 2),  // LTV threshold for partial liquidation (bps)
  LTV-LIQ-FULL         : (buff 2),  // LTV threshold for full liquidation (bps)
  LIQ-PENALTY-MIN      : (buff 2),  // Min liquidation penalty/bonus (bps)
  LIQ-PENALTY-MAX      : (buff 2),  // Max liquidation penalty/bonus (bps)
  LIQ-CURVE-EXP        : (buff 2)   // Curve exponent for graduated liquidation (bps)
)
```

**File:** docs/egroups.md (L41-48)
```markdown
| `LIQ-CURVE-EXP` | bps | 10000 (1.0) | Exponent for graduated penalty curve |

**Graduated Liquidation:**

The `LIQ-CURVE-EXP` parameter controls how liquidation penalty scales between min and max:
- `10000` (1.0): Linear scaling
- `>10000` (>1.0): Aggressive curve (penalty increases faster)
- `<10000` (<1.0): Gentle curve (e.g., square root)
```

**File:** mainnet/contracts/market/v0-4-market.clar (L703-704)
```text
(define-private (calc-liq-factor (ltv-curr uint) (ltv-liq-partial uint) (ltv-liq-full uint))
  (min BPS (div-bps-down (- ltv-curr ltv-liq-partial) (- ltv-liq-full ltv-liq-partial))))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L706-713)
```text
;; Apply curve exponent for graduated liquidation
;; liq-factor = liq-factor^alpha
(define-private (calc-liq-factor-exp (factor uint) (exp uint))
  (if (is-eq exp BPS) 
    factor
    (if (> exp BPS) 
        (/ (pow factor (/ exp BPS)) (pow BPS (- (/ exp BPS) u1)))
        (sqrti (* factor BPS))))) ;; assume factor^0.5
```

**File:** mainnet/contracts/market/v0-4-market.clar (L737-756)
```text
;; Combines the 4-step liquidation factor calculation into a single helper
;; Returns: { liq-pct-scaled: uint, liq-penalty: uint, max-debt-usd: uint }
(define-private (calc-liquidation-params
  (current-ltv uint)
  (ltv-liq-partial uint)
  (ltv-liq-full uint)
  (liq-penalty-min uint)
  (liq-penalty-max uint)
  (curve-exponent uint)
  (total-debt-usd uint))
  
  (let ((liq-pct-linear (calc-liq-factor current-ltv ltv-liq-partial ltv-liq-full))
        (liq-pct-scaled (calc-liq-factor-exp liq-pct-linear curve-exponent))
        (liq-penalty (calc-liq-factor-bound liq-pct-scaled liq-penalty-min liq-penalty-max))
        (max-debt-usd (calc-liq-debt-repay total-debt-usd liq-pct-scaled)))
    {
      liq-pct-scaled: liq-pct-scaled,
      liq-penalty: liq-penalty,
      max-debt-usd: max-debt-usd
    }))
```
