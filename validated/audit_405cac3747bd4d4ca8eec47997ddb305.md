### Title
Repeated public `accrue()` calls split interest into many small deltas, causing floor-rounding of `reserve-inc` to permanently drop treasury yield - ([File: mainnet/contracts/vault/v0-vault-ststx.clar])

### Summary
`accrue` is a public, unauthenticated function that recomputes the borrow index and mints treasury `zft` shares proportional to `reserve-inc = mul-div-down(debt-delta, fee-reserve, BPS)` [1](#0-0) . Because floor division is subadditive, splitting one interest-accrual period into many tiny sub-periods (each triggering its own `accrue` call) strictly reduces (never increases) the total reserve fee minted to `.dao-treasury` compared to letting the same total debt delta accrue in one call. An attacker with no capital can call the public `accrue()` function every block indefinitely to depress the treasury's cut, while all the underlying interest still accumulates fully into `total-assets` for existing `zft` holders.

### Finding Description
The relevant identity is:

`Σ_{i=1..N} reserve-inc_i  ==  mul-div-down( total-debt_N - total-debt_0 , fee-reserve, BPS )`

where `total-debt_i = mul-div-down(principal-scaled, index_i, INDEX-PRECISION)` and `reserve-inc_i = mul-div-down(debt-delta_i, fee-reserve, BPS)` is computed fresh inside each `accrue` call [2](#0-1) .

Because `old-debt`/`new-debt` for consecutive calls telescope exactly (`old-debt_i == new-debt_{i-1}`, both computed from the *same* `scaled-principal` with only `idx` advancing), the sum of `debt-delta_i` across N calls equals the single-shot `total-debt_N - total-debt_0` exactly — there is no drift in total debt/interest accounted to the vault. The divergence appears one step later: `mul-div-down` applied to `fee-reserve/BPS` **per small `debt-delta_i`** is only guaranteed subadditive, i.e.

`Σ floor(debt-delta_i * fee-reserve / BPS) <= floor(Σ debt-delta_i * fee-reserve / BPS)`

with strict inequality whenever any individual `debt-delta_i * fee-reserve mod BPS != 0`. Each `accrue` call that produces a non-zero-but-sub-BPS-fraction `debt-delta` rounds `reserve-inc` down to a value strictly less than its "fair share" of the eventual total, and this lost fraction is never later recovered because subsequent calls compute their own delta and floor independently.

`accrue` has no access control (`check-caller-auth` is not called on it) and is reachable directly by any unprivileged principal, or indirectly via `deposit`/`redeem`/`system-borrow`/`system-repay`/`flashloan`, all of which call `(try! (accrue))` unconditionally at the top [3](#0-2) [4](#0-3) . `next-index`'s borrow multiplier uses `mul-div-up`, so any non-zero `time-delta` with `rate > 0` strictly increases `index` by at least 1 unit each call (guaranteeing a fresh non-zero `debt-delta` whenever `principal-scaled` is large enough) [5](#0-4) [6](#0-5) . No `min-out`/slippage/pause/cap check prevents calling `accrue` on its own or via a `deposit` of dust amounts every block; the only self-mitigation is that calling twice in the same block is a no-op because `time-delta == 0` forces `multiplier = INDEX-PRECISION` [7](#0-6) , so the attacker must call at most once per block, which is trivially satisfiable.

### Impact Explanation
Per accrual event the loss is bounded by less than 1 base unit of the underlying token's `reserve-inc` (a fraction less than 1 that is discarded by `mul-div-down`), and it compounds an additional floor at the `treasury-lp = mul-div-down(reserve-inc, total-supply, total-assets-preview - reserve-inc)` step [8](#0-7) . This loss is fully repeatable (once per block, indefinitely, requiring `principal-scaled > 0`, i.e. active borrowing) and is monotonic — grouping accrual into more calls can never raise `Σ reserve-inc_i`, only lower or equal it. The discarded fee never accrues anywhere; it simply is not minted to `.dao-treasury`, so it stays folded into `total-assets` for existing `zft` holders, i.e. it is redistributed from the treasury to current suppliers, at zero cost and zero capital to the caller. This matches the "High — theft of unclaimed yield" category since it is the treasury's protocol fee (unclaimed yield) that is permanently diverted/lost rather than principal.

### Likelihood Explanation
The only precondition is an outstanding scaled-principal debt (`principal-scaled > 0`), which exists under normal vault operation whenever any borrow is active. The attacker needs no capital and no special permissions — `accrue` is a bare public function with no `check-caller-auth`, and its guards (`pause-states`, `time-delta == 0` short-circuit) do not prevent repeated once-per-block calls. This is trivially automatable (a bot calling `accrue()` every block) and costs only ordinary transaction fees.

### Recommendation
Track fractional remainder ("dust") of the fee computation across calls (e.g., accumulate `debt-delta * fee-reserve mod BPS` in a persistent variable and carry it into the next `accrue` computation), or compute `reserve-inc` using `mul-div-up` instead of `mul-div-down` so the treasury is never shorted, with any resulting surplus reconciled against supplier interest. Alternatively, rate-limit `accrue`'s state effects to a minimum time interval so an attacker cannot force arbitrarily fine-grained splitting.

### Proof of Concept
Clarinet simnet test plan:
1. Deploy vault, initialize, set `fee-reserve` to a non-trivial value (e.g. u1000), set interest-rate points so `interest-rate()` is non-zero at some utilization.
2. Have a borrower call `system-borrow` to create `principal-scaled > 0`.
3. **Scenario A (single accrual):** advance the chain by `N` seconds/blocks in one jump, then call `accrue()` once. Record `zft` balance of `.dao-treasury` (call it `treasury_A`).
4. **Scenario B (split accrual):** reset state (fresh deployment with identical initial parameters/borrow), then loop `N` times: advance 1 block, call `accrue()` (or `deposit` with a dust amount). Record final `.dao-treasury` `zft` balance (`treasury_B`).
5. Assert `treasury_B < treasury_A`, demonstrating the treasury receives strictly less in the split-accrual scenario despite `total-debt_N` and `index_N` being identical in both scenarios, and quantify `treasury_A - treasury_B` as the value siphoned from treasury to remaining `zft` holders.

### Citations

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L170-178)
```text
(define-private (calc-multiplier-delta (rate uint) (time-delta uint) (round-up bool))
  (+ INDEX-PRECISION
    (if round-up
      (mul-div-up rate
                  (* time-delta INDEX-PRECISION)
                  SECONDS-PER-YEAR-BPS)
      (mul-div-down rate
                  (* time-delta INDEX-PRECISION)
                  SECONDS-PER-YEAR-BPS))))
```

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L379-390)
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

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L763-767)
```text
(define-public (deposit (amount uint) (min-out uint) (recipient principal))
    (let (
      (states (var-get pause-states))
      (u (try! (accrue)))
      (account contract-caller)
```

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L797-801)
```text
(define-public (redeem (amount uint) (min-out uint) (recipient principal))
  (let (
    (states (var-get pause-states))
    (u (try! (accrue)))
    (account contract-caller)
```

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L835-863)
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
