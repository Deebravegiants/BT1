This confirms the asymmetry: `redeem` explicitly guards against a zero output with `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` at [1](#0-0) , but `deposit` has no equivalent check on the minted `inkind` (shares) value, relying only on the caller-supplied `min-out` slippage guard [2](#0-1) . Since `convert-to-shares-preview` floors (`mul-div-down`) [3](#0-2) , a deposit called with `min-out` of `u0` (or any value `≤` the rounded-down share amount) can mint `0` shares while still transferring the depositor's assets into the vault and permanently increasing `assets` for existing shareholders [4](#0-3) . This is present identically in every vault variant (`sbtc`, `ststx`, `ststxbtc`, `stx`, `usdc`, `usdh`) in both `mainnet/contracts/vault/*` and `local-testing/contracts/vault/*`.

### Title
Missing zero-share-output guard in `deposit` allows silent loss of depositor principal - (File: mainnet/contracts/vault/v0-vault-usdc.clar and all sibling vault contracts)

### Summary
The `deposit` function computes minted shares via `convert-to-shares-preview`, which floors the result (`mul-div-down`), but unlike `redeem` it never asserts that the computed share amount is non-zero. It only enforces `(>= inkind min-out)`, so if the caller passes `min-out` equal to `u0` (or any value `≤` the rounded-down amount), a deposit that rounds down to `0` shares still succeeds: the depositor's assets are transferred into the vault and `assets` is incremented, but no shares are minted to the recipient.

### Finding Description
`convert-to-shares-preview` returns `assets * total-supply / total-assets` rounded down via `mul-div-down` whenever both `total-supply` and `total-assets` are non-zero [3](#0-2) . In `deposit`, the only guard on the resulting `inkind` value is the slippage check `(asserts! (>= inkind min-out) ERR-SLIPPAGE)` [5](#0-4) ; there is no `(asserts! (> inkind u0) ...)` analogous to the one present in `redeem` [6](#0-5) . Consequently, whenever `total-supply` and `total-assets` have grown large relative to a small deposit amount (e.g., after significant interest accrual inflates `total-assets` relative to `total-supply`), `deposit` can round `inkind` to `0`, and if `min-out` is `u0`, the deposit proceeds: `receive-underlying` pulls the caller's assets into the vault, `ft-mint?` mints `0` shares, and `assets` is permanently increased by the deposited amount [4](#0-3) . This breaks the value identity that should tie minted shares to contributed backing (`Δshares/Δassets` should track `total-supply/total-assets`); here `Δshares = 0` while `Δassets > 0`, silently diluting the depositor's claim to zero while donating the deposited value to existing shareholders.

### Impact Explanation
The depositor's principal is transferred into the vault and irrecoverably lost (permanent freezing/theft of principal from the depositor's perspective, with the value effectively redistributed to other shareholders as unearned yield), matching the "theft of principal" / "permanent freezing of funds" impact classes. The condition is most reachable in the higher-total-asset vaults (e.g., `sbtc`, `ststxbtc`) after accrued interest has scaled `total-assets` well above `total-supply`, making small deposit amounts round to zero shares.

### Likelihood Explanation
This requires a depositor (or an integrating contract/front-end that defaults `min-out` to `u0`) to submit a small deposit amount relative to the vault's `total-assets`/`total-supply` ratio, and is entirely self-inflicted rather than exploitable against another party — the caller retains the ability to protect themselves by supplying a non-zero `min-out`. Likelihood is therefore moderate: dependent on user/integration behavior and on the vault's asset/supply ratio reaching a point where floor-division loses full unit value for realistic deposit sizes.

### Recommendation
Add an explicit `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` in `deposit`, mirroring the guard already present in `redeem`, so that a deposit unconditionally reverts if it would mint zero shares, regardless of the `min-out` value supplied by the caller.

### Proof of Concept
1. Vault accrues interest over time such that `total-assets` (e.g., `100_000_000` units) grows much larger than `total-supply` (e.g., `100_000` shares).
2. Caller invokes `deposit` with `amount = 999`, `min-out = u0`.
3. `convert-to-shares-preview` computes `mul-div-down(999, 100_000, 100_000_000)`, which floors to `0`.
4. `(asserts! (>= inkind min-out) ERR-SLIPPAGE)` passes because `0 >= 0`.
5. `receive-underlying` transfers the `999` units from the caller into the vault; `ft-mint? zft 0 recipient` mints zero shares; `assets` is incremented by `999`.
6. The caller has permanently lost `999` units of principal and received nothing in return, while remaining shareholders' claim on the vault's assets increases proportionally.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L308-317)
```text
        (ts (total-supply-preview)))
    (if (is-eq ts u0)
        amount
        (if (is-eq ta u0)
            u0
            (mul-div-down amount ts ta)))))

(define-private (convert-to-assets-preview (amount uint))
  (let ((ta (total-assets-preview))
        (ts (total-supply-preview)))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L768-775)
```text
      (inkind (convert-to-shares-preview amount)))

    (asserts! (not (get deposit states)) ERR-PAUSED)
    (asserts! (var-get initialized) ERR-INIT)
    (asserts! (not (var-get in-flashloan)) ERR-REENTRANCY)
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)
    (asserts! (>= inkind min-out) ERR-SLIPPAGE)
    (asserts! (<= (+ current-assets amount) CAP-SUPPLY) ERR-SUPPLY-CAP-EXCEEDED)
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L777-779)
```text
    (try! (receive-underlying amount account))
    (try! (ft-mint? zft inkind recipient))
    (var-set assets (+ current-assets amount))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L808-810)
```text
  (asserts! (> amount u0) ERR-AMOUNT-ZERO)
  (asserts! (> inkind u0) ERR-OUTPUT-ZERO)
  (asserts! (>= inkind min-out) ERR-SLIPPAGE)
```
