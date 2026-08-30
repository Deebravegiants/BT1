### Title
Unchecked recipient address in `deposit`/`redeem` allows shares to be minted to an unreachable principal, permanently freezing user funds - (File: `mainnet/contracts/vault/v0-vault-stx.clar` and sibling vault contracts)

### Summary
All Zest v2 vault contracts (`v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-usdc.clar`, `v0-vault-usdh.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`) expose `deposit` and `redeem` functions that take a caller-supplied `recipient` principal and use it directly as the mint/transfer target, with no validation that `recipient` is a reachable, non-self address. This is the same bug class as the EthBridge report: an unchecked destination-address parameter on a value-moving function that can silently strand funds.

### Finding Description
`deposit` mints vault shares to the supplied `recipient` without any sanity check on that address: [1](#0-0) 

Contrast this with the `transfer` function in the very same contract, which explicitly guards against the destination being the vault contract itself: [2](#0-1) 

The `deposit` and `redeem` functions omit this `(asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)` check on `recipient`: [3](#0-2) 

Because Clarity has no native "zero address," the functional analog of the EthBridge zero-`_to` bug here is `recipient == current-contract` (the vault's own principal) or any other principal that can never become `contract-caller`/`tx-sender` for a subsequent `redeem` call. If a user calls `deposit` with `recipient` set to the vault's own address (e.g. due to a wallet/integration bug, or a malicious relayer/aggregator that forwards deposits on a user's behalf), `receive-underlying` still pulls the real underlying asset from the depositor, but `ft-mint? zft inkind recipient` credits the shares to the vault contract itself — a principal that cannot initiate a `redeem` call on itself in the normal call flow. The user's principal (underlying value) is consumed, backing the total-supply of shares, but the specific shares entitling recovery of that value are permanently unclaimable by any actor.

This breaks the fundamental vault identity that every unit of `zft` minted must correspond to a claim redeemable by some externally reachable principal:
`sum(redeemable_shares) == total-supply(zft)`
When `recipient == current-contract`, this becomes `sum(redeemable_shares) < total-supply(zft)` for the value contributed by that depositor — i.e., value is minted into the ledger but the corresponding claim is unrecoverable, which is economically equivalent to the depositor's principal being permanently frozen (their underlying is now custody of the vault, but no principal can invoke `redeem`/`transfer` to extract it because the owning address is the contract itself).

### Impact Explanation
This falls under "permanent freezing of funds" (High/Critical, depending on the size of the affected deposit). The depositor's underlying asset is transferred into the vault via `receive-underlying`, but their claim (the minted shares) is issued to an address that cannot execute `redeem`, `transfer`, or any withdrawal path — the funds are unrecoverable by design, mirroring exactly the EthBridge report's described consequence: "depositing tokens but not being able to receive them."

### Likelihood Explanation
Likelihood is lower than the original EthBridge case because Clarity principals do not have an implicit "zero value" the way EVM addresses default to `address(0)`; a user or integrator would need to deliberately or mistakenly pass the vault's own contract principal as `recipient`. However, this is realistic for third-party front-ends, bots, or contract-to-contract integrations that compute `recipient` programmatically (e.g., mis-wired proxy/router contracts), and the codebase itself demonstrates awareness of this exact risk by adding the guard to `transfer` but forgetting it in `deposit`/`redeem` — an inconsistency that increases confidence this is an oversight rather than an intentional design choice.

### Recommendation
Add the same guard used in `transfer` to `deposit` and `redeem` across all vault contracts:
```clarity
(asserts! (not (is-eq current-contract recipient)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
```
placed alongside the other `asserts!` checks in both functions, before `ft-mint?`/`send-underlying` is executed.

### Proof of Concept
1. User calls `deposit(amount, min-out, recipient)` on `v0-vault-stx.clar` with `recipient` set to the vault's own contract principal (`current-contract`), either directly or via a misconfigured integration.
2. `receive-underlying` transfers `amount` of the real underlying asset (`.wstx`) from the depositor to the vault: [4](#0-3) 
3. `ft-mint? zft inkind recipient` mints the corresponding shares to the vault contract's own address rather than the depositor: [5](#0-4) 
4. The depositor now holds zero `zft` balance and has no way to invoke `redeem` (which requires `contract-caller`/`account` to hold the balance) to reclaim their contributed underlying — the deposited value is permanently locked in the vault, inflating `total-supply` without a corresponding reachable claim.

### Citations

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

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L763-795)
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

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L797-831)
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
