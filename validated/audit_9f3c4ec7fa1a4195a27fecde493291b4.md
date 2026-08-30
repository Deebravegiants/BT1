### Title
Interest-rate manipulation via temporary large deposit lets borrowers avoid paying accrued interest - (File: `mainnet/contracts/vault/v0-vault-*.clar`)

### Summary
The Zest v2 vault contracts (`v0-vault-usdc.clar`, `v0-vault-usdh.clar`, `v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, and their `local-testing` counterparts) compute interest as a point-in-time rate applied over the *entire* elapsed time since the last accrual, rather than as a time-weighted integral. An unprivileged actor can temporarily inflate the vault's `assets` balance to depress `utilization`/`interest-rate` right before any transaction triggers `accrue`, causing the whole elapsed interval to be under-accrued, then withdraw the funds — an on-chain analog of the referenced Tracer "avoid paying insurance" bug (manipulate a rate right before it gets snapshotted over a time window).

### Finding Description
`interest-rate` is derived purely from the current `utilization`, which is itself computed from the *current* `assets`/`total-debt` snapshot: [1](#0-0) 

`next-index` (and `next-liquidity-index`) then applies that instantaneous `interest-rate` to the full `time-delta` elapsed since `last-update`: [2](#0-1) 

`accrue` uses this to bump `index`/`lindex` and mints the treasury's fee share, and only updates `last-update` if the index actually changed: [3](#0-2) 

Because `deposit` calls `accrue` *before* adding the new funds to `assets`, an attacker cannot manipulate the rate within a single deposit transaction: [4](#0-3) 

However, the manipulation is not confined to a single transaction. An attacker can:
1. Deposit a very large amount of the underlying asset (funded by an external flashloan or their own capital) into the vault, which correctly accrues past interest first, then adds the funds to `assets`, dramatically lowering `utilization` for as long as the deposit remains.
2. Wait while `assets` stays inflated. Any subsequent transaction that touches the vault (their own `redeem`, or any other user's `deposit`/`redeem`/`system-borrow`/`system-repay`) triggers `accrue`, which computes `interest-rate` from the now-suppressed `utilization` and multiplies it by the *entire* `time-delta` since the last update — including the period before the attacker's deposit landed, when true utilization (and the rate that should have applied) was much higher.
3. Withdraw (`redeem`) the deposited funds back out, restoring `utilization` to normal. Because `last-update` is now stamped at withdrawal time, the interest lost for the manipulated interval can never be recovered — it is permanently skipped, unlike Tracer's insurance rate which merely reset until the next window.

This breaks the identity that should hold across the vault:
`Δindex × principal_scaled (over Δt) == ∫ true_borrow_rate(u(t)) dt × principal_scaled`
Instead, the actual computation collapses to:
`Δindex ≈ rate(u(t_now)) × Δt`
which an attacker can force toward zero by controlling `u(t_now)` at the moment `accrue` executes, even though `u(t)` was high for most of `Δt`.

### Impact Explanation
This permanently reduces the interest that should accrue to lenders (and the `fee-reserve` skimmed to `.dao-treasury` via `calc-treasury-lp-preview`) for a real elapsed period, while borrowers' debt (`total-debt`/`index`) is never restated to the correct higher value. This is theft/permanent loss of unclaimed yield distributed via the share-price mechanism (`index`/`lindex`), matching the in-scope "interest created versus interest distributed" identity, since the interest that should have been created for lenders is permanently lost rather than merely delayed.

### Likelihood Explanation
The attack requires no privileged role — `deposit`, `redeem`, and the implicit `accrue` call inside them are fully unprivileged and callable by any principal (only `system-borrow`/`system-repay` require `check-caller-auth`, but they are not needed for this attack). The capital required (a large deposit) can be sourced from an external flashloan since the funds only need to sit in the vault across the exploited interval, not within a single atomic transaction, making an external flashloan viable for at least a portion of the timing (e.g., across two transactions in adjacent blocks if the lending protocol supports it, or simply large owned capital for longer windows). The main constraint is capital cost vs. the size of interest avoided, which scales with `total-debt` and the length of the manipulated window — larger, less-frequently-touched vaults are more attractive targets.

### Recommendation
Accrue interest using a time-weighted/integrated rate model (e.g., accrue in smaller increments whenever utilization changes materially, or record a rate checkpoint at the *start* of each interval rather than applying the rate observed at the end of the interval). Alternatively, snapshot `utilization` (and thus the rate) at the time funds are deposited/withdrawn by forcing an `accrue` call immediately before *and* after any balance-changing operation that could shift `utilization`, ensuring no interval is priced using a rate that only existed for a fraction of that interval.

### Proof of Concept
1. At time `T0`, `last-update = T0`, `utilization = U_high` (real state, no manipulation).
2. Time passes with no vault interaction until `T1` (large `time-delta = T1 - T0`).
3. Attacker deposits a large amount `D` at `T1`: `deposit` calls `accrue()` first — at this point `time-delta` may be small/zero if another tx already touched the vault, or it correctly accrues at `U_high` if this is genuinely the first touch; either way `assets` then increases by `D`, making `utilization ≈ U_low`.
4. No other transactions occur while `D` remains parked; `last-update` stays at `T1`.
5. Time passes to `T2`. Attacker calls `redeem` to withdraw `D` (or any other user triggers `accrue`): `accrue()` computes `interest-rate` from `U_low` (line [5](#0-4)  ) and applies it over `time-delta = T2 - T1` (line [6](#0-5) ), producing a much smaller `index` increase than the true utilization `U_high'` (which would have applied had `D` not been parked) warrants for that interval.
6. Attacker's `redeem` completes, restoring `assets` to pre-deposit levels and resetting `last-update = T2`; the interest gap for `[T1, T2]` is permanently unrecoverable — borrowers effectively paid reduced interest and lenders/treasury permanently lost the corresponding yield.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L366-402)
```text
(define-private (utilization)
  (calc-utilization (get-available-assets) (total-debt)))

(define-private (interest-rate)
  (let ((points-data (var-get points-ir))
        (uword (get util points-data))
        (rword (get rate points-data))
        (utils (unpack-u16 uword))
        (rates (unpack-u16 rword)))
    (interpolate-rate (utilization) utils rates)))

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

**File:** local-testing/contracts/vault/vault-sbtc.clar (L765-797)
```text
(define-public (deposit (amount uint) (min-out uint) (recipient principal))
    (let (
      (states (var-get pause-states))
      (u (try! (accrue)))
      (account contract-caller)
      (CAP-SUPPLY (var-get cap-supply))
      (current-assets (var-get assets))
      (inkind (convert-to-shares-preview amount)))

    (asserts! (not (get deposit states)) ERR-PAUSED)
    (asserts! (var-get initialized) ERR-INIT)
    (asserts! (not (var-get in-flashloan)) ERR-REENTRANCY)
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)
    (asserts! (>= inkind min-out) ERR-SLIPPAGE)
    (asserts! (<= (+ current-assets amount) CAP-SUPPLY) ERR-SUPPLY-CAP-EXCEEDED)

    (try! (receive-underlying amount account))
    (try! (ft-mint? zft inkind recipient))
    (var-set assets (+ current-assets amount))

    (print {
      action: "deposit",
      caller: contract-caller,
      data: {
        depositor: account,
        recipient: recipient,
        amount: amount,
        shares-minted: inkind,
        assets: (+ current-assets amount)
      }
    })

    (ok inkind)))
```
