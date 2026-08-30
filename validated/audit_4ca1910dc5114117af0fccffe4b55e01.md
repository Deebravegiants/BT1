Confirmed. The vault `deposit` functions and market-vault `collateral-add` all trust the caller-supplied `amount` parameter rather than verifying the actual tokens received, mirroring the M-15 pattern exactly.

### Title
Vault `deposit` and Market `collateral-add`/`supply-collateral-add` trust the requested `amount` instead of verifying actual tokens received, allowing insolvency with fee-on-transfer/deflationary underlying tokens - (File: `mainnet/contracts/vault/v0-vault-usdc.clar`, `mainnet/contracts/vault/v0-vault-usdh.clar`, `mainnet/contracts/vault/v0-vault-ststx.clar`, `mainnet/contracts/vault/v0-vault-ststxbtc.clar`, `mainnet/contracts/market/v0-market-vault.clar`)

### Summary
Every zVault's `deposit` function computes shares to mint from the caller-supplied `amount` parameter, calls `receive-underlying` to pull that `amount` of underlying token, and then mints shares for exactly `amount` worth of value — without ever checking that the vault's underlying balance actually increased by `amount`. The same pattern exists in `collateral-add` in the market-vault contract, which records `amount` as the user's collateral in the `collateral` map before/independent of confirming the transfer moved `amount` tokens. If the underlying SIP-010 token ever charges a transfer fee, burns a percentage on transfer, or otherwise delivers less than the requested `amount` to the contract (a fee-on-transfer/deflationary token), the contract mints/credits value based on the requested `amount` while its actual backing increased by less, breaking the 1:1 backing identity for all other depositors.

