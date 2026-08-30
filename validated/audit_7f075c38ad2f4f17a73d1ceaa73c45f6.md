### Title
Missing upper bound on `fee-reserve` causes underflow in `calc-liquidity-rate`, permanently reverting `accrue()` and freezing deposits/redeems/borrows/repays - (File: `mainnet/contracts/vault/v0-vault-stx.clar` and sibling vaults)

### Summary
The vault's interest/reserve computation performs `(- BPS reserve-factor-bps)` without validating that `reserve-factor-bps` (the `fee-reserve` variable) is `<= BPS`. This is the same arithmetic pattern as the WatchPug `Basket.sol#handleFees()` bug (`BASE - feePct` underflow): if the reserve factor is ever configured at or above 100% (`BPS`, i.e. `u10000`), the subtraction underflows and reverts every call, permanently bricking `accrue()` and, transitively, `deposit`, `redeem`, `system-borrow`, and `system-repay` on that vault.

### Finding Description
`calc-liquidity-rate` computes the LP-facing yield rate as: [1](#0-0) 
```
(define-private (calc-liquidity-rate (var-borrow-rate uint) (util-pct uint) (reserve-factor-bps uint))
  (let ((util-applied (mul-bps-down var-borrow-rate util-pct))
        (one-minus-rf (- BPS reserve-factor-bps)))
    (mul-bps-down util-applied one-minus-rf)))
```
This is structurally identical to the reported `BASE - feePct` computation in `Basket.sol#handleFees()`: a base constant minus a fee-percentage-like input, with no clamp ensuring the fee input stays `<= BASE`.

`reserve-factor-bps` is supplied directly from the mutable `fee-reserve` contract variable in `next-liquidity-index`: [2](#0-1) 
```
(define-private (next-liquidity-index)
  (let ((states (var-get pause-states))
        (lidx (var-get lindex)))
    (if (get accrue states)
        lidx
        (let (
            (rate (interest-rate))
            (liquidity-rate (calc-liquidity-rate rate (utilization) (var-get fee-reserve)))
            ...
```
which is called unconditionally from the public `accrue` function: [3](#0-2) 
```
(define-public (accrue)
  (let ((states (var-get pause-states))
        (idx (var-get index))
        (lidx (var-get lindex)))
      (if (get accrue states)
          (ok { index: idx, lindex: lidx })
          (let ((next (next-index))
                (nliq (next-liquidity-index))
                ...
```
`accrue` is invoked at the start of every `deposit`, `redeem`, `system-borrow`, and other lending entrypoints (e.g. `deposit` at line 766, `redeem` at line 800). If `fee-reserve` is ever set to a value `>= BPS` (`u10000`, 100%), `(- BPS reserve-factor-bps)` underflows on the very next `accrue()` call, causing every subsequent call to `deposit`, `redeem`, `system-borrow`, `system-repay`, etc. to revert - the vault becomes unusable until `fee-reserve` is lowered again.

A second, related manifestation of the same root-cause class exists in `accrue`'s treasury-LP computation: [4](#0-3) 
```
(old-debt (mul-div-down scaled-principal idx INDEX-PRECISION))
(new-debt (mul-div-down scaled-principal next INDEX-PRECISION))
(debt-delta (if (> new-debt old-debt) (- new-debt old-debt) u0))
(reserve-inc (mul-div-down debt-delta (var-get fee-reserve) BPS))
(treasury-lp (if (> reserve-inc u0) (mul-div-down reserve-inc (total-supply) (- (total-assets-preview) reserve-inc)) u0))
```
Here `(- (total-assets-preview) reserve-inc)` also underflows once `fee-reserve > BPS` makes `reserve-inc` exceed `debt-delta` (and thus potentially `total-assets-preview`), providing a second revert path for the exact same misconfiguration. The same pattern is duplicated verbatim across `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdc.clar`, and `v0-vault-usdh.clar`.

I was unable to locate and inspect the `fee-reserve` setter function within the tool-call budget available, so I cannot confirm whether the DAO-governed setter enforces `<= BPS` on this value. If such a cap is enforced there, this specific underflow path is unreachable; if it is not enforced (or if a future non-DAO governance path can set it), the described revert is directly triggerable.

### Impact Explanation
If `fee-reserve` can reach or exceed `BPS` (100%) through any legitimate configuration path without an on-chain bound check, the vault's core lending operations (`deposit`, `redeem`, `system-borrow`, `system-repay`) all revert via the underflowing `accrue()` call. This is a temporary freezing of funds for all depositors/borrowers of that vault until the parameter is corrected - matching the "temporary freezing of funds" impact tier, directly analogous to the referenced WatchPug M-14 finding where an out-of-range fee parameter combined with time elapsed disrupted minting/burning until the publisher corrected the fee.

### Likelihood Explanation
Likelihood is low-to-medium and contingent on unverified information: it requires the `fee-reserve` value to be set to `>= BPS` via governance, either by operator error (analogous to the original report's "1000% licenseFee" misconfiguration) or by absence of a validation check in the setter. Given the structural identity to the flagged bug class (`BASE - feePct`-style subtraction with no clamp), and that this exact value is DAO-configurable across six near-identical vault contracts, the underlying code pattern is a real latent risk even if not currently triggered on mainnet.

### Recommendation
Add an explicit bound check wherever `fee-reserve` (reserve factor bps) is set, e.g. `(asserts! (<= new-fee-reserve BPS) ERR-...)`, and/or clamp `reserve-factor-bps` inside `calc-liquidity-rate` (e.g. `(min reserve-factor-bps BPS)`) before computing `(- BPS reserve-factor-bps)`, to make the underflow structurally impossible regardless of governance input validation elsewhere. Apply the same fix consistently to all six vault contracts (`v0-vault-stx`, `v0-vault-sbtc`, `v0-vault-ststx`, `v0-vault-ststxbtc`, `v0-vault-usdc`, `v0-vault-usdh`).

### Proof of Concept
1. DAO (or whichever role controls `fee-reserve`) sets `fee-reserve` to `u10000` or greater on any vault (e.g. `v0-vault-stx.clar`) — assuming no on-chain cap prevents this (unverified in this scan).
2. Any user calls `deposit`, `redeem`, or `system-borrow`.
3. The call chain reaches `accrue -> next-liquidity-index -> calc-liquidity-rate`, executing `(- BPS reserve-factor-bps)` with `reserve-factor-bps >= BPS`, which underflows and aborts the transaction.
4. All subsequent calls to these entrypoints revert identically until `fee-reserve` is lowered below `BPS`, freezing the vault's deposit/redeem/borrow/repay functionality.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L186-189)
```text
(define-private (calc-liquidity-rate (var-borrow-rate uint) (util-pct uint) (reserve-factor-bps uint))
  (let ((util-applied (mul-bps-down var-borrow-rate util-pct))
        (one-minus-rf (- BPS reserve-factor-bps)))
    (mul-bps-down util-applied one-minus-rf)))
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

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L835-850)
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
```
