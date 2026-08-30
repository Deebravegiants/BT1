### Title
`deposit` mints `u0` shares while crediting full `amount` to `assets`, permanently diluting shareholders - ([File: mainnet/contracts/vault/v0-vault-stx.clar])

### Summary
`deposit` computes `inkind` via `convert-to-shares-preview` and only requires `inkind >= min-out` before minting [1](#0-0) . Unlike `redeem`, which explicitly rejects a zero output with `ERR-OUTPUT-ZERO` [2](#0-1) , `deposit` has no such guard, so when `amount*ts < ta` and `min-out=0`, the call succeeds, `assets` grows by the full `amount`, and `total-supply` grows by `u0`.

### Finding Description
Broken identity: `total-assets == total-supply * price-per-share` should hold after every state-changing call. `deposit` breaks this: `assets_after = assets_before + amount` (line 781) while `zft_minted = inkind = convert-to-shares-preview(amount) = 0` whenever `mul-div-down(amount, ts, ta) == 0`, i.e., `amount*ts < ta` [3](#0-2) .

Code path: `deposit(amount, min-out=0, recipient)` → `inkind` computed at line 770 → slippage check `(>= inkind min-out)` at line 776 trivially passes for `inkind=0, min-out=0` → `receive-underlying` pulls `amount` from `contract-caller` at line 779 → `ft-mint? zft 0 recipient` at line 780 is a no-op (Clarity's native `ft-mint?` does not reject a zero amount) → `var-set assets (+ current-assets amount)` at line 781 unconditionally increases backing.

Root cause: the missing `(asserts! (> inkind u0) ...)` check that exists symmetrically in `redeem` (line 811) but is absent in `deposit`. This lets `assets` (the numerator of share price) grow without a matching increase in `total-supply` (the denominator), inflating price-per-share for all existing `zft` holders at the depositing caller's expense. Each `deposit` call transfers real underlying from the caller's own wallet (`account = contract-caller`, see `receive-underlying`), so the caller who triggers this is the party whose funds are absorbed into `assets` for zero shares — repeated across N distinct principals who each call `deposit` under these conditions, `assets` grows by `n*amount` while `total-supply` stays flat, permanently redistributing value to pre-existing shareholders.

### Impact Explanation
Per call: `amount` STX worth of principal is added to `assets` for `0` shares — a 100% loss of that call's principal, transferred pro-rata to all existing `zft` holders. This is repeatable indefinitely as long as `ta/ts` stays high enough relative to the deposit size (each successive call only worsens the ratio in existing holders' favor, making the condition easier to keep satisfying). The party bearing the loss is whoever calls `deposit` with `min-out=0` (or any `min-out <= 0`) under these conditions; the beneficiaries are existing `zft` holders. This is a direct loss of principal, matching a Critical severity (theft of user funds at rest, insolvency-style share/asset mismatch), though it requires the loss-taking party to itself submit the transaction with inadequate slippage protection (`min-out=0`) — it is not something an external attacker can force onto an unwilling, uninvolved victim's wallet without that wallet's own transaction.

### Likelihood Explanation
Preconditions: vault must be in a late-stage/high `ta` state with `ts>0`, and the depositor(s) must pass `min-out=0` (or a `min-out` still satisfied by 0 shares) — this is plausible if a UI/integration defaults `min-out` to `0` or a caller doesn't compute an accurate minimum. No special privilege is needed; capital cost equals the deposited `amount`, and the “attack” is trivially repeatable by anyone (including the deploying party itself, or a whitelisted principal batching multiple wallets) as long as each call independently satisfies `amount*ts < ta`.

### Recommendation
Add a zero-shares guard in `deposit` symmetric to `redeem`'s `ERR-OUTPUT-ZERO` check, e.g. `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` before minting, so that a deposit yielding zero shares reverts instead of silently donating principal to existing holders.

### Proof of Concept
Clarinet simnet test plan:
1. Deploy `v0-vault-stx`, call `initialize` (mints `MINIMUM-LIQUIDITY` shares to `NULL-ADDRESS`, `assets = MINIMUM-LIQUIDITY`, `total-supply = MINIMUM-LIQUIDITY`).
2. Drive `ta` far above `ts` (e.g., via repeated `system-borrow`/interest accrual or a large legitimate deposit followed by simulated time advancement via `stacks-block-time` and `accrue`) until `ta` is large relative to `total-supply`.
3. From N distinct simnet wallets, call `deposit(amount, u0, wallet_i)` with `amount` chosen so `amount * (get-total-supply) < (get-total-assets)`.
4. After each call, assert:
   - `(get-assets)` increased by exactly `amount`.
   - `(get-total-supply)` (via `get-total-supply`) is unchanged (`+u0`).
5. After N iterations, assert `sum(assets increase) == n*amount` while `total-supply` delta `== u0`, confirming `total-assets != total-supply * price-per-share` divergence and quantifying the redistributed value.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L308-315)
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

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L763-781)
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
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L806-811)
```text
    (inkind (convert-to-assets-preview amount)))

  (asserts! (>= current-assets inkind) ERR-INSUFFICIENT-ASSETS)
  (asserts! (not (get redeem states)) ERR-PAUSED)
  (asserts! (> amount u0) ERR-AMOUNT-ZERO)
  (asserts! (> inkind u0) ERR-OUTPUT-ZERO)
```
