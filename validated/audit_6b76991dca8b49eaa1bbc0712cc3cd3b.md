### Title
Reserve-fee rounding lets the permissionless `accrue()` be called in tiny increments to zero out protocol treasury minting - (File: `mainnet/contracts/vault/v0-vault-usdc.clar` and equivalent `v0-vault-*.clar` vault contracts)

### Summary
The `accrue()` function in each vault contract computes the protocol's reserve share of interest as `reserve-inc = (debt-delta * fee-reserve) / BPS`, then mints treasury shares only `(if (> reserve-inc u0) ...)`. Because `accrue()` is a public, unauthenticated function that anyone can invoke at any time, an attacker can call it every block (fragmenting the interest-accrual window into tiny slices) so that each call's `debt-delta` stays below `BPS / fee-reserve`, causing `reserve-inc` to round to zero every time while the borrower's `index`-based debt still fully accrues.

### Finding Description
`accrue()` updates the borrow `index`/`lindex` unconditionally based on elapsed time, then derives the protocol's cut of the interest earned since `last-update`: [1](#0-0) 

```
(debt-delta (if (> new-debt old-debt) (- new-debt old-debt) u0))
(reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
(treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0))
```

`reserve-inc` uses integer division (`mul-div-down`) and truncates to zero whenever `debt-delta * fee-reserve < BPS`. Since `index`/`lindex`/`last-update` are still advanced regardless of whether `treasury-lp` ends up minted, the borrower's full debt keeps accruing to the vault via `debt-preview`/`total-debt` (which feeds `total-assets`, increasing the redemption value for all zft holders), but the reserve-factor's share that should have been split off to `.dao-treasury` is silently lost for that accrual window because `treasury-lp` was computed as `u0` and the `(if (> treasury-lp u0) (try! (ft-mint? ...)) false)` branch never fires.

This is structurally the same rounding-fragmentation bug as the referenced report: a fee (there, `ownerShare`; here, `reserve-inc`) is computed via integer division on a per-call basis, and by keeping the per-call input (`_numOfTokensToBuy` there, elapsed-time-driven `debt-delta` here) small enough, the fee can be made to round to zero on every single call. Because `accrue()` has no access control (unlike `system-borrow`/`system-repay`, which call `check-caller-auth`), any address can call it as frequently as blocks allow, repeatedly resetting `last-update` and re-triggering a fresh, tiny `debt-delta` window each time. [2](#0-1) 

The value identity broken is "interest created versus interest distributed": borrowers pay 100% of the interest baked into the index (fully reflected in `total-assets`/`total-debt`), but the reserve-factor's designated share of that interest is never minted to the DAO treasury when an attacker keeps forcing `reserve-inc` to zero, so that share is effectively redirected entirely to liquidity-provider share value instead of the protocol.

### Impact Explanation
This does not cause insolvency or theft of principal, but it causes the protocol to permanently lose its accrued/unclaimed protocol-reserve yield on every accrual event that an attacker fragments below the rounding threshold. Given that `fee-reserve` is typically expressed in BPS (out of `BPS` = 10000) and interest per short block interval on realistic debt sizes can easily be a handful of base units, an attacker calling `accrue()` every block can keep `debt-delta * fee-reserve` under `BPS` for extended periods, denying the treasury its yield share while suppliers still receive full interest value. This matches "theft/freezing of unclaimed yield" impact.

### Likelihood Explanation
Likelihood is high: `accrue()` requires no permission or fee beyond gas, and any address can call it as frequently as block cadence allows across all `v0-vault-*` contracts (`v0-vault-usdc`, `v0-vault-stx`, `v0-vault-sbtc`, `v0-vault-ststx`, `v0-vault-ststxbtc`, `v0-vault-usdh`), all of which share the identical accrual logic.

### Recommendation
Do not gate treasury minting purely on the per-call `reserve-inc > 0` check computed from a possibly-tiny `debt-delta`. Instead, accumulate un-minted reserve remainder across calls (carry a `pending-reserve` variable that persists rounding remainders between `accrue()` invocations) so fragmentation cannot cause the protocol to lose its fee share, mirroring the report's suggested fix of rejecting/deferring computations that round the fee to zero instead of silently dropping it.

### Proof of Concept
1. Attacker (or anyone) monitors a vault, e.g. `v0-vault-usdc`, with a non-trivial `fee-reserve` (say 1000 bps) and typical `BPS` = 10000.
2. Instead of letting interest accumulate over a normal interval (e.g., an hour) before someone calls `accrue()`, the attacker calls `accrue()` on every new block.
3. Each call computes `debt-delta` for only the elapsed time since the previous block's `accrue()`, which is tiny; `reserve-inc = (debt-delta * fee-reserve) / BPS` rounds down to `0` as long as `debt-delta * fee-reserve < BPS`.
4. `treasury-lp` is thus `u0` every call, so `(ft-mint? zft treasury-lp .dao-treasury)` never executes; meanwhile `index`/`lindex`/`last-update` are still advanced, and the full interest amount is reflected in `total-debt`/`total-assets` for liquidity providers.
5. Repeating this indefinitely denies `.dao-treasury` its designated reserve-factor share of interest for as long as the attacker keeps calling `accrue()` in small enough windows, while suppliers capture the full amount instead.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L833-861)
```text
(define-public (accrue)
  (let ((states (var-get pause-states))
        (idx (var-get index))
        (lidx (var-get lindex)))
      (if (get accrue states)
          ;; PAUSED: Pass-through without reverting
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
```
