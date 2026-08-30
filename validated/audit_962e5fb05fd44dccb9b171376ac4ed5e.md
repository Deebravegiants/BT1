This confirms the mechanism. I have enough to finalize the finding.

## Analysis

The `accrue` function in each vault (e.g., `v0-vault-usdc.clar`) computes the DAO treasury's protocol fee on every accrual with a two-stage floor-division: [1](#0-0) 

`debt-delta` is computed in raw underlying-token units (USDC = 6 decimals), then `reserve-inc = mul-div-down(debt-delta, fee-reserve, BPS)` truncates towards zero, and `treasury-lp` (the vault-share amount minted to `.dao-treasury`) is only minted `(if (> reserve-inc u0) ... u0)`. Critically, once `next != idx`, the code unconditionally does `(var-set index next)` and `(var-set last-update stacks-block-time)` — meaning the index/time base is rebased on every call regardless of whether `reserve-inc` rounded to zero: [2](#0-1) 

Because `mul-div-down` is used identically for the constants: [3](#0-2) 

`BPS = 10000`, so for any `debt-delta < 10000/fee-reserve` (e.g., with a 1000 bps / 10% reserve factor, any `debt-delta < 10` raw USDC units, i.e. < $0.00001), `reserve-inc` truncates to exactly 0 and no `treasury-lp` shares are minted — yet the index has already advanced and `last-update` has already been rebased, so this lost fee fraction is never recovered on a subsequent call (unlike the vault's own debt index, which is deferred via the "don't rebase last-update unless index changed" guard). This mirrors the report's root cause exactly: a token with fewer decimals (6 for USDC/USDH, 8 for sBTC) combined with frequent small time-deltas between accruals (which happens naturally whenever users transact often, since every `deposit`/`redeem`/`borrow`/`repay` call triggers `accrue`) makes `debt-delta` per call tiny, systematically truncating the treasury's reserve-factor cut to zero while suppliers still receive their full, un-diluted share of interest.

### Title
Per-accrual reserve-fee truncation with low-decimal underlying tokens permanently starves DAO treasury of protocol interest revenue - (File: `mainnet/contracts/vault/v0-vault-usdc.clar`, `v0-vault-usdh.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-ststx.clar`)

### Summary
`accrue()` in the vault contracts computes the protocol's reserve-factor cut (`reserve-inc`) via floor division of `debt-delta * fee-reserve / BPS`, and mints the equivalent vault shares to `.dao-treasury` only if `reserve-inc > 0`. Because the vault index and `last-update` are unconditionally rebased whenever the accrual causes any index change at all — independent of whether the fee portion itself rounded to zero — any accrual period whose `debt-delta` is small enough (frequent calls, low-decimal underlying such as USDC/USDH at 6 decimals) causes the reserve fee to be permanently lost rather than deferred.

### Finding Description
`calc-multiplier-delta`/`next-index` compute interest using `INDEX-PRECISION` (1e12), which is fine-grained enough that the debt index itself rarely truncates to a no-op, and the code explicitly defers `last-update` when the index doesn't change (protecting index-level interest from truncation loss). However, this deferral protection is not applied to the separate `reserve-inc` computation:
```
(reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
(treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0))
``` [4](#0-3) 
`BPS = u10000` [5](#0-4) , so `reserve-inc` floors to 0 whenever `debt-delta < BPS / fee-reserve` (e.g., <10 raw USDC units for a 10% reserve factor). Immediately after, regardless of `reserve-inc`, the code does `(var-set index next)` and `(var-set last-update stacks-block-time)` whenever `idx != next`: [2](#0-1) 
This rebases the base for the *next* `debt-delta` calculation to start from the already-realized `next` index, so the fractional fee corresponding to this period's `debt-delta` is not carried forward — it is permanently dropped. This breaks the identity: `sum(fee owed over all accrual periods) == fee actually minted to dao-treasury`. Suppliers receive the full undiluted interest (since `total-assets` already reflects the full `debt-delta`), while the protocol's designed 10% cut silently evaporates for any accrual granular enough to trigger this rounding, i.e. whenever a low-decimal-underlying vault is accrued frequently by ordinary user activity (deposits/borrows/repays/redeems all call `accrue`).

### Impact Explanation
This is a permanent, protocol-wide loss of unclaimed protocol yield (the DAO treasury's reserve-factor revenue) with no possibility of recovery, since the debt base used for the next period's `debt-delta` calc has already moved past the point where the lost fraction could be re-captured. Given USDC/USDH vaults use 6 decimals and sBTC uses 8, and every vault-touching user action calls `accrue`, an attacker (or just organic high-frequency usage) can keep `debt-delta` per call below the truncation threshold indefinitely, ensuring `dao-treasury` never receives its share of interest on that flow of debt.

### Likelihood Explanation
High under normal/organic conditions for the lower-decimal-underlying vaults (USDC, USDH) at low-to-moderate utilization/interest rates, and trivially forceable by an attacker who simply calls any state-mutating vault function (e.g., tiny repeated `system-repay`/`deposit`/`redeem`) at high frequency to keep each `debt-delta` below the truncation floor — no privileged access or DAO action required.

### Recommendation
Track the fractional/undistributed portion of `reserve-inc` (and/or `debt-delta`) in a persistent remainder accumulator across accruals instead of discarding it when it truncates to zero, so the reserve-factor fee is eventually minted once the accumulated remainder becomes non-zero — analogous to how the debt index's `last-update` is deferred rather than rebased on a no-op.

### Proof of Concept
1. Deploy/observe `vault-usdc` (6-decimal USDC underlying) with `fee-reserve` = 1000 bps (10%) and an active positive borrow rate.
2. Repeatedly call any accrue-triggering entry point (e.g., `deposit` with `min-out u0`, or `system-repay` with `amount u1`) in quick succession such that each `time-delta` between calls is small enough that `debt-delta` computed via `mul-div-down(scaled-principal, next-idx-minus-idx, INDEX-PRECISION)` stays below `BPS / fee-reserve` (10 raw USDC units for the example rate).
3. Observe across many such calls that `reserve-inc` is `u0` every time, so the `(if (> treasury-lp u0) (try! (ft-mint? zft treasury-lp .dao-treasury)) false)` branch never executes [6](#0-5) , while `index`/`last-update` are still advanced each time, permanently consuming the corresponding interest period without ever crediting `dao-treasury`.
4. Compare `dao-treasury`'s `zUSDC` balance after N high-frequency small accruals vs. a single accrual covering the same aggregate `debt-delta` in one call — the latter mints a non-zero `treasury-lp`, the former mints zero, demonstrating the value that is permanently forfeited purely due to call cadence/decimal granularity.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L25-28)
```text
(define-constant BPS u10000)
(define-constant PRECISION u100000000)
(define-constant INDEX-PRECISION u1000000000000)  ;; 1e12 for index calculations
(define-constant SECONDS-PER-YEAR-BPS (* u31536000 BPS))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L841-861)
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
```
