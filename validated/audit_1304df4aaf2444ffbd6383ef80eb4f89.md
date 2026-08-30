## Analysis

The Zest vault contracts (e.g. `mainnet/contracts/vault/v0-vault-sbtc.clar`, and identically in `v0-vault-stx.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdc.clar`, `v0-vault-usdh.clar`) contain a permissionless `accrue` function that is the direct structural analog of `VaultRewarderLib._claimVaultRewards`/`_accumulateSecondaryRewardViaEmissionRate` in the report: a public function that computes an incremental delta since the last recorded timestamp and mints a proportional fee/reward based on that delta, using round-down division.

### Title
Griefing via frequent permissionless `accrue()` calls causes protocol reserve fee (treasury yield) to round down to zero and be permanently lost - (File: `mainnet/contracts/vault/v0-vault-sbtc.clar`)

### Summary
`accrue()` is `define-public` with no access control and is invoked as the first step of essentially every vault action (`deposit`, `redeem`, `system-borrow`, `system-repay`, `transfer`, `flashloan`). On each call it computes `debt-delta` (interest accrued since `last-update`) and mints the treasury's cut (`treasury-lp`) proportional to that delta. Because the delta is calculated from `last-update` to `stacks-block-time` and `last-update` is reset on every call regardless of whether `debt-delta`/`reserve-inc` rounded to zero, an attacker (or even a busy chain with fast Nakamoto blocks) that triggers `accrue()` every block causes each incremental `debt-delta`/`reserve-inc` to round down to zero, permanently forfeiting the DAO treasury's fee share of interest that would otherwise have accumulated.

### Finding Description
`accrue()` computes: [1](#0-0) 

```
old-debt      = mul-div-down(scaled-principal, idx,  INDEX-PRECISION)
new-debt      = mul-div-down(scaled-principal, next, INDEX-PRECISION)
debt-delta    = new-debt - old-debt                     (rounds down)
reserve-inc   = mul-div-down(debt-delta, fee-reserve, BPS)   (rounds down again)
treasury-lp   = mul-div-down(reserve-inc, total-supply, total-assets-preview - reserve-inc)
```

`last-update` is unconditionally advanced to `stacks-block-time` whenever `idx` or `lindex` change, even if `debt-delta`/`reserve-inc` computed to `0`: [2](#0-1) 

Because `mul-div-down` performs floor division at two levels (`old-debt`/`new-debt`, then `reserve-inc`), a small enough `time-delta` between consecutive calls yields `debt-delta = 0` or a `debt-delta` too small for `fee-reserve/BPS` to produce a non-zero `reserve-inc`, per call. Since `accrue()` is called on every state-changing action and is itself directly public, an attacker (or simply organic high-frequency traffic — deposits/redeems/borrows/repays from unrelated users in adjacent blocks) can keep `time-delta` between consecutive `accrue()` invocations small enough that `reserve-inc` rounds to zero on every call, while `index`/`lindex` still advance (so borrowers' debt and depositors' yield accrue normally via the cumulative index). The protocol's fee cut (`reserve-inc` → `treasury-lp` minted to `.dao-treasury`) is calculated strictly from the *incremental* delta of that single call, not from a running/cumulative remainder — so once a call rounds `reserve-inc` to zero, that slice of interest revenue is gone forever; it is not retried or accumulated on the next call because `last-update` has already advanced past it.

This is structurally identical to the reported bug class: a permissionless function that recomputes a reward/fee based on the delta since the last call, using floor division, invoked in rapid succession to keep the delta below the rounding threshold — except here the value drained is the vault's protocol/reserve fee (unclaimed yield owed to the DAO treasury) rather than a Notional reward token.

### Impact Explanation
The griefing attack causes a permanent loss of the reserve fee (`fee-reserve` share of interest) that should accrue to `.dao-treasury` via `treasury-lp` minting. As TVL and `scaled-principal` grow, larger absolute deltas are needed to avoid the rounding floor, but so does the attack window shrink relative to block time on faster Stacks (Nakamoto) block production — mirroring exactly the L2/Arbitrum condition in the original report. This is theft/permanent freezing of unclaimed protocol yield, satisfying the "theft of unclaimed yield" / "permanent freezing of unclaimed yield" High-severity criteria, without requiring any privileged access or DAO compromise.

### Likelihood Explanation
`accrue()` has zero access control and zero cost beyond a normal transaction fee, and is already invoked as a side effect of every deposit/redeem/borrow/repay/transfer/flashloan call across every vault (`vault-sbtc`, `vault-stx`, `vault-ststx`, `vault-ststxbtc`, `vault-usdc`, `vault-usdh`). No special privileges, whitelisting, or DAO action are required — an attacker (or simply routine high-frequency usage) can trigger it every block. The rounding-to-zero condition is a deterministic consequence of the two nested floor divisions and is easily satisfiable for small time deltas or moderate `fee-reserve` values, matching the original report's escalation-accepted, high-severity conclusion.

### Recommendation
Track unaccrued/undistributed reserve fee as a running remainder (or accumulate `debt-delta` continuously without resetting `last-update` on rounding-to-zero events) so that sub-threshold increments are carried forward and eventually collected rather than discarded. Alternatively, compute `reserve-inc` using round-up division favoring the protocol, or rate-limit/batch `accrue()` so the minimum interval between fee-affecting accruals cannot be trivially minimized by an attacker.

### Proof of Concept
Using `mainnet/contracts/vault/v0-vault-sbtc.clar` constants (`INDEX-PRECISION = u1000000000000` = 1e12, `BPS = u10000`): [3](#0-2) 

1. Assume `scaled-principal = 100000000` (1 sBTC, 8-decimal base units), `idx = INDEX-PRECISION = 1e12`, `interest-rate = u500` (5% APR bps), `fee-reserve = u1000` (10%).
2. Attacker calls any state-mutating vault function (or `accrue()` transitively) every ~1 second (achievable on fast Stacks/Nakamoto blocks): `time-delta = 1`.
3. `calc-multiplier-delta(rate=500, time-delta=1, round-up=true)` ≈ `INDEX-PRECISION + 1586` (rounded up), giving `next ≈ 1e12 + 1586`.
4. `old-debt = mul-div-down(1e8, 1e12, 1e12) = 1e8`.
5. `new-debt = mul-div-down(1e8, 1e12+1586, 1e12) = floor(1e8 + 1e8*1586/1e12) = floor(1e8 + 0.1586) = 1e8`.
6. `debt-delta = new-debt - old-debt = 0` ⇒ `reserve-inc = 0` ⇒ `treasury-lp = 0` — no fee minted, yet `last-update` is advanced.
7. Repeating this every block for an extended period (a day, a week) causes the treasury's accumulated fee share for that entire period to be zero, whereas calling `accrue()` only once at the end of the period would have correctly minted a non-zero `treasury-lp` reflecting the full interest accrued — the DAO treasury permanently loses that yield. [4](#0-3)

### Citations

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L25-28)
```text
(define-constant BPS u10000)
(define-constant PRECISION u100000000)
(define-constant INDEX-PRECISION u1000000000000)  ;; 1e12 for index calculations
(define-constant SECONDS-PER-YEAR-BPS (* u31536000 BPS))
```

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L147-151)
```text
(define-private (mul-div-down (x uint) (y uint) (z uint))
  (/ (* x y) z))

(define-private (mul-div-up (x uint) (y uint) (z uint))
  (/ (+ (* x y) (- z u1)) z))
```

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L833-864)
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

(define-public (system-borrow (amount uint) (receiver principal))
  (let (
```
