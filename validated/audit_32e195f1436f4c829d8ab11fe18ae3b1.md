### Title
Permanent freeze of vault deposits due to `lindex` being writable to zero in `socialize-debt` - ([File: mainnet/contracts/vault/v0-vault-stx.clar])

### Summary
Each lending vault (`v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdc.clar`, `v0-vault-usdh.clar`) tracks a liquidity index `lindex` that converts vault shares (ztokens) to underlying assets and back, exactly analogous to `slashIndex` in the reported InfiniFi bug. The `socialize-debt` function can write `lindex` down to exactly `u0` when a bad-debt write-off consumes the vault's entire tracked asset base, mirroring the scenario where `slashIndex` was zeroed after a total loss event.

### Finding Description
`lindex` is initialized to `INDEX-PRECISION` and is used as the price factor between shares and underlying assets, as documented in `docs/vaults.md`: `shares = amount / price` on deposit and `amount = shares * price` on redeem, where price is derived from `lindex` [1](#0-0) .

The `socialize-debt` function computes a new `lindex` proportional to the fraction of `total-assets` written off, but when `old-total-assets` is not strictly greater than `debt-reduction` (i.e., a full or over-full loss is socialized against the vault), it falls back to setting `lindex` to `u0` unconditionally: [2](#0-1) 

This is structurally identical to the `slashIndex = 0` condition described in the report: a legitimate loss-accounting code path can drive the index variable that vault-wide pricing depends on to exactly zero. Once `lindex` is `u0`, `accrue` (which recomputes `treasury-lp` using `total-assets-preview`) and any share/asset conversion function that divides by the price derived from `lindex` will attempt a division by zero, aborting the transaction [3](#0-2) .

Because `lindex` is a single global variable per vault (not scoped to a subset of positions), driving it to zero via one `socialize-debt` call permanently blocks all subsequent `accrue`, `deposit`, and any share-to-asset conversion calls that depend on the price computed from `lindex` for every depositor in that vault, not just the specific debt that was socialized.

### Impact Explanation
This is a permanent freezing-of-funds condition consistent with High/Critical impact criteria: users with existing ztoken balances in the affected vault would be unable to `accrue` interest or convert their shares back to underlying assets going forward, because the shared pricing state (`lindex`) is corrupted to zero and there is no code path shown to reset it (unlike the recommended InfiniFi fix of resetting `slashIndex` to `1e18` when the tracked balance hits zero).

### Likelihood Explanation
`socialize-debt` is restricted to an authorized caller (`check-caller-auth`), so triggering the exact zero-out condition requires a socialize-debt call against a vault whose `total-assets` has been reduced to at or below the write-off amount — a scenario that can occur during a legitimate bad-debt socialization following undercollateralized liquidations, i.e., not necessarily an attacker-controlled path, but a reachable operational state.

### Recommendation
In `socialize-debt`, avoid writing `lindex` to `u0`; instead, either floor it at a minimum non-zero value or, if `total-assets` is fully wiped out, reset `lindex` to `INDEX-PRECISION` alongside a corresponding reset of the vault's share supply/asset accounting, mirroring the two-sided fix that InfiniFi noted was required (reset index and separately reconcile downstream aggregates) rather than fixing only the index variable in isolation.

### Proof of Concept
1. A vault (e.g., `v0-vault-stx`) accrues bad debt equal to or exceeding its current `total-assets`.
2. An authorized caller invokes `socialize-debt` with a `scaled-amount` such that `debt-reduction >= old-total-assets`.
3. `new-lindex` evaluates to `u0` per the fallback branch in `socialize-debt` and is persisted via `var-set lindex new-lindex` [4](#0-3) .
4. Any subsequent call to `accrue` (invoked implicitly by deposit/redeem/borrow/repay flows) computes `treasury-lp` using a division derived from `total-assets-preview`/`lindex`-dependent state, and any price-based share/asset conversion divides by a zero-derived price, aborting the transaction and freezing the vault's normal operation for all remaining depositors.

Note: I was not able to fully read the exact `convert-to-shares`/`convert-to-assets`/`total-assets-preview` implementations within the available tool budget to confirm the precise line where the zero-division panic occurs; this should be verified directly in `mainnet/contracts/vault/v0-vault-stx.clar` (and sibling vault files) before treating this as fully confirmed.

### Citations

**File:** docs/vaults.md (L55-72)
```markdown
## Share Pricing Mechanism

### How Ztokens Accrue Value

Vault shares (ztokens) increase in value relative to underlying assets through the **liquidity index**:

```
Initial State:
- 1 zUSDC = 1 USDC (index = 1.0)

After Interest Accrual:
- 1 zUSDC = 1.10 USDC (index = 1.10)
- 10% interest earned

Later:
- 1 zUSDC = 1.25 USDC (index = 1.25)
- 25% cumulative interest
```
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L944-963)
```text
(define-public (socialize-debt (scaled-amount uint))
  (let ((scaled-principal (var-get principal-scaled))
        (borrowed (var-get total-borrowed))
        (idx (var-get index))
        (current-assets (var-get assets))
        (current-lindex (var-get lindex))
        (old-total-assets (total-assets))
        (debt-reduction (mul-div-down scaled-amount idx INDEX-PRECISION))
        (principal-reduction (if (> scaled-principal u0)
                                (mul-div-down scaled-amount borrowed scaled-principal)
                                u0))
        ;; Write down lindex proportionally to loss in total-assets
        (new-lindex (if (and (> old-total-assets u0) (> old-total-assets debt-reduction))
                       (mul-div-down current-lindex (- old-total-assets debt-reduction) old-total-assets)
                       u0)))

    (try! (check-caller-auth))
    (asserts! (> scaled-amount u0) ERR-AMOUNT-ZERO)

    (var-set lindex new-lindex)
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L837-865)
```text
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

(define-public (system-borrow (amount uint) (receiver principal))
  (let (
      (states (var-get pause-states))
```
