## Finding

### Title
`accrue` treasury-LP minting can underflow/divide-by-zero and permanently freeze the vault - (File: `mainnet/contracts/vault/v0-vault-usdh.clar` and equivalent `v0-vault-*.clar` / `local-testing/contracts/vault/vault-*.clar` files)

### Summary
The `accrue` function mints treasury shares (`treasury-lp`) proportional to the protocol's fee-reserve cut of newly accrued interest, using the formula `reserve-inc * total-supply / (total-assets-preview - reserve-inc)`. Unlike the analogous `socialize-debt` function in the same contract, which explicitly guards against the subtrahend exceeding the minuend, this calculation has no check that `total-assets-preview > reserve-inc`. If `reserve-inc >= total-assets-preview`, the subtraction underflows (Clarity aborts on uint underflow) or, if exactly equal, the division divides by zero — in both cases `accrue` reverts. Since every state-mutating vault entrypoint (`deposit`, `redeem`, `system-borrow`, `system-repay`) calls `accrue` first and cannot proceed without it succeeding, this permanently bricks the vault the same way the Y2K `mintRollovers`/`previewWithdraw` divide-by-zero permanently bricks the rollover queue.

### Finding Description
`accrue` computes: [1](#0-0) 

```
(reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
(treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0))
```

`total-assets-preview` is `current-assets` (physical, un-lent liquidity) plus `interest` (the virtual, unrepaid portion of debt, i.e. `debt-preview - total-borrowed`): [2](#0-1) 

`interest` only resets close to zero after debt is fully repaid (via `system-repay`, which reduces `total-borrowed` in step with `principal-scaled`): [3](#0-2) 

If, at the moment `accrue` next runs, the vault's physical liquidity (`current-assets`) is near zero (most assets are lent out) and the previously-unpaid interest has just been fully repaid (so `interest` ≈ 0), then any subsequent jump in the interest index over an elapsed period produces `debt-delta` that constitutes essentially all of `total-assets-preview`. With `fee-reserve` taking a meaningful cut of that delta, `reserve-inc` can equal or exceed `total-assets-preview`, causing `(- (total-assets-preview) reserve-inc)` to underflow (Clarity aborts the transaction on uint underflow) — this makes `mul-div-down` either divide by zero or abort outright, and the whole `accrue` call reverts.

Notably, the sibling function `socialize-debt` explicitly guards against exactly this class of underflow: [4](#0-3) 
```
(new-lindex (if (and (> old-total-assets u0) (> old-total-assets debt-reduction))
               (mul-div-down current-lindex (- old-total-assets debt-reduction) old-total-assets)
               u0))
```
This shows the missing guard in `accrue`'s treasury-lp computation is an oversight, not an intentional design choice.

### Impact Explanation
`accrue` is a hard dependency of every state-mutating vault call: [5](#0-4) [6](#0-5) [7](#0-6) 

If `accrue` deterministically reverts once this underflow condition is hit (and since `debt-delta`/`reserve-inc` only grow further with time, the condition does not self-resolve), then `deposit`, `redeem`, `system-borrow`, and `system-repay` all become permanently unusable on that vault. This is a permanent freeze of funds (all deposited principal and unclaimed yield in that vault become inaccessible), matching the "High" impact bar (permanent freezing of unclaimed yield/funds), and depending on total value in the affected vault could reach protocol-insolvency-adjacent severity since users can never withdraw.

### Likelihood Explanation
Likelihood depends on utilization and fee-reserve configuration reaching a state where nearly all liquidity is borrowed out, prior interest has just been fully repaid (interest resets near zero), and enough time/interest accrues in one step so that the reserve cut of that single delta approaches the vault's entire preview-TVL. This is a plausible operating condition for a high-utilization vault (not requiring DAO compromise or malicious governance action) but is a narrower trigger than the original Y2K bug's simple "deposit == relayer fee" condition, so likelihood is assessed as low-to-medium without further modeling of realistic `fee-reserve`/index growth parameters.

### Recommendation
Add an explicit guard before computing `treasury-lp`, mirroring the pattern already used in `socialize-debt`:
```clarity
(treasury-lp (if (and (> reserve-inc u0) (> (total-assets-preview) reserve-inc))
                 (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc))
                 u0))
```
This prevents the underflow/divide-by-zero from ever reverting `accrue`, at the cost of skipping treasury-share minting in that edge case (acceptable, since minting a share representing >100% of TVL was invalid math to begin with).

### Proof of Concept
1. Vault has `current-assets` ≈ 0 (near-full utilization) after a `system-repay` that fully repays outstanding debt, resetting `total-borrowed` ≈ `debt` so `interest` ≈ 0.
2. Time passes (or the index otherwise jumps) such that `next-index` produces a large `debt-delta` on the next `accrue` call, while `current-assets` remains ≈ 0, making `total-assets-preview` ≈ `debt-delta`.
3. `fee-reserve` (set via DAO governance to a normal-but-nontrivial reserve percentage) yields `reserve-inc = debt-delta * fee-reserve / BPS` that is ≥ `total-assets-preview`.
4. Any subsequent call to `deposit`, `redeem`, `system-borrow`, or `system-repay` invokes `accrue`, which computes `(- (total-assets-preview) reserve-inc)`, underflows, and the transaction aborts.
5. Because `debt-delta`/`reserve-inc` continue to grow over time relative to a stagnant, near-zero `current-assets`, the condition persists, and the vault becomes permanently unusable for all core operations. [1](#0-0)

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L339-350)
```text
(define-private (total-assets-preview)
  (let ((current-assets (var-get assets))
        (debt (debt-preview))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))

;; -- Treasury LP preview helpers --------------------------------------------

(define-private (calc-treasury-lp-preview)
  (let ((scaled-principal (var-get principal-scaled))
        (idx (var-get index))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L799-808)
```text
    (account contract-caller)
    (current-assets (var-get assets))
    (balance (get-balance-internal account))
    (balance-check (asserts! (>= balance amount) ERR-INSUFFICIENT-BALANCE))
    (available-assets (get-available-assets))
    (inkind (convert-to-assets-preview amount)))

  (asserts! (>= current-assets inkind) ERR-INSUFFICIENT-ASSETS)
  (asserts! (not (get redeem states)) ERR-PAUSED)
  (asserts! (> amount u0) ERR-AMOUNT-ZERO)
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L841-848)
```text
          (let ((next (next-index))
                (nliq (next-liquidity-index))
                (scaled-principal (var-get principal-scaled))
                (old-debt (mul-div-down scaled-principal idx INDEX-PRECISION))
                (new-debt (mul-div-down scaled-principal next INDEX-PRECISION))
                (debt-delta (if (> new-debt old-debt) (- new-debt old-debt) u0))
                (reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
                (treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0)))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L863-866)
```text
(define-public (system-borrow (amount uint) (receiver principal))
  (let (
      (states (var-get pause-states))
      (u (try! (accrue)))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L900-923)
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

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L953-956)
```text
        ;; Write down lindex proportionally to loss in total-assets
        (new-lindex (if (and (> old-total-assets u0) (> old-total-assets debt-reduction))
                       (mul-div-down current-lindex (- old-total-assets debt-reduction) old-total-assets)
                       u0)))
```
