### Title
Any single accrual/oracle failure on one asset permanently bricks deposit, redeem, borrow, repay, and collateral operations for users with cross-asset positions - (`local-testing/contracts/market/market.clar`, `mainnet/contracts/market/v0-4-market.clar`)

### Summary
`market.clar`/`v0-4-market.clar` fold over a user's *entire* debt and collateral list on every `borrow`, `repay`, `collateral-add`, `collateral-remove`, and `liquidate` call, calling `(unwrap-panic (accrue-and-cache ...))` for each asset the user holds. `accrue-and-cache` forwards to `vault-accrue`, which calls the underlying vault's public `accrue` function. Because the loop uses `unwrap-panic` (not a graceful `asserts!`/`try!` that returns an error code), a single failing/reverting `accrue` call on *any one* of the user's collateral or debt assets aborts the entire transaction — for every action the user tries to take, on every asset, from then on. This mirrors the Notional `_redeemMaturedPositions` bug class: an inner loop over N positions, each doing an external call that can fail, wired via a mandatory pre-hook into every core user-facing operation (issue/redeem there; borrow/repay/collateral-add/collateral-remove/liquidate here).

### Finding Description
`accrue-user-debts`/`accrue-debt-asset` and `accrue-user-collateral`/`accrue-collateral-asset` iterate the caller's full position list and call: [1](#0-0) 

