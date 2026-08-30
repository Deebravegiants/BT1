## Title
Vault `total-assets` optimistically counts unpaid accrued borrower interest as real backing, inflating share redemption value before bad debt is socialized - (File: `mainnet/contracts/vault/v0-vault-stx.clar` and equivalent vaults `v0-vault-usdc.clar`, `v0-vault-usdh.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`)

### Summary
The vault's `total-assets` function adds the full outstanding accrued interest (`debt - borrowed`) to the real on-hand asset balance (`assets`), treating it as if it were already collected principal/interest backing the vault, exactly like the SherX report's optimistic `calcUnderlying` assumption that outstanding premiums will be paid. `total-assets` directly feeds `convert-to-assets`/`convert-to-shares`, which determine how much real underlying a share redeems for.

### Finding Description
`total-assets` is defined as: [1](#0-0) 

`current-assets` (`var-get assets`) only increases when real underlying is actually received, e.g. in `system-repay`: [2](#0-1) 

`debt` (`total-debt`) is a purely accrued, index-based number that grows automatically with time via `next-index`/`accrue`, independent of whether the borrower actually has the ability to repay: [3](#0-2) 

`total-assets` is consumed by the ERC4626-style conversion helpers that price shares for deposits/withdrawals: [4](#0-3) 

The protocol does have a mechanism to write off bad/uncollectible debt, `socialize-debt`, which reduces `principal-scaled`/`total-borrowed` and marks down the liquidity index when debt cannot be repaid: [5](#0-4) 

This mirrors the SherX pattern exactly: `total-assets` (analogous to SherX's `calcUnderlying`) optimistically assumes all accrued debt is collectible and already backs the vault, while the "correction" (`socialize-debt`, analogous to `payOffDebtAll`) is a separate, non-atomic call that must be triggered afterward. Between the point a borrower actually becomes unable to repay (default/insolvency) and the point `socialize-debt` is invoked to write down the bad debt, `total-assets` still includes that uncollectible interest/principal as if it were real backing. Any `withdraw`/`redeem` executed in that window uses `convert-to-assets` computed off the inflated `total-assets`, so the withdrawing user is paid out of the vault's actual `current-assets` (real underlying token balance) at a rate that assumes the bad debt will still be repaid in full.

The value identity broken is:
```
total-assets (used for share pricing) = current-assets (real backing) + accrued-interest-and-principal-not-actually-collectible
```
which should instead be:
```
total-assets = current-assets + recoverable-accrued-interest-and-principal-only
```

### Impact Explanation
Because share redemption value is derived directly from the inflated `total-assets`, a user redeeming during the window before `socialize-debt` is executed extracts more real underlying tokens per share than the vault can actually back, at the direct expense of remaining depositors, who are left holding shares against assets that no longer exist (temporary/permanent freezing of funds for remaining depositors, and effectively theft of principal transferred from later withdrawers to earlier ones). This matches the required impact categories: protocol insolvency and freezing of funds for the LPs who remain in the vault once the bad debt is finally socialized.

### Likelihood Explanation
This requires an actual borrower default/insolvency event (a `borrow` position becoming unrecoverable) combined with a delay before the permissioned `socialize-debt` call is made. Given that `socialize-debt` is a distinct, presumably operator/DAO-triggered transaction rather than something invoked atomically at the moment insolvency occurs, this window realistically exists in production, similar to how the original SherX report found protocols could plausibly be underwater before `payOffDebtAll` runs.

### Recommendation
Track recoverable vs. non-performing debt separately (e.g., flag positions past a liquidation/default threshold) and exclude non-performing accrued interest/principal from `total-assets` until either it is repaid or `socialize-debt` is called, or make debt write-down atomic with any state read that affects share pricing (`total-assets`, `total-assets-preview`) so `convert-to-assets`/`convert-to-shares` can never price shares off debt known to be uncollectible.

### Proof of Concept
1. A borrower takes on debt via `system-borrow` in `v0-vault-stx.clar`, and interest accrues via `accrue`/`next-index`, increasing `total-debt` (and thus `total-assets`) over time.
2. The borrower's position becomes insolvent (collateral value collapses or borrower otherwise cannot repay) — `total-borrowed`/`principal-scaled` still reflect the un-repaid debt, and `total-assets` still adds the full `debt - borrowed` interest as if it will be collected.
3. Before any DAO/operator calls `socialize-debt` to write down the bad debt, a depositor calls `withdraw`/`redeem`; `convert-to-assets` computes the payout using the inflated `total-assets`, paying out real underlying from `current-assets` at a rate that assumes the bad debt is fully collectible.
4. When `socialize-debt` is eventually called, remaining LPs absorb the full loss (via reduced `lindex`), receiving less than they should have because early withdrawers already extracted a disproportionate share of the real backing.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L308-324)
```text
(define-private (convert-to-shares-preview (amount uint))
  (let ((ta (total-assets-preview))
        (ts (total-supply-preview)))
    (if (is-eq ts u0)
        amount
        (if (is-eq ta u0)
            u0
            (mul-div-down amount ts ta)))))

(define-private (convert-to-assets-preview (amount uint))
  (let ((ta (total-assets-preview))
        (ts (total-supply-preview)))
    (if (is-eq ta u0)
        u0
        (if (is-eq ts u0)
            u0
            (mul-div-down amount ta ts)))))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L328-339)
```text
(define-private (total-debt)
  (calc-cumulative-debt (var-get principal-scaled) (var-get index)))

(define-private (debt-preview)
  (calc-cumulative-debt (var-get principal-scaled) (next-index)))

(define-private (total-assets)
  (let ((current-assets (var-get assets))
        (debt (total-debt))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L902-925)
```text
(define-public (system-repay (amount uint))
  (let (
        (states (var-get pause-states))
        (u (try! (accrue)))
        (scaled-principal (var-get principal-scaled))
        (idx (var-get index))
        (debt (total-debt))
        (total-borrowed-amount (var-get total-borrowed))
        (capped-amount (if (> amount debt) debt amount))
        (principal-reduction (calc-principal-ratio-reduction capped-amount scaled-principal debt))
        (capped-reduction (if (> principal-reduction scaled-principal) scaled-principal principal-reduction))
        (updated-scaled-principal (- scaled-principal capped-reduction))
        (principal-repaid (mul-div-down capped-amount total-borrowed-amount debt))
        (interest-paid (- capped-amount principal-repaid))
        (total-borrowed-new (if (> total-borrowed-amount principal-repaid) (- total-borrowed-amount principal-repaid) u0)))

    (try! (check-caller-auth))
    (asserts! (not (get repay states)) ERR-PAUSED)
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)

    (try! (receive-underlying capped-amount tx-sender))
    (var-set principal-scaled updated-scaled-principal)
    (var-set total-borrowed total-borrowed-new)
    (var-set assets (+ (var-get assets) interest-paid))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L944-960)
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
```