### Finding Description
In each vault (e.g. `v0-vault-usdc.clar`), `deposit` does:
```
(inkind (convert-to-shares-preview amount)) ...
(try! (receive-underlying amount account))
(try! (ft-mint? zft inkind recipient))
(var-set assets (+ current-assets amount))
``` [1](#0-0) 

`receive-underlying` merely performs the SIP-010 `transfer` call for `amount` and returns `(ok true)` without ever comparing pre/post balances: [2](#0-1) 

`inkind` (shares minted) is derived purely from the caller-supplied `amount`, and the internal `assets` accounting variable is bumped by the full `amount` regardless of what was actually received: [3](#0-2) 

Similarly, in the market-vault, `collateral-add` records the full requested `amount` into the user's collateral ledger and only afterward calls `receive-tokens`, which is just a passthrough `transfer` call with no balance verification: [4](#0-3) [5](#0-4) 

If the underlying `<ft-trait>` token (STX-wrapper, sBTC, stSTX, USDC, USDH, or stSTXbtc token) is later upgraded/replaced with, or if any of these follow a fee-on-transfer/deflationary model where `transfer` delivers less than the requested amount to the recipient, then:
- `assets` (vault's internal accounting of backing) is incremented by the full nominal `amount`, but the vault's real token balance only increased by `amount - fee`.
- `inkind` shares are minted as if the full `amount` was received.
- Any user calling `redeem` afterward draws from `assets`/shares that assume more backing exists than what is truly custodied, so later redeemers cannot all be paid in full — later withdrawals fail or drain value from other depositors.
- The same happens for market collateral: `collateral-add` credits the user's collateral map with the full requested `amount`, which can later be withdrawn via `collateral-remove`/`send-tokens` for the full nominal amount even though the market only ever custodied `amount - fee`.

This breaks the identity: `sum(shares) * share_price == actual_underlying_custodied` (for vaults) and `sum(collateral_ledger[asset]) == actual_underlying_custodied` (for market-vault collateral).

### Impact Explanation
This is a protocol-insolvency class bug: the ledger of claims (shares outstanding or collateral entries) can exceed the actual tokens custodied by the contract. Later redeemers/collateral-removers cannot be paid in full from real backing, and earlier withdrawers effectively capture value belonging to remaining depositors — direct loss of principal for some users. This matches the Critical impact criteria (protocol insolvency / theft of principal at rest).

### Likelihood Explanation
Likelihood depends entirely on whether any of the supported underlying tokens (wSTX, sBTC, stSTX, USDC, USDH, stSTXbtc) behaves as fee-on-transfer/deflationary now or is swapped for one later via the `<ft-trait>` abstraction used generically by `market.clar`'s `supply-collateral-add`, which accepts any `ft-trait`-conforming token. Since the vaults hardcode specific tokens (`.usdc`, `.usdh`, `.ststx`, `.sbtc`, `.wstx`) that are not currently known to be deflationary, likelihood for those is currently low absent a token-contract change; however, `market.clar`'s generic `<ft-trait>` acceptance in `supply-collateral-add`/`collateral-add` widens exposure to any asset onboarded by the DAO in the future. This mirrors the original report's disposition, where the protocol acknowledged the issue but chose not to support such tokens rather than fix the code — indicating this is a known, documented, unmitigated class of risk in the code itself.

### Recommendation
Before minting shares or crediting collateral, measure the underlying token balance immediately before and after the `transfer` call (or use `get-balance`) and use the actual delta as the basis for `inkind`/collateral crediting, rather than trusting the caller-supplied `amount`. Apply this consistently in `receive-underlying` (all vaults) and `receive-tokens` (market-vault).

### Proof of Concept
1. Assume (hypothetically) the underlying token for a vault, e.g. `.usdc`, is replaced/onboarded with a token that charges a 1% fee on transfer, burning it rather than forwarding it.
2. User A calls `deposit` with `amount = 1000`. `inkind` shares are computed and minted for `1000`-worth of value, but `receive-underlying` only actually delivers `990` tokens to the vault; `assets` is nonetheless incremented by `1000`. [6](#0-5) 
3. User B deposits normally with a non-deflationary flow, minting proportional shares against the now-inflated `assets`/share-price baseline.
4. When users redeem, `redeem` computes payout via `convert-to-assets-preview` based on the inflated `assets` value versus real underlying balance, so the last redeemers cannot be paid the underlying amount recorded, and value is transferred away from later redeemers to earlier ones — a permanent shortfall/insolvency in the vault's backing. [7](#0-6)

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L761-783)
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
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L795-810)
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
```

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L291-296)
```text
(define-private (receive-underlying (amount uint) (account principal))
  (begin
    (try! (contract-call? 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token transfer amount account current-contract none))
    (ok true)))

(define-private (send-underlying (amount uint) (account principal))
```

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L306-317)
```text
(define-private (convert-to-shares-preview (amount uint))
  (let ((ta (total-assets-preview))
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

**File:** mainnet/contracts/market/v0-market-vault.clar (L256-257)
```text
(define-private (receive-tokens (asset <ft-trait>) (amount uint) (account principal))
  (contract-call? asset transfer amount account current-contract none))
```

**File:** mainnet/contracts/market/v0-market-vault.clar (L374-404)
```text
(define-public (collateral-add (account principal) (amount uint) (ft <ft-trait>) (asset-id uint))
  (let ((states (var-get pause-states))
        (entry (resolve-or-create account))
        (user-id (get id entry))
        (mask (get mask entry))
        (updated-mask (mask-update mask asset-id true true)) ;; collateral, insert
        (updated-entry (merge entry (refresh updated-mask)))
        (result (add-user-collateral user-id asset-id amount)))

    (try! (check-impl-auth))
    (asserts! (not (get collateral-add states)) ERR-PAUSED)
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)

    (try! (receive-tokens ft amount account))
    
    (insert updated-entry)

    (print {
      action: "collateral-add",
      caller: contract-caller,
      data: {
        account: account,
        asset-id: asset-id,
        amount: amount,
        updated-collateral-amount: result,
        mask-before: mask,
        mask-after: updated-mask
      }
    })
      
    (ok result)))
```
