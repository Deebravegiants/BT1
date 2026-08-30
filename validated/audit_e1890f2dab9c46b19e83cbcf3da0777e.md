### Title
`lindex`-based zToken collateral pricing permanently diverges from true share value due to double-flooring in `calc-liquidity-rate` - (File: `mainnet/contracts/vault/v0-vault-stx.clar` / `mainnet/contracts/utility/v0-1-data.clar`)

### Summary
The vault computes a separate "liquidity index" (`lindex`) that is used **only** to price zTokens (e.g. `zSTX`, `zUSDC`, `zsBTC`) for collateral valuation in the oracle, while the vault's own ERC4626-style share accounting (`convert-to-shares` / `convert-to-assets`, `total-assets`) uses a fully independent, always-accruing calculation. Because `calc-liquidity-rate` performs two sequential floor divisions, it can round to zero far more easily than the borrow rate that actually drives interest accrual, causing `lindex` to stop growing while the real backing value of zTokens keeps increasing. This is the same root cause pattern as the referenced report (a rate/derived value silently floors to zero and a downstream consumer relies on it as if it were always accurate/non-zero), but here it desynchronizes collateral pricing from actual redeemable value.

### Finding Description
`calc-liquidity-rate` applies two consecutive `mul-bps-down` (floor) operations: [1](#0-0) 

```
(calc-liquidity-rate (var-borrow-rate uint) (util-pct uint) (reserve-factor-bps uint))
  util-applied  = (var-borrow-rate * util-pct) / BPS         ;; floor #1
  liquidity-rate = (util-applied * (BPS - reserve-factor-bps)) / BPS  ;; floor #2
```

At realistic low-utilization values (e.g. `var-borrow-rate = 150` bps, `util-pct = 10` bps → `util-applied = 1500/10000 = 0` after floor), `liquidity-rate` becomes `0` even though the true borrow rate is non-zero. This directly feeds `next-liquidity-index`: [2](#0-1) 

so `lindex` stops growing (multiplier stays at `INDEX_PRECISION`) while `next-index` — used for the borrower debt ledger — is computed directly from the un-scaled `var-borrow-rate` and continues to grow every accrual: [3](#0-2) 

Meanwhile, the vault's actual share-to-asset accounting is fully decoupled from `lindex` and grows correctly from the full interest accrued on debt: [4](#0-3) [5](#0-4) 

However, the protocol's oracle module prices every zToken purely via `lindex`, not via the vault's real share price: [6](#0-5) 

```
zSTX price = stx-price * lindex / INDEX_PRECISION
```

Because `lindex` can get stuck at `INDEX_PRECISION` (representing a 1:1, zero-growth ratio) while the true redeemable value of a zSTX share (via `convert-to-assets`, driven by `total-assets`) keeps rising, the identity that should hold:

`oracle_price(zToken) == redemption_value(zToken)`  (i.e. `stx_price * lindex/PRECISION == stx_price * total_assets/total_supply`)

is broken. The left side stalls at the initial ratio while the right side compounds with every borrower interest payment.

### Impact Explanation
This is used directly for collateral/health-factor computation in `v0-1-data.clar` (`get-asset-price` → LTV / liquidation checks). A user holding zTokens as collateral is assigned less collateral value than they actually hold, permanently understating their true redeemable balance for as long as `liquidity-rate` keeps flooring to zero (which happens systematically at low-to-moderate utilization, a normal and frequent vault state, not an edge case). This is a mispricing of collateral caused by a bug in this protocol's own price-derivation code (in scope per the rules, as it's not a third-party oracle feed issue but an internal calculation feeding the oracle). The practical effect is a persistent under-valuation of yield already accrued to zToken holders when that value is used for borrowing/liquidation purposes — a freezing of that unclaimed yield's utility as collateral, and it can also propagate to unfair liquidations of positions that are actually healthy once the real, un-discounted zToken value is considered.

### Likelihood Explanation
High likelihood: the double-floor condition in `calc-liquidity-rate` triggers whenever `borrow_rate * utilization / BPS` truncates to 0 or a small value, which is common at low utilization — a routine, externally-observable, non-privileged vault state (no special permissions or attacker action required beyond normal deposit/borrow activity that keeps utilization low). No governance or oracle-publisher action is needed; it is a pure function of on-chain vault state and normal usage.

### Recommendation
Do not use `lindex` as an independent collateral-pricing mechanism decoupled from the vault's real share accounting. Either:
1. Derive zToken oracle price directly from the vault's own `convert-to-assets`/`total-assets`/`total-supply` ratio (the same mechanism used for redemptions), eliminating the parallel `lindex` computation entirely, or
2. Fix the precision loss in `calc-liquidity-rate` by combining both scaling factors into a single division (`(var-borrow-rate * util-pct * (BPS - reserve-factor-bps)) / (BPS * BPS)`) with higher intermediate precision, and additionally reconcile `lindex` growth against `total-assets`/`total-supply` growth periodically so the two never diverge below the true accrued value.

### Proof of Concept
1. Vault `v0-vault-stx` starts with `var-borrow-rate = 150` bps (1.5%) at `10` bps utilization (0.1%), `reserve-factor = 1000` bps (10%).
2. Call the vault's `accrue` (triggered indirectly by any deposit/borrow/repay call): `util-applied = (150 * 10) / 10000 = 0` (floors), so `liquidity-rate = (0 * 9000) / 10000 = 0`.
3. `next-liquidity-index` returns the unchanged `lindex` value (multiplier stays `INDEX_PRECISION`) — see [2](#0-1) .
4. `next-index` (borrower debt index) still grows normally from the full un-scaled `150` bps rate, so `total-debt` and, via `debt-delta`, `total-assets`/`total-supply` (through `treasury-lp` minting) increase each accrual — see [7](#0-6) .
5. Repeated accruals over time cause `convert-to-assets(1 zSTX)` to rise above `1 STX`, while `get-asset-price(zSTX) = stx_price * lindex / INDEX_PRECISION` remains pinned at `stx_price` (i.e., `lindex` stuck at `INDEX_PRECISION`), demonstrating the value identity break used for collateral valuation in `v0-1-data.clar`.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L186-190)
```text
(define-private (calc-liquidity-rate (var-borrow-rate uint) (util-pct uint) (reserve-factor-bps uint))
  (let ((util-applied (mul-bps-down var-borrow-rate util-pct))
        (one-minus-rf (- BPS reserve-factor-bps)))
    (mul-bps-down util-applied one-minus-rf)))

```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L334-348)
```text
(define-private (total-assets)
  (let ((current-assets (var-get assets))
        (debt (total-debt))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))

(define-private (total-assets-preview)
  (let ((current-assets (var-get assets))
        (debt (debt-preview))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))

;; -- Treasury LP preview helpers --------------------------------------------
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L379-391)
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

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L392-404)
```text
(define-private (next-liquidity-index)
  (let ((states (var-get pause-states))
        (lidx (var-get lindex)))
    (if (get accrue states)
        lidx
        (let (
            (rate (interest-rate))
            (liquidity-rate (calc-liquidity-rate rate (utilization) (var-get fee-reserve)))
            (time-delta (- stacks-block-time (var-get last-update)))
            (multiplier (if (is-eq time-delta u0)
                          INDEX-PRECISION
                          (calc-multiplier-delta liquidity-rate time-delta false))))
          (calc-index-next lidx multiplier)))))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L463-466)
```text
(define-read-only (get-assets) (ok (var-get assets)))
(define-read-only (get-total-assets) (ok (total-assets-preview)))
(define-read-only (convert-to-shares (amount uint)) (ok (convert-to-shares-preview amount)))
(define-read-only (convert-to-assets (amount uint)) (ok (convert-to-assets-preview amount)))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L843-865)
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
```

**File:** mainnet/contracts/utility/v0-1-data.clar (L554-587)
```text
  ;; zSTX - STX price x liquidity index
  (if (is-eq aid zSTX)
      (let ((stx-price (default-to u0 (get-pyth-price PYTH-STX)))
            (lindex (get-vault-liquidity-index STX)))
        (mul-div-down stx-price lindex INDEX-PRECISION))
  ;; zsBTC - BTC price x liquidity index
  (if (is-eq aid zsBTC)
      (let ((btc-price (default-to u0 (get-pyth-price PYTH-BTC)))
            (lindex (get-vault-liquidity-index sBTC)))
        (mul-div-down btc-price lindex INDEX-PRECISION))
  ;; zstSTX - stSTX price x liquidity index (stSTX already includes ratio)
  (if (is-eq aid zstSTX)
      (let ((stx-price (default-to u0 (get-pyth-price PYTH-STX)))
            (ratio (unwrap-panic (get-ststx-ratio)))
            (ststx-price (mul-div-down stx-price ratio STSTX-RATIO-DECIMALS))
            (lindex (get-vault-liquidity-index stSTX)))
        (mul-div-down ststx-price lindex INDEX-PRECISION))
  ;; zUSDC - USDC price x liquidity index
  (if (is-eq aid zUSDC)
      (let ((usdc-price (default-to u0 (get-pyth-price PYTH-USDC)))
            (lindex (get-vault-liquidity-index USDC)))
        (mul-div-down usdc-price lindex INDEX-PRECISION))
  ;; zUSDH - USDH price x liquidity index
  (if (is-eq aid zUSDH)
      (let ((usdh-price (default-to u0 (get-dia-price DIA-USDH)))
            (lindex (get-vault-liquidity-index USDH)))
        (mul-div-down usdh-price lindex INDEX-PRECISION))
  ;; stSTXbtc - BTC price (liquid staked STX with BTC yield)
  (if (is-eq aid stSTXbtc) (default-to u0 (get-pyth-price PYTH-STX))
  ;; zstSTXbtc - stSTXbtc price x liquidity index
  (if (is-eq aid zstSTXbtc)
      (let ((btc-price (default-to u0 (get-pyth-price PYTH-STX)))
            (lindex (get-vault-liquidity-index stSTXbtc)))
        (mul-div-down btc-price lindex INDEX-PRECISION))
```
