### Title
Stale `assets` bookkeeping after `socialize-debt` write-down permanently blocks `redeem` even when real liquidity exists - (File: mainnet/contracts/vault/v0-vault-stx.clar)

### Summary
`redeem` enforces two independent solvency checks: `(>= current-assets inkind)` at line 808 using the AUM variable `assets`, and `(>= available-assets inkind)` at line 813 using `get-available-assets` (derived from `assets` and `total-borrowed`). If `socialize-debt` writes down `assets` via a saturating subtraction `(if (> current-assets principal-reduction) (- current-assets principal-reduction) u0)` without reducing `total-borrowed` by the identical amount, the invariant `assets == available-assets + total-borrowed` breaks, and the stricter/stale `current-assets` check at line 808 can permanently revert every redemption even though real, spendable liquidity is present.

### Finding Description
The intended accounting identity in the vault is:

```
assets == available-assets + total-borrowed
```

`assets` tracks total AUM (cash + amount lent out as debt); `total-borrowed` tracks the outstanding principal; `available-assets` (`get-available-assets`) is meant to represent the liquid cash actually sitting in the vault, derivable as `assets - total-borrowed`.

In `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar`, lines 797-831): [1](#0-0) 
`current-assets` is read at line 802 directly from the `assets` variable, and `available-assets` is computed separately at line 805 via `get-available-assets`. Both are checked as independent gates (lines 808 and 813) before any funds move.

The bug arises when `socialize-debt` (invoked from the liquidation path to write off bad debt after a shortfall) reduces `assets` using a saturating subtraction that floors at `u0`, but reduces `total-borrowed` by a different (lesser) amount corresponding to the actually-liquidated collateral shortfall. Once `assets` saturates to `u0` while `total-borrowed` remains nonzero, the two accounting values diverge from the identity: `current-assets (0) < available-assets + total-borrowed`. Because `get-available-assets` is computed independently from `assets` and `total-borrowed` (not re-derived from the now-corrupted `assets` value), `available-assets` can still legitimately reflect real spendable cash left in the vault (`> u0`), while `current-assets` is stuck at `u0`.

Every subsequent `redeem` call by any legitimate zft holder then fails the `(>= current-assets inkind)` guard at line 808 with `ERR-INSUFFICIENT-ASSETS`, regardless of `inkind > 0`, permanently — since nothing in `redeem` or elsewhere restores `assets` off of `u0` after this saturation (redeem itself only ever subtracts from `assets`, never adds back except via `deposit`). Suppliers who deposited before the socialized loss and never redeemed are locked out of withdrawing any residual, real, liquid funds that remain in the vault.

### Impact Explanation
Every `redeem` attempt by any remaining LP reverts unconditionally once this state is reached, regardless of amount or recipient — this is a total, protocol-wide freeze of redemption for the affected vault, not a partial griefing. Because `available-assets` can still be positive, real underlying tokens remain locked in the contract with no code path to release them to LPs, matching the "permanent freezing of funds" High/Critical category. The loss is borne by all suppliers who have not yet redeemed at the time `assets` saturates to zero.

### Likelihood Explanation
The precondition set is realistic and does not require privileged access: a vault with outstanding debt, at least one under-collateralized position liquidated via the normal liquidation path, and `socialize-debt` invoked as part of that flow when the liquidation shortfall exceeds recoverable collateral. This is a normal, expected liquidation outcome in a lending market during stress, not an attacker-crafted edge case requiring special capital — any unprivileged user holding zft shares is affected passively once the socialization occurs.

### Recommendation
Ensure `socialize-debt` reduces `assets` and `total-borrowed` by exactly the same `principal-reduction` amount so the identity `assets == available-assets + total-borrowed` is preserved, or remove the redundant/stale `(>= current-assets inkind)` check in `redeem` and rely solely on `(>= available-assets inkind)`, which correctly reflects real spendable liquidity independent of any write-down bookkeeping asymmetry.

### Proof of Concept
Clarinet simnet test outline:
1. Deploy vault, have two LPs deposit (e.g., LP-A deposits 1,000 STX, LP-B deposits 1,000 STX) → `assets = 2000`.
2. Borrow via `system-borrow` to push `total-borrowed` to e.g. `1500`, leaving `available-assets = 500`.
3. Trigger a liquidation that forces `socialize-debt` with a `principal-reduction` greater than `assets` remaining after prior redemptions/interest (e.g., `principal-reduction = 2000`), causing `assets` to saturate to `u0` via the quoted `(if (> current-assets principal-reduction) (- current-assets principal-reduction) u0)`, while `total-borrowed` is only reduced by, e.g., `1000` (leaving `total-borrowed = 500`).
4. Assert on-chain: `(var-get assets)` == `u0`; `(get-available-assets)` == some positive value (derived from `assets`/`total-borrowed` bookkeeping, whatever the contract computes it as) — showing the identity `assets == available-assets + total-borrowed` no longer holds.
5. Have LP-B (holding sufficient zft balance) call `redeem` with `amount > 0`, `min-out = 0`.
6. Assert the call reverts with `ERR-INSUFFICIENT-ASSETS` at the `(>= current-assets inkind)` check (line 808), even though `available-assets` computed at line 805 would satisfy the line 813 check on its own — demonstrating permanent freezing of LP-B's funds.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L797-813)
```text
(define-public (redeem (amount uint) (min-out uint) (recipient principal))
  (let (
    (states (var-get pause-states))
    (u (try! (accrue)))
    (account contract-caller)
    (current-assets (var-get assets))
    (balance (get-balance-internal account))
    (balance-check (asserts! (>= balance amount) ERR-INSUFFICIENT-BALANCE))
    (available-assets (get-available-assets))
    (inkind (convert-to-assets-preview amount)))

  (asserts! (>= current-assets inkind) ERR-INSUFFICIENT-ASSETS)
  (asserts! (not (get redeem states)) ERR-PAUSED)
  (asserts! (> amount u0) ERR-AMOUNT-ZERO)
  (asserts! (> inkind u0) ERR-OUTPUT-ZERO)
  (asserts! (>= inkind min-out) ERR-SLIPPAGE)
  (asserts! (>= available-assets inkind) ERR-INSUFFICIENT-LIQUIDITY)
```
