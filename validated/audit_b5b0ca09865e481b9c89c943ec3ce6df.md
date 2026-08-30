## Analysis

The reported bug class centers on an unprivileged-principal operation minting/crediting a claim based on `amount > 0` while the derived value (`votingPower`) can round to zero, breaking the identity between what was contributed and what was credited. The Zest vault contracts contain a structurally identical flaw in the ERC-4626-style deposit path: shares minted are not validated to be non-zero even though `redeem()` explicitly validates the mirrored case.

### Title
Zero-share minting in vault `deposit()` allows depositor principal to be credited to the vault with no shares issued - (File: `mainnet/contracts/vault/v0-vault-usdc.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-stx.clar`, `v0-vault-usdh.clar`)

### Summary
In every `vault-*.clar` contract, `deposit()` computes `inkind` (shares to mint) via `convert-to-shares-preview`, which uses `mul-div-down` and therefore rounds toward zero, then only guards against `amount == 0`, not `inkind == 0`. This breaks the identity `shares minted (inkind) > 0 whenever assets added (amount) > 0`. By contrast, the paired function `redeem()` explicitly enforces the analogous non-zero-output check (`ERR-OUTPUT-ZERO`), confirming the protocol designers recognized the need for this guard but omitted it from `deposit()`.

### Finding Description
`deposit()` in each vault contract: [1](#0-0) 

computes `inkind` via `convert-to-shares-preview`: [2](#0-1) 

which rounds down (`mul-div-down amount ts ta`) when `ts > 0` and `ta > 0`. The only preconditions checked are `amount > 0`, `inkind >= min-out` (slippage, trivially satisfied when `min-out = 0`, the natural default), and the supply cap — there is no `inkind > u0` assertion. The real underlying assets are transferred in and the internal `assets` ledger is incremented (`var-set assets (+ current-assets amount)`) unconditionally, while `ft-mint? zft inkind recipient` may mint `u0` shares.

This directly breaks the "share minting versus backing" identity: assets backing the vault increase by `amount`, but the depositor's claim (shares) increases by `0`. The value is absorbed into the vault (and thus proportionally into all other zToken holders' redemption value) with nothing returned to the depositor — the mirror image of value being minted from nothing.

Compare this to `redeem()`, which enforces the reciprocal invariant explicitly: [3](#0-2) 

Here `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` guards against burning shares for zero assets out — but no equivalent guard exists in `deposit()` for minting zero shares for assets in.

The scenario in which `inkind` rounds to zero grows more likely as the vault's `total-assets-preview()`/`total-supply-preview()` ratio (`ta/ts`) grows — e.g., after substantial interest accrual increases `ta` (via the `debt > borrowed` interest overhang added in `total-assets`) relative to `ts`: [4](#0-3) 

A depositor (or a frontrunner targeting a `deposit()`-for-others style flow, if a `deposit`-for-recipient pattern is exposed, since `recipient` is a caller-supplied parameter distinct from `account`) can trigger a state where a legitimate deposit resolves to `inkind = 0`, silently forfeiting the depositor's underlying assets to the pool with zero compensation.

### Impact Explanation
This is a theft-of-principal analog: real underlying assets (USDC, sBTC, STX, stSTX, USDH, stSTXbtc) are pulled from the user and permanently added to the vault's asset ledger, but the corresponding zToken claim is zero, meaning the depositor has no path to redeem those assets back. The lost value is effectively redistributed pro-rata to existing zToken holders. This matches the in-scope Critical impact category "direct theft of user funds at rest ... or protocol insolvency" from the unprivileged depositor's perspective (loss of principal), since the depositor absorbs a total, un-recoverable loss of the deposited amount.

### Likelihood Explanation
The condition requires the vault's `ta/ts` ratio to be large enough relative to a given deposit amount for `mul-div-down` to floor to zero. Because zTokens use standard token precision aligned to the underlying asset and `ta`/`ts` grow together through normal accrual, triggering this at scale requires either (a) a mature vault with heavily compounded interest relative to a small deposit amount, or (b) an attacker manipulating relative deposit size (e.g., a "dust deposit" test/edge case, or a directed small deposit on behalf of a victim if such a caller-specified recipient path is reachable by a third party). The missing guard is a code-level correctness gap independent of whether an attacker can easily engineer the precise ratio, and it is present uniformly across all six vault contracts.

### Recommendation
Add an explicit non-zero-output check in `deposit()`, mirroring the existing `redeem()` guard:
```clarity
(asserts! (> inkind u0) ERR-OUTPUT-ZERO)
```
placed alongside the other preconditions in `deposit()`, before `ft-mint?` and before assets are pulled from the depositor, in all vault contracts (`v0-vault-usdc.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-stx.clar`, `v0-vault-usdh.clar`).

### Proof of Concept
1. Let the vault reach a state where `total-assets-preview() / total-supply-preview()` is large relative to token precision (e.g., through sustained interest accrual increasing `ta` while `ts` stays comparatively small), such that `convert-to-shares-preview(amount)` for some `amount > 0` computes `mul-div-down(amount, ts, ta) = 0`.
2. A user calls `deposit(amount, 0, recipient)` with `min-out = 0` (the natural default when no slippage protection is set).
3. `inkind` evaluates to `u0`; the preconditions `(> amount u0)`, `(>= inkind min-out)` i.e. `(>= 0 0)`, and the supply cap check all pass.
4. `receive-underlying` pulls `amount` real tokens from the depositor into the vault; `var-set assets (+ current-assets amount)` credits the vault's internal ledger.
5. `ft-mint? zft inkind recipient` mints `0` zTokens to `recipient`.
6. The depositor has permanently transferred `amount` of underlying asset into the vault and received no zToken shares in return, with no revert and no recorded claim to reclaim the funds — reproducing, in the Zest vault deposit path, the exact "amount > 0 but derived credited value == 0, with no protective revert" root cause described in the referenced report.

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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L332-344)
```text
(define-private (total-assets)
  (let ((current-assets (var-get assets))
        (debt (total-debt))
        (borrowed (var-get total-borrowed))
        (interest (if (> debt borrowed) (- debt borrowed) u0)))
    (+ current-assets interest)))

(define-private (total-assets-preview)
  (let ((current-assets (var-get assets))
        (debt (debt-preview))
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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L795-813)
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

  (try! (ft-burn? zft amount account))
```
