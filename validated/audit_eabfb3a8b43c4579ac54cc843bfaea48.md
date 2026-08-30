### Title
Missing recipient validation in vault `redeem`/`deposit`/`system-borrow` allows self-inflicted permanent loss of withdrawn principal - (File: mainnet/contracts/vault/v0-vault-usdc.clar)

### Summary
The `redeem` function in every Zest vault contract (`v0-vault-usdc.clar`, `v0-vault-usdh.clar`, `v0-vault-sbtc.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-stx.clar`) lets the caller specify an arbitrary `recipient` for the underlying tokens returned on redemption, but never checks that `recipient` is not the vault contract itself (`current-contract`). This is the same bug class as the reported `PrimitiveEngine.withdraw` issue: a user can accidentally (or be tricked into) set the recipient to the vault's own address, causing the shares they burn to be permanently lost while the underlying is “sent” back into the vault instead of to the user.

### Finding Description
`redeem` burns the caller's `zft` shares and calls `send-underlying`, which performs a SIP-010 `transfer` from `current-contract` to whatever `recipient` was supplied, then decrements the internal `assets` accounting variable by the same amount: [1](#0-0) 

`send-underlying` performs the transfer unconditionally to `account` with no restriction: [2](#0-1) 

If `recipient` (or `account` in `deposit`, or `receiver` in `system-borrow`) equals the vault's own principal, the SIP-010 `transfer` degenerates into a same-address transfer: the underlying token balance of the vault is unchanged, yet:
- The user's `zft` shares are already burned via `ft-burn? zft amount account` before the transfer.
- The `assets` variable is decremented via `(var-set assets (- current-assets inkind))` regardless of where the tokens actually ended up.

This breaks the identity: `shares burned ⇒ underlying delivered to redeemer`. Instead, `shares burned ⇒ underlying stays trapped in the vault, unaccounted for (assets var reduced) and the user's claim (zft) permanently destroyed with no compensating balance received by the user`.

Notably, the codebase itself recognizes the danger of a vault-as-target address in the `transfer` function, which explicitly guards against sending shares to `current-contract`: [3](#0-2) 

But this identical guard (`(asserts! (not (is-eq current-contract to)) ...)`) is absent from `redeem`, `deposit`, `system-borrow`, and analogous market-level pass-through functions such as `borrow` and `collateral-remove-redeem` where an unresolved `receiver` is forwarded directly to `vault-redeem`/`send-underlying`: [4](#0-3) 

### Impact Explanation
A user who redeems shares with `recipient` set to the vault's own contract principal permanently loses their principal: their `zft` claim is burned, and the underlying is not credited to them nor to any tracked recipient — it remains in the vault but is removed from the `assets` accounting used for share-price computation (`total-assets`/`total-assets-preview`), so it becomes non-recoverable, un-attributed value. This is a permanent freezing/loss of user funds equivalent to the original report’s “funds stuck in the engine.” The same defect applies to `deposit`'s `recipient` and `system-borrow`'s `receiver`, and to market-level `borrow`/`collateral-remove-redeem` where a user-supplied `receiver` can be set to the vault or market contract, causing debt to be recorded against the user while the borrowed principal never reaches an externally-owned/controllable address.

### Likelihood Explanation
Likelihood is low-to-moderate: it requires the user (or a front-end bug, or a malicious dApp/wallet integration) to pass the vault's own contract principal as `recipient`/`receiver`. There is no economic incentive for an attacker to target another user this way (functions are self-referential to `contract-caller`'s own shares/debt), so this is a self-inflicted-mistake class bug rather than an attacker-vs-victim exploit, mirroring the original report's "Alice accidentally specifies the engine address" scenario.

### Recommendation
Add the same guard already present in `transfer` to `redeem`, `deposit`, `system-borrow`, and to market-level functions that forward a user-supplied `receiver`/`recipient` (`borrow`, `collateral-remove-redeem`, `collateral-remove`), rejecting any operation where the destination equals the vault's or market's own contract principal:
```clarity
(asserts! (not (is-eq current-contract recipient)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
```

### Proof of Concept
1. User calls `redeem(amount, min-out, recipient)` on `v0-vault-usdc.clar` passing `recipient = 'SP...v0-vault-usdc` (the vault's own principal) [5](#0-4) .
2. `ft-burn? zft amount account` burns the user's shares.
3. `send-underlying inkind recipient` executes a SIP-010 `transfer` from the vault to the vault itself — a no-op on token balance [2](#0-1) .
4. `assets` is decremented by `inkind`, permanently mis-stating vault accounting while the user receives nothing and cannot reclaim the burned shares.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L296-299)
```text
(define-private (send-underlying (amount uint) (account principal))
  (begin
    (try! (contract-call? 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx transfer amount current-contract account none))
    (ok true)))
```

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L750-757)
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

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L795-829)
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
  (try! (send-underlying inkind recipient))
  (var-set assets (- current-assets inkind))

  (print {
    action: "redeem",
    caller: contract-caller,
    data: {
      redeemer: account,
      recipient: recipient,
      shares-burned: amount,
      amount-received: inkind,
      assets: (- current-assets inkind)
    }
  })

  (ok inkind)))
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1211-1234)
```text
(define-public (collateral-remove-redeem (ft <ft-trait>) (amount uint) (min-underlying uint) (receiver (optional principal)) (price-feeds (optional (list 3 (buff 8192)))))
  (let ((ft-address (contract-of ft))
        (asset (try! (get-asset ft-address)))
        (ztoken-id (get id asset))
        (underlying-id (if (is-eq ztoken-id zSTX) STX
                       (if (is-eq ztoken-id zsBTC) sBTC
                       (if (is-eq ztoken-id zstSTX) stSTX
                       (if (is-eq ztoken-id zUSDC) USDC
                       (if (is-eq ztoken-id zUSDH) USDH
                       (if (is-eq ztoken-id zstSTXbtc) stSTXbtc
                       u100)))))))  ;; invalid sentinel for non-ztoken
        (funds-receiver (match receiver recv recv contract-caller)))

    (asserts! (<= underlying-id stSTXbtc) ERR-UNKNOWN-VAULT)
    
    ;; Step 1: Remove collateral - sends zTokens to THIS contract (market)
    ;; receiver=current-contract so market holds the zTokens
    (try! (collateral-remove ft amount (some current-contract) price-feeds))
    
    ;; Step 2: Redeem zTokens for underlying
    ;; vault-redeem calls vault.redeem which burns shares from contract-caller (market)
    ;; Since market now holds the zTokens, this succeeds
    ;; Underlying tokens are sent to the specified receiver
    (vault-redeem underlying-id amount min-underlying funds-receiver)))
```
