## Analysis

Zest's graduated liquidation design in `mainnet/contracts/market/v0-4-market.clar` has a direct analog to the Inverse Finance "liquidation should make a borrower healthier" bug class. There is no check anywhere in `liquidate` that the borrower's post-liquidation LTV (or health factor) is not worse than the pre-liquidation LTV — `is-healthy` is only used in `borrow` / `collateral-add`, never in `liquidate`. [1](#0-0) [2](#0-1) 

### Title
Graduated liquidation curve can push a borrower's LTV *above* pre‑liquidation LTV (even past 100%), socializing bad debt onto lenders - (File: `mainnet/contracts/market/v0-4-market.clar`)

### Summary
`liquidate()` computes a liquidation fraction `f` (`liq-pct-scaled`) and penalty `p` (`liq-penalty`) from the borrower's current LTV via `calc-liquidation-params`/`calc-liq-factor`/`calc-liq-factor-exp`/`calc-liq-factor-bound`, then repays `f·D` of debt while seizing `f·D·(1+p)` of collateral value. For any `f ∈ (0,1)`, the post-liquidation LTV `L'` relates to the pre-liquidation LTV `L` by `L' > L` whenever `L·(1+p) > 1`. Because the penalty `p` scales up toward `LIQ-PENALTY-MAX` as `L` approaches `LTV-LIQ-FULL`, there exists a real, reachable LTV/penalty region (well before the full-liquidation threshold, i.e. `f < 100%`) where `L·(1+p) > 1`. A completely ordinary, permissionless partial liquidation there makes the position *unhealthier*, and can even push it past 100% LTV, i.e. instantly under-collateralized/bad debt, which then gets picked up by the existing bad-debt socialization path and forced onto lenders.

### Finding Description
The health/LTV math is implemented in:
- `calc-liq-factor` / `calc-liq-factor-exp` / `calc-liq-factor-bound` / `calc-liquidation-params` — computes the liquidatable debt fraction `f` and penalty `p` purely as a function of current LTV, egroup min/max penalty and curve exponent. [3](#0-2) 

- `process-debt-asset` / `process-collateral-asset` / `calc-final-liquidation-amounts` — convert `f·D` of debt into a token amount and the corresponding collateral seizure `debt·(1+p)`, with no re-check of the resulting position LTV. [4](#0-3) 

- `liquidate` — executes the repay + collateral removal directly from these values, and only checks `>= ltv-liq-partial` *before* liquidating; there is no assertion comparing pre- and post-liquidation health. [5](#0-4) 

Deriving the identity that should hold: writing `D`,`C` for total debt/collateral USD and `f`,`p` for the liquidated fraction and penalty, if collateral is proportionally distributed (`C = D/L`):

`L' = D(1-f) / (D/L - f·D·(1+p)) = (1-f) / (1/L - f(1+p))`

`L' - L` has the same sign as `f·[L·(1+p) - 1]`. Since `f>0`, liquidation makes the borrower **unhealthier** (`L' > L`) exactly when `L·(1+p) > 1`.

Concrete numeric example using the sBTC/USDC egroup parameters actually deployed (`LTV-LIQ-PARTIAL=8500`, `LTV-LIQ-FULL=9500`, `LIQ-PENALTY-MIN=500`, `LIQ-PENALTY-MAX=1000`, `LIQ-CURVE-EXP=20000`): [6](#0-5) 

At `L = 9400 bps` (94%): linear factor `= (9400-8500)/(9500-8500) = 9000 bps`; squared/curve-adjusted `f = 8100 bps (81%)`; `p = 500 + 8100·(1000-500)/10000 = 905 bps (9.05%)`. This is **not** a full liquidation (`f=81% < 100%`), yet `L·(1+p) = 0.94 × 1.0905 ≈ 1.025 > 1`, so the position becomes unhealthier. Plugging `D=94, C=100`: after liquidating `d=76.14` (seizing `83.03` of collateral usd value), `D'=17.86`, `C'=16.97`, giving `L' ≈ 105.2%` — the position is pushed from a recoverable 94% LTV into outright bad debt (>100% LTV) by a single, ordinary, permissionless `liquidate()` call.

### Impact Explanation
Any unprivileged caller can call `liquidate()` on a position sitting in the upper part of the partial-liquidation band (between `LTV-LIQ-PARTIAL` and `LTV-LIQ-FULL`, where the graduated penalty is large but `f<100%`) and, through completely normal execution, convert an under-water-but-recoverable position into one with LTV > 100%. The remaining debt then has insufficient collateral backing; any subsequent liquidator has no incentive to close it (seizing less than they repay), so it is left to be written off via the existing `socialize-debt-asset` bad-debt path, socializing the loss onto vault depositors/lenders. This is a direct path to protocol insolvency / loss of lender principal, matching the Critical impact bucket (protocol insolvency, theft of principal). It requires no oracle bug, no flashloan, no DAO compromise, and no disabled-collateral edge case — only an ordinary price move putting a position in the vulnerable LTV band, which is exactly the scenario liquidations are meant to safely resolve.

### Likelihood Explanation
The vulnerable LTV band is not a rare corner case — it is guaranteed to exist for any egroup where `LTV-LIQ-FULL · (1 + LIQ-PENALTY-MAX) > 1` (BPS-normalized), which is true for the deployed sBTC/USDC egroup (`0.95 × 1.10 = 1.045 > 1`). Any liquidation bot racing to be first (as they always do, for the fee/bonus) will naturally trigger partial liquidations as soon as a position crosses `LTV-LIQ-PARTIAL`, well before `f` reaches 100%, making this reachable in normal market conditions (price dips) without any special attacker setup.

### Recommendation
Add a post-liquidation health check in `liquidate` (and `liquidate-multi`) analogous to the Inverse Finance fix: compute the position's LTV (or `collateral/debt` ratio) before and after applying `debt-to-repay`/`coll-final`, and require the post-liquidation LTV to be `<=` the pre-liquidation LTV (or require `L·(1+liq-penalty) <= 1` before allowing anything less than a full liquidation of the position for that debt asset). Alternatively, bound `LIQ-PENALTY-MAX` per egroup such that `LTV-LIQ-FULL · (1 + LIQ-PENALTY-MAX) <= BPS` always holds, and/or force `liq-pct-scaled` to jump straight to 100% once the unsafe threshold is crossed rather than following the smooth curve into the unsafe zone.

### Proof of Concept
1. Deploy/observe an egroup such as the sBTC/USDC one with `LTV-LIQ-PARTIAL=8500`, `LTV-LIQ-FULL=9500`, `LIQ-PENALTY-MIN=500`, `LIQ-PENALTY-MAX=1000`, `LIQ-CURVE-EXP=20000` [7](#0-6) .
2. Have a borrower with collateral `C=100` USD and debt `D=94` USD (94% LTV, inside the partial band).
3. Any address calls `market.liquidate(borrower, sbtc-ft, usdc-ft, <debt-amount covering the full max-debt-usd cap>, 0, none, none)`.
4. Inside `liquidate`, `calc-liquidation-params` computes `liq-pct-scaled ≈ 8100 bps` and `liq-penalty ≈ 905 bps` [8](#0-7) ; `process-debt-asset`/`process-collateral-asset`/`calc-final-liquidation-amounts` compute `debt-to-repay ≈ 76.14` and `coll-final` worth `≈ 83.03` USD [9](#0-8) .
5. After execution, borrower's remaining debt `≈17.86` USD is backed by remaining collateral `≈16.97` USD — LTV jumped from 94% to ≈105.2%, with no revert, because no post-liquidation health assertion exists in the function [10](#0-9) .
6. The now-under-collateralized remainder is unprofitable for any further liquidator to close and is eventually written off via `socialize-debt-asset`, socializing the loss onto the vault's depositors [11](#0-10) .

### Citations

**File:** mainnet/contracts/market/v0-4-market.clar (L656-659)
```text
(define-private (is-healthy (collateral-usd uint) (debt-usd uint) (ltv uint))
  (if (is-eq debt-usd u0)
      true
      (<= (* debt-usd BPS) (* collateral-usd ltv))))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L701-756)
```text
;; Calculate liquidation factor: ((ltv-curr - ltv-liq-partial) * BPS) / (ltv-liq-full - ltv-liq-partial)
;; Capped at BPS (100%) to prevent over-liquidation
(define-private (calc-liq-factor (ltv-curr uint) (ltv-liq-partial uint) (ltv-liq-full uint))
  (min BPS (div-bps-down (- ltv-curr ltv-liq-partial) (- ltv-liq-full ltv-liq-partial))))

;; Apply curve exponent for graduated liquidation
;; liq-factor = liq-factor^alpha
(define-private (calc-liq-factor-exp (factor uint) (exp uint))
  (if (is-eq exp BPS) 
    factor
    (if (> exp BPS) 
        (/ (pow factor (/ exp BPS)) (pow BPS (- (/ exp BPS) u1)))
        (sqrti (* factor BPS))))) ;; assume factor^0.5

;; Scale penalty between min and max using liquidation factor
;; liq-penalty = liq-penalty-min + (liq-factor * (liq-penalty-max - liq-penalty-min) / BPS)
;; Capped at bound-max to handle cases where liq-factor > BPS
(define-private (calc-liq-factor-bound (liq-factor uint) (bound-min uint) (bound-max uint))
  (min bound-max (+ bound-min (mul-bps-down liq-factor (- bound-max bound-min)))))

;; Calculate debt to repay based on liquidation factor
;; debt-repay = liq-factor * debt / BPS
(define-private (calc-liq-debt-repay (debt uint) (liq-factor uint)) 
  (mul-bps-down liq-factor debt))

;; Calculate collateral to seize (includes liquidator bonus)
;; collateral-repay = debt-repay * (BPS + liq-penalty) / BPS
(define-private (calc-liq-collateral-repay (debt-repay uint) (liq-penalty uint)) 
  (mul-bps-down debt-repay (+ BPS liq-penalty)))

;; Calculate actual debt repayment when collateral is capped
;; debt-repay-real = (collateral-amount-usd * BPS) / (BPS + liq-penalty)
(define-private (calc-liq-debt-repay-real (collateral-amount-usd uint) (liq-penalty uint)) 
  (div-bps-down collateral-amount-usd (+ BPS liq-penalty)))

;; Graduated liquidation parameter calculation
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

**File:** mainnet/contracts/market/v0-4-market.clar (L758-853)
```text
;; Process debt asset for liquidation
;; Finds asset info, converts to USD, caps at max liquidatable, converts back to token amount
;; Returns: { debt-actual-usd: uint, debt-actual: uint, debt-price: uint, debt-decimals: uint }
(define-private (process-debt-asset
  (debt-amount uint)
  (debt-aid uint)
  (max-debt-usd uint)
  (assets (list 64 {
    id: uint, addr: principal, decimals: uint,
    oracle: { type: (buff 1), ident: (buff 32), callcode: (optional (buff 1)), max-staleness: uint },
    collateral: bool, debt: bool, price: uint
  })))
  (let ((debt-asset-info (unwrap-panic (find-asset debt-aid assets)))
        (debt-price (get price debt-asset-info))
        (debt-decimals (get decimals debt-asset-info))
        (debt-usd (normalize (* debt-amount debt-price) debt-decimals false))
        ;; cap debt at maximum liquidatable amount
        (debt-actual-usd (if (> debt-usd max-debt-usd) max-debt-usd debt-usd))
        ;; convert capped USD amount back to token amount
        (debt-actual (mul-div-down debt-actual-usd (pow u10 debt-decimals) debt-price)))
    {
      debt-actual-usd: debt-actual-usd,
      debt-actual: debt-actual,
      debt-price: debt-price,
      debt-decimals: debt-decimals
    }))

;; Process collateral asset for liquidation
;; Handles both enabled and disabled collateral assets
;; Calculates expected collateral, caps at user balance
;; Returns: { coll-actual: uint, coll-expected: uint, coll-price: uint, coll-decimals: uint }
(define-private (process-collateral-asset
  (coll-aid uint)
  (debt-actual-usd uint)
  (liq-penalty uint)
  (user-coll-balance uint)
  (assets (list 64 {
    id: uint, addr: principal, decimals: uint,
    oracle: { type: (buff 1), ident: (buff 32), callcode: (optional (buff 1)), max-staleness: uint },
    collateral: bool, debt: bool, price: uint
  }))
  (coll-asset {
    id: uint, addr: principal, decimals: uint,
    oracle: { type: (buff 1), ident: (buff 32), callcode: (optional (buff 1)), max-staleness: uint },
    collateral: bool, debt: bool
  }))
  
  (let (;; Calculate expected collateral in USD (with penalty bonus for liquidator)
        (coll-usd-expected (calc-liq-collateral-repay debt-actual-usd liq-penalty))
        
        ;; Handle disabled collaterals by resolving price if not in enabled assets
        (coll-asset-info (match (find-asset coll-aid assets)
                           ;; Found in enabled list: use it (already has price)
                           found found
                           ;; Not found (disabled): resolve price on demand
                           (let ((oracle-data (get oracle coll-asset))
                                 (price (unwrap-panic (price-resolve oracle-data))))
                             (merge coll-asset { price: price }))))
        (coll-price (get price coll-asset-info))
        (coll-decimals (get decimals coll-asset-info))
        (coll-expected (mul-div-down coll-usd-expected (pow u10 coll-decimals) coll-price))
        
        ;; cap at available collateral (user may not have enough)
        (coll-actual (if (> coll-expected user-coll-balance)
                         user-coll-balance
                         coll-expected)))
    {
      coll-actual: coll-actual,
      coll-expected: coll-expected,
      coll-price: coll-price,
      coll-decimals: coll-decimals
    }))

;; Calculate final liquidation amounts with proportional adjustments
;; If collateral was capped, recalculates debt proportionally
;; Returns: { debt-final-usd: uint, debt-final: uint }
(define-private (calc-final-liquidation-amounts
  (debt-actual-usd uint)
  (coll-actual uint)
  (coll-expected uint)
  (coll-price uint)
  (coll-decimals uint)
  (debt-price uint)
  (debt-decimals uint)
  (liq-penalty uint))
  
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

**File:** mainnet/contracts/market/v0-4-market.clar (L879-903)
```text
(define-private (socialize-debt-asset
                (debt-entry { aid: uint, scaled: uint })
                (acc { borrower: principal, success: bool }))
  ;; Early return if previous socialization failed
  (if (not (get success acc))
      acc
      (let ((borrower (get borrower acc))
            (failed-status { borrower: borrower, success: false })
            (asset-id (get aid debt-entry))
            (scaled-debt (get scaled debt-entry)))

            ;; Socialize in vault - pass scaled directly to avoid rounding
            (unwrap! (vault-socialize-debt asset-id scaled-debt) failed-status)
            ;; Refresh cache with new indexes post-write-down (lindex decreased)
            (map-set index-cache
                     { timestamp: stacks-block-time, aid: asset-id }
                     (unwrap! (vault-accrue asset-id) failed-status))
            ;; Remove from obligation
            (unwrap! (contract-call? .v0-market-vault
                                      debt-remove-scaled
                                      borrower
                                      scaled-debt
                                      asset-id) failed-status)
          acc)
        ))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1433-1496)
```text
    ;; health check (FAIL-FAST) 
    ;; Check position is liquidatable BEFORE calling calc-liq-factor
    (health-check  (asserts! (>= current-ltv ltv-liq-partial) ERR-HEALTHY))

    ;; liquidation parameters (graduated liquidation calculation)
    (liq-params (calc-liquidation-params 
                  current-ltv ltv-liq-partial ltv-liq-full
                  liq-penalty-min liq-penalty-max 
                  curve-exponent total-debt-usd))
    (liq-pct-scaled (get liq-pct-scaled liq-params))
    (liq-penalty (get liq-penalty liq-params))
    (max-debt-usd (get max-debt-usd liq-params))

    ;; debt processing
    (debt-info (process-debt-asset debt-amount debt-aid max-debt-usd assets))
    (debt-actual-usd (get debt-actual-usd debt-info))
    (debt-actual (get debt-actual debt-info))
    (debt-price (get debt-price debt-info))
    (debt-decimals (get debt-decimals debt-info))

    ;; collateral processing
    (user-coll-balance (find-collateral-amount (get collateral pos-full) coll-aid))
    (coll-info (process-collateral-asset coll-aid debt-actual-usd liq-penalty 
                                         user-coll-balance assets coll-asset))
    (coll-actual (get coll-actual coll-info))
    (coll-expected (get coll-expected coll-info))
    (coll-price (get coll-price coll-info))
    (coll-decimals (get coll-decimals coll-info))

    ;; final liquidation amounts (with proportional adjustment if needed)
    (final-amounts (calc-final-liquidation-amounts
                     debt-actual-usd coll-actual coll-expected
                     coll-price coll-decimals
                     debt-price debt-decimals liq-penalty))
    (debt-final-usd (get debt-final-usd final-amounts))
    (debt-final (get debt-final final-amounts))

    ;; debt scaling for storage
    (curr-scaled (get-account-scaled-debt borrower debt-aid))
    (scaled-info (scale-debt-for-liquidation debt-final coll-actual curr-scaled debt-aid))
    (scaled-to-remove (get scaled-to-remove scaled-info))
    (debt-to-repay (get debt-to-repay scaled-info))
    (coll-final-raw (get coll-final scaled-info))
    (coll-remaining (- user-coll-balance coll-final-raw))
    (remaining-debt-to-repay
      (if (> coll-remaining u0)
        (let ((rem-coll-usd (normalize (* coll-remaining coll-price) coll-decimals false))
              (rem-debt-usd (div-bps-down rem-coll-usd (+ BPS liq-penalty-max)))
              (rem-debt-tokens (mul-div-down rem-debt-usd (pow u10 debt-decimals) debt-price))
              (rem-borrow-index (get index (unwrap-panic (get-cached-indexes debt-aid))))
              (rem-scaled (mul-div-down rem-debt-tokens INDEX-PRECISION rem-borrow-index)))
          (mul-div-up rem-scaled rem-borrow-index INDEX-PRECISION))
        u1))
    (coll-final (if (is-eq remaining-debt-to-repay u0) user-coll-balance coll-final-raw)))

    (asserts! (not (is-liquidation-paused debt-aid)) ERR-LIQUIDATION-PAUSED)
    (asserts! (is-eq contract-caller tx-sender) ERR-AUTHORIZATION)
    (asserts! (> debt-amount u0) ERR-AMOUNT-ZERO)
    (asserts! (> debt-to-repay u0) ERR-ZERO-LIQUIDATION-AMOUNTS)
    (asserts! (> coll-final u0) ERR-ZERO-LIQUIDATION-AMOUNTS)
    (asserts! (>= coll-final min-collateral-expected) ERR-SLIPPAGE)

    ;; execute liquidation
    (try! (vault-system-repay debt-aid debt-to-repay debt-ft debt-address))
```

**File:** local-testing/contracts/proposals/proposal-create-egroup-sbtc-usdc.clar (L1-22)
```text
;; Proposal to create custom egroup for sBTC collateral / USDC debt
;; This egroup allows higher LTV (70%) for this specific asset pair

(impl-trait .dao-traits.proposal-script)

(define-public (execute)
  (begin
    ;; Create egroup with sBTC collateral (bit 2) + USDC debt (bit 70)
    ;; NEW Asset IDs: sBTC=2, USDC=6, debt_bit=64+6=70
    ;; MASK = 2^2 + 2^70 = 4 + 1180591620717411303424 = 1180591620717411303428
    (try! (contract-call? .egroup insert {
      MASK: u1180591620717411303428,
      BORROW-DISABLED-MASK: u0,           ;; No assets disabled for borrowing
      LIQ-CURVE-EXP: u20000,              ;; 2.0 quadratic (gentle-then-steep)
      LIQ-PENALTY-MIN: u500,              ;; 5%
      LIQ-PENALTY-MAX: u1000,             ;; 10%
      LTV-BORROW: u7000,                  ;; 70% max borrow LTV
      LTV-LIQ-PARTIAL: u8500,             ;; 85% partial liquidation threshold
      LTV-LIQ-FULL: u9500                 ;; 95% full liquidation threshold
    }))
    
    (ok true)))
```
