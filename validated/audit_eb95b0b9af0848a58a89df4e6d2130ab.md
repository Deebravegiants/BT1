### Title
Vault `deposit()` mints zero shares for real underlying, permanently diluting depositor into existing holders — ([File: mainnet/contracts/vault/v0-vault-usdc.clar])

### Summary
Zest's tokenized vaults (`v0-vault-usdc.clar`, `v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdh.clar`) compute minted shares via `convert-to-shares-preview` using floor division `(mul-div-down amount ts ta)`, and unlike `redeem()`, `deposit()` never asserts that the resulting share amount is non-zero. This reproduces the exact "zero-shares-minted" bug class from the referenced xETH report (M-10), and is even less mitigated than the reviewed wxETH fix, since Zest's `deposit()` has no non-zero-mint guard at all.

### Finding Description
`deposit()` in every vault contract computes `inkind` (shares to mint) via `convert-to-shares-preview`: [1](#0-0) 

This rounds down in favor of the pool. The guard checks in `deposit()` are only: [2](#0-1) 

There is **no assertion that `inkind > 0`**. Compare this to `redeem()` in the same file, which explicitly guards against a zero output: [3](#0-2) 

Because `min-out` defaults to `u0` in naive integrations (and even a nonzero `min-out` of `u0` passes the `(>= inkind min-out)` check trivially), a depositor whose `amount` rounds to `0` shares under the current exchange rate (`ta`/`ts`) will still have their underlying asset transferred into the vault via `receive-underlying`, `assets` will be incremented by their full deposit, but `ft-mint?` will mint `u0` zft to them. The value they deposited becomes permanently embedded in the vault's `assets`/`total-assets-preview`, backing the *existing* shareholders' shares instead of the depositor's — a direct value transfer from the new depositor to old shareholders. This is worse than the pre-fix wxETH bug (which needed to reach `<1` wxETH before rounding to zero was even possible while still under a nonzero-mint check); here, no code prevents a `deposit()` call from silently minting zero shares.

The share price (`ta`/`ts`) rises naturally via the accrual mechanism (`total-assets-preview` growing due to `total-debt`/interest, mirrored by `total-supply-preview` growth from the `calc-treasury-lp-preview` fee-reserve shares — see the `total-assets-preview`/`total-supply-preview` helpers in the same file). Once the vault has been live long enough (or a single depositor has been the sole minority holder while significant interest accrued), any subsequent small deposit that rounds down to zero shares will lose 100% of that deposit's value to existing holders.

### Impact Explanation
This breaks the core share-minting-vs-backing identity: `assets_after = assets_before + amount`, but `shares_after = shares_before + 0`, meaning the depositor's value is instantly and irrecoverably transferred to existing shareholders. This is a direct theft of user principal (not merely unclaimed yield), matching the Critical/High impact bar of "theft of user funds at rest" for the affected depositor.

### Likelihood Explanation
The exchange rate (`ta`/`ts`) naturally increases over the vault's lifetime as interest accrues on borrowed funds while the underlying "assets" pool absorbs the corresponding interest income, so this condition can be reached organically without any attacker donation, and is guaranteed to eventually occur for sufficiently small deposit amounts relative to a matured exchange rate. No privileged role or flashloan is required — any regular user calling `deposit()` with a small `amount` (or a default `min-out` of `0`) after the vault has accrued enough interest is affected.

### Recommendation
Add an explicit `(asserts! (> inkind u0) ERR-OUTPUT-ZERO)` check to `deposit()` in all vault contracts, mirroring the existing check already present in `redeem()`, so that deposits which would round down to zero shares revert instead of silently forfeiting the depositor's principal to existing shareholders.

### Proof of Concept
1. Vault is live with `total-supply` = `S` shares and `total-assets-preview` = `A`, where `A/S` (the exchange rate) has grown large due to accrued interest over time (organic protocol operation, no attacker action needed to inflate it).
2. A user calls `deposit(amount, u0, recipient)` with an `amount` small enough that `mul-div-down(amount, S, A) == 0` (i.e., `amount * S < A`).
3. `deposit()` passes all its checks — `(> amount u0)` is true, `(>= inkind min-out)` is `(>= u0 u0)` = true — so the function proceeds.
4. `receive-underlying` transfers the user's `amount` into the vault, `assets` is incremented by `amount`, but `ft-mint? zft u0 recipient` mints zero shares to the depositor.
5. The depositor's `amount` is now backing all existing shareholders' shares; the depositor holds nothing and cannot recover the deposited value. [4](#0-3)

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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L761-797)
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

(define-public (redeem (amount uint) (min-out uint) (recipient principal))
  (let (
    (states (var-get pause-states))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L806-815)
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
