### Title
Missing zero-share guard in `deposit` allows silent loss of principal, asymmetric with `redeem`'s `ERR-OUTPUT-ZERO` check - (File: `mainnet/contracts/vault/v0-vault-ststx.clar`)

### Summary
`redeem` enforces `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` before transferring underlying out, guaranteeing a caller can never burn shares for zero assets. `deposit` has no equivalent check on the minted-shares side: it only enforces `(asserts! (>= inkind min-out) ERR-SLIPPAGE)`, which is satisfied trivially when both `inkind` and `min-out` are `u0`. This lets underlying be pulled from a depositor and permanently locked in the vault while zero shares are minted to the recipient.

### Finding Description
Identity that should hold symmetrically for both directions of the ERC4626-style vault: for any strictly positive `amount`, the resulting non-zero side of the conversion must be non-zero, or the transaction must revert — i.e. `amount > 0 => inkind_deposit(amount) > 0` OR revert, exactly mirroring `amount > 0 => inkind_redeem(amount) > 0` OR revert.

Code path in `deposit`: [1](#0-0) 
computes `inkind` via `convert-to-shares-preview`: [2](#0-1) 
which explicitly returns `u0` when `total-supply-preview` (`ts`) is non-zero but `total-assets-preview` (`ta`) is zero, or, more generally, whenever `amount * ts / ta` rounds down to `0` (e.g. tiny `amount` relative to a high share price). `deposit` only checks `(asserts! (>= inkind min-out) ERR-SLIPPAGE)` — with the common naive-frontend default `min-out = u0`, `(>= 0 0)` passes. The function then proceeds to pull `amount` of underlying from the caller (`receive-underlying`), mint `inkind` (`u0`) shares to `recipient`, and increase `assets` by `amount`: [3](#0-2) 

Compare to `redeem`, which explicitly rejects the zero-output case before doing anything irreversible: [4](#0-3) 

`ta = 0` with `ts > 0` is a reachable state: `total-assets` can be driven to (or toward) zero relative to outstanding supply through bad-debt write-off in `socialize-debt`, which sets `assets` down and can drive `total-assets-preview` to `u0` while `zft` supply remains positive: [5](#0-4) 

In that state, any subsequent `deposit` call, using the common `min-out = u0` default, silently mints zero shares while consuming the caller's `amount` of underlying — the funds become permanently unclaimable principal absorbed into `assets` with no corresponding share claim minted.

### Impact Explanation
Every deposit made while `ta = 0, ts > 0` (or, more generally, whenever `amount` is small enough that `mul-div-down(amount, ts, ta)` rounds to zero) results in a 100% loss of the depositor's transferred `amount` — the depositor receives `ok u0` shares and no revert, so wallets/front-ends relying on transaction success will treat it as a completed deposit. This is a direct, unrecoverable loss of principal borne entirely by the depositor, matching Critical severity (permanent freezing/theft of the depositing principal). The condition is repeatable for every deposit call made in that state, and scales with `amount` — an attacker or unaware user can lose an arbitrarily large amount per call.

### Likelihood Explanation
Triggering requires the vault to be in a `ta≈0, ts>0` state (reachable via legitimate `socialize-debt` bad-debt write-downs) or simply a high share-price rounding scenario for small deposits — no privileged access is needed to become a victim, and any ordinary user using a default `min-out = 0` (the typical unprotected default) is exposed. No attacker capital is required to grief a third party if the state naturally arises from protocol loss events; the only "attack" needed is calling public `deposit` at the right time, which anyone (including the affected user themselves, unknowingly) can trigger.

### Recommendation
Add a symmetric guard in `deposit`, mirroring `redeem`'s `ERR-OUTPUT-ZERO` check: `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` immediately after computing `inkind` and before pulling underlying/minting shares, so that any deposit that would produce zero shares reverts instead of silently destroying the depositor's principal.

### Proof of Concept
Clarinet simnet test plan:
1. Deploy/initialize the ststx vault; perform a normal deposit to get `ts > 0` and `ta > 0`.
2. Drive `total-assets-preview` to `u0` while keeping `zft` supply positive — e.g. call `socialize-debt` (as the authorized caller) with a `scaled-amount` sized to zero out `assets`/`total-assets`, or otherwise construct `ta = 0, ts > 0`.
3. Call `redeem` for a small `amount` in this state and assert it reverts with `(err u802012)` (`ERR-OUTPUT-ZERO`), confirming the guard on redeem's side.
4. Call `deposit(amount, u0, victim)` in the same state and assert:
   - The call returns `(ok u0)` (no revert).
   - `ft-get-balance zft victim` is unchanged (`u0` shares minted).
   - The victim's/depositor's underlying balance decreased by `amount`.
   - `(var-get assets)` increased by `amount` with no corresponding claim created.
5. This demonstrates the asymmetry: identical zero-conversion condition reverts on `redeem` but succeeds and destroys funds on `deposit`.

### Citations

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L308-315)
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

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L763-795)
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

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L808-817)
```text
  (asserts! (>= current-assets inkind) ERR-INSUFFICIENT-ASSETS)
  (asserts! (not (get redeem states)) ERR-PAUSED)
  (asserts! (> amount u0) ERR-AMOUNT-ZERO)
  (asserts! (> inkind u0) ERR-OUTPUT-ZERO)
  (asserts! (>= inkind min-out) ERR-SLIPPAGE)
  (asserts! (>= available-assets inkind) ERR-INSUFFICIENT-LIQUIDITY)

  (try! (ft-burn? zft amount account))
  (try! (send-underlying inkind recipient))
  (var-set assets (- current-assets inkind))
```

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L944-967)
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
    (var-set principal-scaled (if (> scaled-principal scaled-amount) (- scaled-principal scaled-amount) u0))
    (var-set total-borrowed (if (> borrowed principal-reduction) (- borrowed principal-reduction) u0))
    (var-set assets (if (> current-assets principal-reduction) (- current-assets principal-reduction) u0))

```