`accrue-and-cache` performs `(try! (vault-accrue aid))` on cache miss: [2](#0-1) 

`vault-accrue` simply forwards to each vault's public `accrue`: [3](#0-2) 

Inside a vault's `accrue`, the reserve/treasury mint computation performs an unchecked subtraction as an argument to `mul-div-down`: [4](#0-3) 

`treasury-lp` is computed as `(mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc))`. If `reserve-inc` (the reserve-factor share of the freshly-accrued interest delta) is ever `>= total-assets-preview` — e.g., after a long period without any accrual call on a vault at high utilization, causing `debt-delta` (and thus `reserve-inc`) to spike relative to the vault's remaining underlying assets — this subtraction underflows. Clarity aborts the whole transaction on an unchecked-arithmetic underflow rather than returning a graceful error.

Because this `accrue` call is invoked transitively via `unwrap-panic` from every position-touching market entrypoint (`borrow`, `repay`, `collateral-add`, `collateral-remove`, `liquidate`) for *any* asset appearing in the user's debt/collateral list, once one vault's `accrue` becomes permanently unable to succeed, every user who holds that asset as debt or collateral loses the ability to perform *any* market action, not just on the broken asset but on all of their positions (since the fold aborts the entire `try!`/transaction chain). This is the same "loop-of-external-calls-embedded-in-a-mandatory-hook" bug class as the Notional finding: `moduleIssueHook`/`moduleRedeemHook` calling `_redeemMaturedPositions`, which reverts the entire issuance/redemption if any single fCash redemption fails.

### Impact Explanation
If the underflow (or any other revert path inside a vault's `accrue`) is triggered, users holding that asset as collateral or debt can no longer repay debt, remove collateral, or be cleanly liquidated through the normal path, because every code path that touches their position folds through `accrue-user-debts`/`accrue-user-collateral` with `unwrap-panic`. This is a permanent freezing of funds (collateral/debt positions become unmanageable) and, in the debt-repayment-blocked case, could also prevent liquidators/borrowers from ever reconciling debt, risking protocol insolvency if bad debt cannot be resolved.

### Likelihood Explanation
This requires a specific, narrow arithmetic edge case (`reserve-inc >= total-assets-preview`), which is far less likely than the original Notional bug (any one of many external fCash redemptions failing) but is structurally identical: a single failed inner-loop call embedded via `unwrap-panic`/hard revert in mandatory pre-checks for every core user action. Likelihood is Low-to-Medium — it depends on a vault going a long time without accrual under high utilization/low liquidity plus a non-trivial `fee-reserve` setting, but the code path itself is reachable without any DAO misconfiguration or privileged action, purely through normal usage patterns (nobody calling any market function on that vault for a long stretch).

### Recommendation
- Replace `unwrap-panic` in `accrue-debt-asset`/`accrue-collateral-asset` with propagated `try!`/graceful error handling so a single asset's accrual failure doesn't hard-abort unrelated operations, and consider allowing per-asset recovery (e.g., an admin/DAO function to reset a stuck vault's accrual state).
- Guard the `treasury-lp` computation in each vault's `accrue` with an explicit `if (>= total-assets-preview reserve-inc) ... else` branch (cap `reserve-inc` to `total-assets-preview`) instead of relying on the unchecked subtraction to be safe.
- Add regression tests that force a large `debt-delta` after an extended accrual gap at high utilization to confirm `accrue` never underflows.

### Proof of Concept
1. A vault (e.g., `v0-vault-stx`) accumulates outstanding debt at high utilization and goes without any accrual call for an extended period (nobody deposits/borrows/repays on it).
2. `next-index`/`next-liquidity-index` compute a large `debt-delta` since `last-update`, producing `reserve-inc = debt-delta * fee-reserve / BPS`, per: [5](#0-4) 
3. If `total-assets-preview() < reserve-inc`, the `(- (total-assets-preview) reserve-inc)` expression underflows, and Clarity aborts the `accrue` call with a runtime arithmetic-underflow error (not a graceful `err`).
4. Any market call touching that vault's asset — `borrow`, `repay`, `collateral-add`, `collateral-remove`, `liquidate` — invokes `accrue-user-debts`/`accrue-user-collateral`, which call `(unwrap-panic (accrue-and-cache aid))`: [6](#0-5) 
5. Since `unwrap-panic` on a hard runtime abort simply re-aborts, every subsequent market operation touching any position that includes this asset now fails permanently, freezing user funds until a contract upgrade fixes the arithmetic.

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L189-196)
```text
(define-private (vault-accrue (aid uint))
  (if (is-eq aid STX) (contract-call? .v0-vault-stx accrue)
  (if (is-eq aid sBTC) (contract-call? .v0-vault-sbtc accrue)
  (if (is-eq aid stSTX) (contract-call? .v0-vault-ststx accrue)
  (if (is-eq aid USDC) (contract-call? .v0-vault-usdc accrue)
  (if (is-eq aid USDH) (contract-call? .v0-vault-usdh accrue)
  (if (is-eq aid stSTXbtc) (contract-call? .v0-vault-ststxbtc accrue)
  ERR-UNKNOWN-VAULT)))))))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L245-257)
```text
(define-private (accrue-and-cache (aid uint))
  (let ((cache-key { timestamp: stacks-block-time, aid: aid })
        (cached? (map-get? index-cache cache-key)))

    (match cached?
      ;; cache HIT: return cached value (1 read only)
      cached-indexes (ok cached-indexes)

      ;; cache MISS: accrue and cache (vault-accrue now returns indexes)
      (let ((indexes (try! (vault-accrue aid))))
        ;; store in cache
        (map-set index-cache cache-key indexes)
        (ok indexes)))))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L259-293)
```text
(define-private (accrue-user-debts (debt-list (list 64 { aid: uint, scaled: uint})))
  (fold accrue-debt-asset debt-list { success: true }))

(define-private (accrue-debt-asset
  (debt-entry { aid: uint, scaled: uint })
  (acc { success: bool }))
  (begin
    ;; this will use cache if available, accrue if not
    (unwrap-panic (accrue-and-cache (get aid debt-entry)))
    acc))

(define-private (accrue-user-collateral (coll-list (list 64 {aid: uint, amount: uint})))
  (fold accrue-collateral-asset coll-list { success: true }))

(define-private (accrue-collateral-asset
  (coll-entry { aid: uint, amount: uint })
  (acc { success: bool }))
  (let ((aid (get aid coll-entry)))
    ;; Only accrue if asset is a registered ztoken
    (if (is-ztoken aid)
        ;; ZToken: map to underlying vault routing ID and accrue
        ;; zSTX(1)->STX(0), zsBTC(3)->sBTC(2), zstSTX(5)->stSTX(4), zUSDC(7)->USDC(6), zUSDH(9)->USDH(8), zstSTXbtc(11)->stSTXbtc(10)
        (let ((vault-id (if (is-eq aid zSTX) STX
                        (if (is-eq aid zsBTC) sBTC
                        (if (is-eq aid zstSTX) stSTX
                        (if (is-eq aid zUSDC) USDC
                        (if (is-eq aid zUSDH) USDH
                        (if (is-eq aid zstSTXbtc) stSTXbtc
                        ;; will cause ERR-UNKNOWN-VAULT with any value over 64
                        u100))))))))
          (begin
            (unwrap-panic (accrue-and-cache vault-id))
            acc))
        ;; Non-ztoken: skip accrual (no liquidity index needed)
        acc)))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L843-863)
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
