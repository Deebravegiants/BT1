### Title
Depositing while `total-assets` rounds/settles to zero but `total-supply` is non-zero silently mints 0 shares, letting attacker steal the deposit - (File: `mainnet/contracts/vault/v0-vault-usdc.clar`)

### Summary
Zest's ERC4626-style vault contracts (`v0-vault-usdc.clar`, `v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdh.clar`, and their `local-testing` twins) compute deposit shares with `convert-to-shares-preview`. Unlike the Sherlock/Velar report where `pool_value == 0` causes a **revert** (DoS), the Zest implementation special-cases this state to **return `u0`** instead of reverting: [1](#0-0) 

This converts a potential DoS into a **silent value-loss bug**: a depositor's real underlying tokens are pulled into the vault and its share of assets increases, but the depositor is minted **zero shares** — their principal is effectively donated to existing shareholders.

### Finding Description
`deposit` computes `inkind` (shares to mint) via `convert-to-shares-preview amount`, then mints `inkind` to the recipient and adds the *full* `amount` to the notional `assets` accounting variable regardless of whether `inkind` is zero: [2](#0-1) 

The only guard against a zero-share mint is the slippage check `(asserts! (>= inkind min-out) ERR-SLIPPAGE)` — which a user who has not set `min-out > 0` will not catch, and which does not prevent the underlying transfer from happening before the check fails to matter (the check is enforced, but a naive/careless depositor who passes `min-out = 0` sails right through with `inkind = 0`).

The root cause is that `total-assets`/`total-assets-preview` can reach `0` while `total-supply`/`total-supply-preview` remains non-zero: [3](#0-2) 

`assets` is a **notional** bookkeeping variable, decremented only on `redeem` (not on `system-borrow`, since borrowed principal is not subtracted from `assets`, only tracked via `total-borrowed`): [4](#0-3) 

Meanwhile, `total-supply` includes protocol-fee LP shares (`treasury-lp`) that `accrue` mints to `.dao-treasury` on every interest accrual and are never automatically burned: [5](#0-4) 

Because `dao-treasury`'s LP balance persists independently of ordinary depositor activity, it is entirely possible for all "real" depositors to fully redeem (`assets -> 0`, `total-debt <= total-borrowed` so `interest -> 0`, giving `total-assets == 0`) while `total-supply` remains non-zero due to residual, unredeemed `treasury-lp` shares held by `dao-treasury`. In this state:

`convert-to-shares-preview` hits the `ts != 0, ta == 0 -> return u0` branch instead of reverting. Any subsequent depositor who calls `deposit` gets `0` shares minted while their `amount` is folded into `assets`, i.e. it becomes redeemable value backing the treasury's pre-existing shares. This breaks the fundamental share/backing identity: `Δassets_deposited != Δbacking_of_minted_shares` (0 shares minted for a positive contribution to total assets).

### Impact Explanation
This is a direct theft of user principal: a depositor transfers real tokens into the vault (`receive-underlying`) but receives no claim (`0` shares) on those tokens, and the vault's outstanding shares (dao-treasury's leftover `treasury-lp`) become worth strictly more as a result. Whoever holds those outstanding shares (or subsequent legitimate first depositor who mistakenly gets a windfall via the `ts == 0` branch resetting) can redeem and capture the donated value. This matches the "direct theft of user funds at rest or in motion" Critical impact class, since the loss is deterministic and non-recoverable for the depositor once the transaction lands.

### Likelihood Explanation
Likelihood depends on reaching a state where `total-assets == 0` while `total-supply != 0`. This is plausible under normal operation because:
- `accrue` mints treasury LP shares whenever `reserve-inc > 0`, and these are not auto-burned.
- All non-treasury depositors can legitimately redeem down to `assets == 0` (e.g., after a period of no outstanding borrow/interest), leaving only the treasury's dust of `treasury-lp` shares outstanding.
- No explicit minimum-liquidity/dead-shares protection exists to prevent `total-assets` from reaching exactly `0` while `total-supply > 0`.
A depositor without slippage protection (`min-out = 0`, the natural default for a "first/refill" depositor) would be silently harmed; this does not require any privileged action, just normal vault usage timing.

### Recommendation
- Never allow `deposit` to mint `0` shares for a non-zero `amount`; explicitly `asserts!` that `inkind > 0` regardless of `min-out`.
- Consider burning `treasury-lp` dust or excluding it from `total-supply-preview` when `total-assets == 0`, or re-seed `total-assets` with a minimum-liquidity floor so the ratio can never degenerate to `ts != 0, ta == 0`.
- Alternatively, when `ta == 0` and `ts != 0`, either revert the deposit (fail-safe, matching the original DoS design) or reset the vault's share accounting atomically instead of silently returning `0` shares.

### Proof of Concept
1. Vault `v0-vault-usdc.clar` is live with active LPs; interest accrues over time, and `accrue` periodically mints `treasury-lp` shares to `.dao-treasury` per [6](#0-5) .
2. All non-treasury LPs `redeem` their full shares, and any outstanding debt is fully repaid such that `interest == 0`, driving `current-assets -> 0` and thus `total-assets -> 0` (per lines 332-337), while `dao-treasury`'s `treasury-lp` balance keeps `total-supply != 0`.
3. A new user calls `deposit(amount, 0, recipient)`. `convert-to-shares-preview amount` evaluates `ts != 0`, `ta == 0` and returns `u0` (lines 306-313).
4. `deposit` proceeds: `receive-underlying` pulls `amount` real tokens from the user, `ft-mint? zft 0 recipient` mints nothing, and `var-set assets (+ current-assets amount)` credits the deposit into the notional pool backing the treasury's existing shares (lines 761-793).
5. `dao-treasury` (or whoever ends up holding the outstanding shares) can now `redeem` those shares for a proportional share of the newly inflated `total-assets`, capturing the victim's deposit for free.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L306-313)
```text
(define-private (convert-to-shares-preview (amount uint))
  (let ((ta (total-assets-preview))
        (ts (total-supply-preview)))
    (if (is-eq ts u0)
        amount
        (if (is-eq ta u0)
            u0
            (mul-div-down amount ts ta)))))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L332-337)
```text
(define-private (total-assets)
  (let ((current-assets (var-get assets))
        (debt (total-debt))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L761-793)
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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L811-819)
```text
  (asserts! (>= available-assets inkind) ERR-INSUFFICIENT-LIQUIDITY)

  (try! (ft-burn? zft amount account))
  (try! (send-underlying inkind recipient))
  (var-set assets (- current-assets inkind))

  (print {
    action: "redeem",
    caller: contract-caller,
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
