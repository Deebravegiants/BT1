### Title
Vault `deposit` mints zSTX/zUSDC/zUSDH/etc. shares to an unvalidated `recipient`, permanently freezing depositor funds if `recipient` is the vault contract itself or the `NULL-ADDRESS` - (File: `mainnet/contracts/vault/v0-vault-stx.clar` and sibling vaults `v0-vault-sbtc.clar`, `v0-vault-usdc.clar`, `v0-vault-usdh.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`)

### Summary
The bond-teller analog (recipient unchecked before minting a value-bearing token) maps directly to Zest's `deposit` entry point in every tokenized vault contract. `deposit` mints `zft` shares to an attacker/user-supplied `recipient` principal with no restriction, while the vault's own `transfer` function explicitly guards against sending shares to the vault contract itself.

### Finding Description
`deposit` accepts underlying tokens from `contract-caller`, computes `inkind` shares, and mints them straight to `recipient` without any validity check: [1](#0-0) 

Compare this to `transfer`, which explicitly forbids sending shares to the vault contract's own principal: [2](#0-1) 

The vault even defines a `NULL-ADDRESS` constant: [3](#0-2) 

but this constant is not referenced inside `deposit` to reject `recipient = NULL-ADDRESS` or `recipient = current-contract`. Because the presence of the `current-contract` guard in `transfer` shows the developers recognized the danger of shares being sent to an address from which they can never be moved (the vault contract cannot itself be `tx-sender`/`contract-caller` to later call `transfer` or `redeem` on its own held shares), the same guard is missing on the `deposit` path where a caller supplies `recipient` directly. If `recipient` is set to the vault's own contract principal (or `NULL-ADDRESS`), `ft-mint? zft inkind recipient` succeeds, `assets` is incremented by the deposited amount, but the minted shares become permanently unredeemable — no principal can ever present the vault contract itself as `tx-sender`/`contract-caller` to call `redeem`.

This breaks the identity: `sum(shares outstanding that are redeemable) == assets backing them`. Shares are minted (backing recorded), but a portion of those shares can never be redeemed for the underlying — the deposited principal is effectively burned/frozen exactly as in the referenced bond report where `payoutToken` was sent to `address(0)`.

### Impact Explanation
Underlying principal deposited by a user (STX/sBTC/USDC/USDH/stSTX/stSTXBTC) becomes permanently locked/frozen if the shares are minted to the vault contract itself or the null address, since there is no mechanism for the vault to call its own `transfer`/`redeem` to recover them. This is a permanent freezing of funds for the depositing user's principal — meeting the High severity bar of "temporary/permanent freezing of funds."

### Likelihood Explanation
`deposit` is a fully public, unprivileged entry point taking `recipient` as a raw parameter, so any user (or a front-end/integration bug) could pass the vault's own principal or the null address. The likelihood mirrors the original bond finding: a user's mistake or a naive integrating contract forwarding an unvalidated recipient triggers the loss, with no revert to catch it, unlike the `transfer` function which already guards this exact case.

### Recommendation
Add the same precondition used in `transfer` to `deposit` (and to `redeem`'s recipient parameter for underlying-asset sends), rejecting `recipient` equal to `current-contract` or `NULL-ADDRESS`:
```clarity
(asserts! (not (is-eq current-contract recipient)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
(asserts! (not (is-eq recipient NULL-ADDRESS)) ERR-INVALID-ADDRESS)
```

### Proof of Concept
1. Caller holds underlying tokens and calls `deposit(amount, min-out, recipient)` on `v0-vault-stx.clar` with `recipient` set to the vault contract's own principal (`current-contract`) or `NULL-ADDRESS`. [4](#0-3) 
2. `receive-underlying` pulls `amount` of underlying from the caller into the vault, `assets` increases, and `ft-mint? zft inkind recipient` mints shares to that unreachable principal.
3. Because `transfer` requires `(is-eq tx-sender from)` and the vault contract can never be `tx-sender`, and `redeem` similarly requires the caller to hold and burn their own balance via `contract-caller`, the minted shares at `recipient` = vault/NULL-ADDRESS can never be moved or redeemed — the deposited principal is permanently frozen, matching the impact described in the source bond report.

### Citations

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L37-39)
```text
;; -- Utilities
(define-constant NULL-ADDRESS (unwrap-panic (principal-construct? (if is-in-mainnet 0x16 0x1a) 0x0000000000000000000000000000000000000000)))
(define-constant ITER-UINT-8 (list u0 u1 u2 u3 u4 u5 u6 u7))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L752-759)
```text
(define-public (transfer (amount uint) (from principal) (to principal) (memo (optional (buff 34))))
  (begin
    (try! (accrue))
    (asserts! (or (is-eq tx-sender from) (is-eq contract-caller from)) (err u4))
    (asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
    (try! (ft-transfer? zft amount from to))
    (match memo to-print (print to-print) 0x)
    (ok true)))
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
