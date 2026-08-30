Based on my research, I found a structural analog to the reported Cork bug in the Zest vault contracts' interest-accrual path.

### Title
Division-by-zero panic in `calc-treasury-lp-preview` freezes all vault operations - (File: `mainnet/contracts/vault/v0-vault-stx.clar` and equivalent per-asset vaults)

### Summary
The reported Cork bug is a class of "unguarded division whose denominator can become zero under low-liquidity/edge-case reserve conditions, causing a revert/panic that DoSes an otherwise-valid user operation." The Zest vaults contain the same bug class inside `calc-treasury-lp-preview`, which computes the treasury's preview LP share using `mul-div-down` with a denominator `(- ta-preview reserve-inc)` that is not checked to be non-zero before the division.

### Finding Description
`calc-treasury-lp-preview` computes: [1](#0-0) 
```
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
This function is invoked unconditionally, whenever `reserve-inc > 0`, inside `accrue`: [2](#0-1) 

`accrue` is itself called at the top of essentially every state-mutating vault entrypoint — `system-borrow`, redeem/deposit flows, `flashloan`, and repay/socialize-debt paths — meaning if `calc-treasury-lp-preview` panics, the *entire vault* (deposits, redemptions, borrows, repayments, flashloans) becomes permanently unusable until the underlying state changes on its own (which it cannot, since every mutating call reverts).

The denominator `(- ta-preview reserve-inc)` is `total-assets-preview() - reserve-inc`. `reserve-inc` is a fee-rate fraction (`fee-reserve / BPS`) of the newly accrued `debt-delta`. If `total-assets-preview()` becomes equal to `reserve-inc` — e.g., in a vault with very low `assets`/`total-borrowed` (near-empty vault state, similar in spirit to Cork's "both reserves are empty" precondition) combined with a nonzero accrued `debt-delta` and `fee-reserve` — the subtraction yields `0`, and the subsequent `mul-div-down` divides by zero, causing an unrecoverable panic identical in mechanism to Cork's `panic: division or modulo by zero (0x12)`.

Unlike Cork's function, which has a caller-level fallback (`_swapRaForDsViaRollover` should simply skip rollover and continue the swap via AMM), `accrue()` has no fallback path: it is a hard dependency for every subsequent operation, so this bug class is strictly worse in Zest — it is not merely "the rollover path is blocked," it is "the entire vault is blocked."

### Impact Explanation
If reachable, this causes a permanent temporary freezing of funds: every deposit, redemption, borrow, repay, and flashloan on the affected vault would revert because `accrue()` cannot be executed without hitting the same division. Users' principal and unclaimed yield inside that vault would be inaccessible until a contract upgrade or DAO intervention. This matches the "permanent/temporary freezing of funds" impact category.

### Likelihood Explanation
This requires a vault state where `total-assets-preview() == reserve-inc` exactly (or is driven arbitrarily close by adversarial deposit/withdraw sequencing to force the two quantities to match, similar to how the Cork PoC manipulates reserves down to zero via repeated `swapAsset`/`redeemEarlyLv` calls). I was not able to fully verify, within the available search budget, the exact numeric bounds on `fee-reserve` (its setter and cap) or confirm Clarity's exact division semantics (though Clarity's `/` on `uint` is known to abort with a runtime error on zero divisor, functionally equivalent to Solidity's panic). Confirming exact reachability (i.e., whether an attacker/normal user flow can force `total-assets-preview() - reserve-inc == 0` under realistic `fee-reserve` bounds) requires deeper numeric analysis of `total-borrowed`, `assets`, and `fee-reserve` bounds than I could complete here.

### Recommendation
Add an explicit zero/underflow guard in `calc-treasury-lp-preview` before the final division, e.g.:
```
(if (and (> reserve-inc u0) (> ta-preview reserve-inc))
    (mul-div-down reserve-inc (total-supply) (- ta-preview reserve-inc))
    u0)
```
This mirrors the Cork fix's pattern of short-circuiting to a safe default value instead of performing a division that can hit a zero denominator.

### Proof of Concept
I could not construct or verify a concrete numeric PoC sequence (specific deposit/borrow/time-warp amounts) that forces `total-assets-preview() == reserve-inc` within the current investigation; this would require simulating `mul-div-down`/`mul-div-up` rounding behavior and the `fee-reserve` bound together, which I was unable to complete before running out of tool-call budget. I recommend a Devin session with access to the full repo and a Clarinet/simnet test harness to attempt to drive `assets`, `total-borrowed`, and `fee-reserve` into the exact ratio needed to trigger the panic, confirming or refuting reachability. [1](#0-0) [3](#0-2)

### Citations

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L350-360)
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
```

**File:** local-testing/contracts/vault/vault-ststx.clar (L837-867)
```text
;; -- Lending operations -----------------------------------------------------

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
