### Title
Protocol reserve fee on interest can be permanently avoided via frequent micro-accruals - (File: `mainnet/contracts/vault/v0-vault-usdh.clar` and equivalent `v0-vault-*.clar` vaults)

### Summary
The vault's `accrue` function mints a "treasury LP" share to the DAO representing `fee-reserve` bps of the interest accrued since the last update. This fee is computed with Solidity/Clarity-style integer division that truncates (rounds down) to zero for small interest deltas, exactly the bug class described in the reference report. Because `accrue` is a permissionless, publicly callable function that any caller can invoke at will, an attacker (or simply a bot calling it every block) can force the interest to be recognized in many tiny increments, each of which rounds the protocol's fee share to zero, while the full un-fee'd interest still flows into `total-assets` (and thus into LP share value). This permanently denies the DAO/treasury its share of yield.

### Finding Description
`accrue` computes the interest delta and the treasury's cut like this: [1](#0-0) 

The fee ("reserve-inc") is calculated using `mul-div-down`, i.e. Clarity's native truncating integer division: [2](#0-1) [3](#0-2) 

`debt-delta` (the interest that accrued since the last `accrue` call) is itself a function of `time-delta = stacks-block-time - last-update`: [4](#0-3) 

Since `accrue` is a `define-public` function with no caller-authorization check (unlike e.g. `system-borrow`, which calls `check-caller-auth`), any account can call it. By calling `accrue` immediately/frequently (small `time-delta` per call), `debt-delta` per call can be kept small enough that:

```
reserve-inc = (debt-delta * fee-reserve) / BPS = 0
```

whenever `debt-delta * fee-reserve < BPS (10000)`. When this happens, no treasury-lp shares are minted to `.dao-treasury`: [5](#0-4) 

However, the underlying `index` (and hence `total-debt`/`total-assets`, which drives LP share value) advances by the full `debt-delta` regardless of whether the fee rounded to zero: [6](#0-5) 

This exactly mirrors the referenced Primitive Protocol bug: fees computed as `(amount * feeRate) / DENOMINATOR` truncate to zero for sufficiently small `amount` (here, `debt-delta`), and an attacker fully controls the granularity of that "amount" by controlling how often they call the permissionless `accrue` function.

### Impact Explanation
The identity that should hold is:

```
interest_accrued (added to total-assets) = interest_to_LPs + interest_to_treasury (fee-reserve share)
```

By spamming `accrue()` with minimal time gaps, an attacker forces `interest_to_treasury ≈ 0` for the vault's entire lifetime while `interest_accrued` continues to flow in full into `total-assets`, i.e. into existing LP token holders' share value. The DAO's protocol-fee share of interest income (unclaimed yield) is permanently redirected to LPs instead of the treasury. Per the rules, this is theft/permanent freezing of unclaimed yield belonging to the protocol treasury — classified as High impact.

### Likelihood Explanation
`accrue` is public, has no caller-authorization gate, costs only the gas/transaction fee of a no-op-like call, and is trivially automatable (e.g., call once per block or once per transaction in a busy vault). Any user, or even MEV/bot infrastructure incidental to normal vault activity, can trigger this behavior; deliberate exploitation requires no privileged access and no flashloan.

### Recommendation
- Avoid computing the treasury fee from a per-call delta that can be made arbitrarily small. Options:
  - Track un-collected/accumulated interest fee-eligible remainder across calls (carry the rounding remainder forward) rather than resetting `debt-delta`/`reserve-inc` to a fresh computation each call.
  - Enforce a minimum `time-delta` before `accrue` performs the interest/fee computation (e.g., a cooldown), or make fee accrual epoch-based instead of continuously call-triggered.
  - Compute the reserve fee proportionally to `index`/`lindex` divergence in a way that is monotonic and reconciled at redemption time rather than per-call, so it cannot be starved by call frequency.
  - At minimum, use round-up (`mul-div-up`) for the reserve fee combined with dust-remainder carry-forward so the treasury's total collected fee converges to the correct amount over time regardless of call granularity.

### Proof of Concept
1. Attacker (or bot) observes the vault has outstanding borrowed principal generating interest (`total-borrowed > 0`).
2. Attacker calls `accrue()` repeatedly, back-to-back (every block or even every transaction if `stacks-block-time` updates enough to produce `time-delta > 0` but small).
3. On each call, `next-index()` computes a very small `multiplier`/`debt-delta` because `time-delta` is minimal.
4. `reserve-inc = mul-div-down(debt-delta, fee-reserve, BPS)` evaluates to `0` on each call because `debt-delta * fee-reserve < 10000`.
5. `index` (and therefore `total-debt`/`total-assets`) still advances each call by the (small but nonzero) `debt-delta`, so LPs' share value keeps growing.
6. Repeating this over the vault's lifetime results in the DAO/treasury receiving `0` treasury-lp shares in total, versus receiving a meaningful, non-zero amount had `accrue` been called at normal (larger interval) frequency — permanently forfeiting the protocol's designed fee-reserve cut of interest to LPs instead.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L147-148)
```text
(define-private (mul-div-down (x uint) (y uint) (z uint))
  (/ (* x y) z))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L326-337)
```text
(define-private (total-debt)
  (calc-cumulative-debt (var-get principal-scaled) (var-get index)))

(define-private (debt-preview)
  (calc-cumulative-debt (var-get principal-scaled) (next-index)))

(define-private (total-assets)
  (let ((current-assets (var-get assets))
        (debt (total-debt))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L348-359)
```text
(define-private (calc-treasury-lp-preview)
  (let ((scaled-principal (var-get principal-scaled))
        (idx (var-get index))
        (next (next-index))
        (old-debt (mul-div-down scaled-principal idx INDEX-PRECISION))
        (new-debt (mul-div-down scaled-principal next INDEX-PRECISION))
        (debt-delta (if (> new-debt old-debt) (- new-debt old-debt) u0))
        (reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
        (ta-preview (total-assets-preview)))
    (if (> reserve-inc u0)
        (mul-div-down reserve-inc (total-supply) (- ta-preview reserve-inc))
        u0)))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L377-388)
```text
(define-private (next-index)
  (let ((states (var-get pause-states))
        (idx (var-get index)))
    (if (get accrue states)
        idx
        (let (
            (rate (interest-rate))
            (time-delta (- stacks-block-time (var-get last-update)))
            (multiplier (if (is-eq time-delta u0)
                          INDEX-PRECISION
                          (calc-multiplier-delta rate time-delta true))))
          (calc-index-next idx multiplier)))))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L839-863)
```text
          (ok { index: idx, lindex: lidx })
          ;; NOT PAUSED: Normal accrual logic
          (let ((next (next-index))
                (nliq (next-liquidity-index))
                (scaled-principal (var-get principal-scaled))
                (old-debt (mul-div-down scaled-principal idx INDEX-PRECISION))
                (new-debt (mul-div-down scaled-principal next INDEX-PRECISION))
                (debt-delta (if (> new-debt old-debt) (- new-debt old-debt) u0))
                (reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
                (treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0)))
            (if (not (is-eq idx next))
                (var-set index next)
                false)
            (if (not (is-eq lidx nliq))
                (var-set lindex nliq)
                false)
            (if (> treasury-lp u0)
                (try! (ft-mint? zft treasury-lp .dao-treasury))
                false)
            (if (or (not (is-eq idx next)) (not (is-eq lidx nliq)))
                (var-set last-update stacks-block-time)
                false)
            (ok { index: next, lindex: nliq })))))

(define-public (system-borrow (amount uint) (receiver principal))
```
