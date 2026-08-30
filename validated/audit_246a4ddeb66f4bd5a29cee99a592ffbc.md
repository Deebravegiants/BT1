### Title
Protocol fee-reserve minting rounds down to zero on the USDC vault due to precision loss in low-decimal `debt-delta` × `fee-reserve` calculation - (File: `mainnet/contracts/vault/v0-vault-usdc.clar`)

### Summary
The `accrue` function in `mainnet/contracts/vault/v0-vault-usdc.clar` mints treasury fee shares (`treasury-lp`) proportional to `debt-delta` (the interest accrued to borrowers since `last-update`) scaled by `fee-reserve`/`BPS`. Because the USDC vault operates on 6-decimal raw asset units (`DECIMALS u6`), `debt-delta` for short accrual intervals is a very small integer, and `mul-div-down` (integer division, rounds down) frequently truncates `reserve-inc` to `u0`. Since `last-update` is unconditionally advanced to the current block whenever the index changes, the un-minted fee for that interval is permanently and irrecoverably lost — this is the same root-cause pattern as Sherlock M-18 in Sentiment V2's `Pool.accrue()`.

### Finding Description
`accrue` computes debt growth and the treasury's cut of it: [1](#0-0) 

The fee-reserve computation `reserve-inc` is `mul-div-down debt-delta fee-reserve BPS` — an integer division by `BPS = u10000`. `debt-delta` itself is derived from `mul-div-down scaled-principal idx INDEX-PRECISION` differences, denominated in raw 6-decimal USDC units: [2](#0-1) 

For a realistic USDC pool (thousands of dollars borrowed) accruing over a short interval, `debt-delta` can easily be in the single-digit-to-low-double-digit range of raw units (since USDC has only 6 decimals versus the 18-decimal precision assumed by most rate math). When `debt-delta * fee-reserve < BPS` (e.g. `debt-delta` small and `fee-reserve` a modest basis-point value), `reserve-inc` truncates to `u0`, so no `treasury-lp` is minted: [3](#0-2) 

Crucially, whenever the index changes (i.e., any nonzero time has elapsed), `last-update` is advanced regardless of whether `reserve-inc` rounded to zero: [4](#0-3) 

This breaks the identity that should hold between interest generated for the pool (`debt-delta`, which is being added to every depositor's/lender's claim via `total-assets`) and the fee actually forwarded to the DAO treasury (`treasury-lp` minted from `reserve-inc`): **interest created ≠ fee forwarded**. Because `debt-delta` still increases borrower debt and depositor claims each time `accrue` is called (borrowers pay the full interest, lenders' underlying claim increases via `total-assets`), but the treasury's proportional cut can be silently zeroed by rounding, and the checkpoint (`last-update`) resets so the lost fee-window can never be recovered on a later, larger accrual.

Any unprivileged account (a borrower calling `system-borrow`/`system-repay`, or a depositor calling `deposit`) can trigger `accrue` at will and cheaply, since these are the standard user-facing entry points that call `accrue` as their first step. By interacting frequently (short intervals between calls), an attacker (or normal high-frequency market activity) keeps each interval's `debt-delta * fee-reserve` below the `BPS` rounding threshold, causing the fee-reserve mint to round to zero on every call while the underlying interest still fully accrues to borrower debt and lender claims.

### Impact Explanation
This causes a permanent loss of the protocol's/DAO treasury's fee-reserve share of interest — i.e., theft/loss of unclaimed yield that would otherwise have been minted as `treasury-lp` to `.dao-treasury`. The loss compounds over time and is not a one-off event: the checkpoint-and-reset design of `accrue` guarantees each rounded-down interval's fee is gone forever, matching the reasoning validated by the Sherlock M-18 judgment (Medium severity, "theft of unclaimed yield/fee revenue").

### Likelihood Explanation
Any user of the USDC vault (the only in-scope stablecoin vault confirmed with `DECIMALS u6`) naturally triggers `accrue` on every `deposit`, `system-borrow`, and `system-repay`. No privileged role or DAO action is required. High-frequency, low-value interactions (deposits, small borrows/repays, or direct external calls that invoke `accrue`) are cheap and can be sustained indefinitely, especially on the low-fee Stacks chain, making the precision-loss condition (`debt-delta * fee-reserve < BPS`) easy to hit and repeat.

### Recommendation
Scale internal debt/asset accounting to a fixed high precision (e.g., 18 decimals) independent of the underlying asset's native decimals, only truncating back down to native decimals at the point of external transfer. Alternatively, accumulate un-minted fee remainder (the truncated portion of `reserve-inc`) across `accrue` calls instead of discarding it when `last-update` is advanced, so that fee dust compounds until it is large enough to mint rather than being permanently lost.

### Proof of Concept
1. Deploy/observe `mainnet/contracts/vault/v0-vault-usdc.clar` with a nonzero `fee-reserve` and a realistic total-borrowed amount (e.g., a few thousand USDC, 6 decimals).
2. Call `system-borrow`/`deposit` (which invoke `accrue`) at short intervals (seconds to a few minutes).
3. Each call computes `debt-delta` from `mul-div-down scaled-principal idx INDEX-PRECISION` differences in raw 6-decimal units; for short intervals this is a small integer.
4. `reserve-inc` = `mul-div-down debt-delta fee-reserve BPS` rounds to `u0` whenever `debt-delta * fee-reserve < BPS` — confirm via `calc-treasury-lp-preview`/the inline `accrue` logic at [5](#0-4)  that no `treasury-lp` is minted despite `index`/`last-update` advancing.
5. Repeat step 2 indefinitely; since `last-update` always advances, verify that cumulatively the treasury receives systematically less `treasury-lp` than the true proportional share of total interest accrued to `total-debt`, demonstrating irrecoverable fee loss over time — directly analogous to the PoC methodology (`testZeroFeesPaid`) in the referenced Sherlock report.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L17-27)
```text

;; -- Core configuration
(define-constant UNDERLYING 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx)
(define-constant NAME "Zest USDC")
(define-constant SYMBOL "zUSDC")
(define-constant DECIMALS u6)

;; -- Precision & scaling
(define-constant BPS u10000)
(define-constant PRECISION u100000000)
(define-constant INDEX-PRECISION u1000000000000)  ;; 1e12 for index calculations
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L348-359)
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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L841-865)
```text
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
  (let (
      (states (var-get pause-states))
```
