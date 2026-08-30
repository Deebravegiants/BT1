## Analysis: `tx.origin`-style authentication bypass analog

This is a legitimate finding. Zest Protocol is written in Clarity, where `tx-sender` behaves exactly like Solidity's `tx.origin` — it is the *original transaction signer* and persists unchanged through the entire call stack unless a contract explicitly switches context with `as-contract?` (Clarity's equivalent of `msg.sender`, which does change per hop, is `contract-caller`) . The Sherlock report's core complaint — using the deep-call-persistent identity instead of the immediate caller identity to authorize an action — has a direct analog in Zest's vault `transfer` function.

### Root cause

Every zToken vault (`v0-vault-usdc.clar`, `v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-usdh.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`) implements the SIP-010 `transfer` function with this authorization check: [1](#0-0) 

```clarity
(define-public (transfer (amount uint) (from principal) (to principal) (memo (optional (buff 34))))
  (begin
    (try! (accrue))
    (asserts! (or (is-eq tx-sender from) (is-eq contract-caller from)) (err u4))
    (asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
    (try! (ft-transfer? zft amount from to))
    ...
```

The same pattern is repeated identically in the other vaults: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The `(is-eq tx-sender from)` branch permits authorization purely by matching the *originating signer of the transaction* — not the direct caller. This is functionally the "tx.origin" pattern: any intermediate contract that a user interacts with (e.g., a swap router, a "claim" contract, an NFT mint page — anything the user is lured into calling) can, inside its own logic, call `(contract-call? .v0-vault-usdc transfer amount victim attacker none)`. Because `contract-caller` is the malicious contract (not `from`) but `tx-sender` still equals the victim (persists across the whole call chain), the `or` condition is satisfied and the transfer succeeds without the victim ever directly authorizing that specific transfer to that specific vault.

By contrast, elsewhere in the same codebase (`collateral-add`, `supply-collateral-add`) the developers correctly guard against exactly this class of bug by requiring `(asserts! (is-eq contract-caller tx-sender) ERR-AUTHORIZATION)` — i.e., only allowing the action when there is *no* intermediary contract at all: [7](#0-6) [8](#0-7) . The `transfer` function, however, does the opposite — it explicitly widens authorization to also accept the `tx-sender`-based (origin-style) check, reopening the exact vulnerability class the rest of the protocol was hardened against.

### Title
Vault `transfer` authorizes via `tx-sender` instead of requiring `contract-caller`, enabling `tx.origin`-style theft of zToken custody - (File: `mainnet/contracts/vault/v0-vault-usdc.clar` and equivalent vault contracts)

### Summary
The SIP-010 `transfer` function in every Zest vault contract (`v0-vault-usdc.clar`, `v0-vault-stx.clar`, `v0-vault-sbtc.clar`, `v0-vault-usdh.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`) authorizes the transfer if `tx-sender` (the original transaction signer, Clarity's analog of Solidity's `tx.origin`) equals `from`, in addition to `contract-caller` (Clarity's analog of `msg.sender`) equaling `from`. Because `tx-sender` persists unchanged through the whole call stack (unless a contract uses `as-contract?`), any unrelated intermediate contract that a user is induced to call can itself call the vault's `transfer` and move that user's zToken balance to an attacker-controlled address, since the check passes on the `tx-sender == from` branch even though `contract-caller` is the malicious contract, not the user.

### Finding Description
`transfer` is defined as: [9](#0-8)  — the guard `(or (is-eq tx-sender from) (is-eq contract-caller from))` accepts authorization from either the immediate caller or the original signer of the transaction. In Clarity, `tx-sender` is not reset when a contract makes a nested `contract-call?` to another contract (only `as-contract?` changes it), so it behaves like `tx.origin`, not like `msg.sender`. This means the vault cannot distinguish "the user directly called `transfer`" from "the user called some other, unrelated contract, which then internally called `transfer` on their behalf."

The identity that should hold is: *only the token owner's direct, deliberate call (or an explicitly-approved spender) should be able to move that owner's zToken balance* — i.e. `custody-authorized-mover == direct caller of transfer`. The `tx-sender` branch breaks this identity by allowing `custody-authorized-mover == any contract in the call chain that the owner happened to interact with in the same transaction`.

### Impact Explanation
An attacker can deploy a malicious/benign-looking contract (e.g., disguised as a yield aggregator, claim page, or swap helper). When a victim who holds zTokens (e.g., zUSDC from `v0-vault-usdc`) calls any function on this malicious contract, the malicious contract can silently issue `(contract-call? .v0-vault-usdc transfer <victim-balance> victim attacker none)`. Since `tx-sender` is still the victim throughout that call, the transfer succeeds, and the victim's zToken (vault share) balance — representing custody over the underlying deposited assets — is stolen. This is direct theft of user funds at rest (Critical impact under the given rubric), since zToken share ownership is the custody record for the underlying vault assets.

### Likelihood Explanation
Likelihood is High for any user who interacts with third-party or unaudited contracts while holding vault positions — which is the normal usage pattern for DeFi users interacting with a lending/vault protocol across an ecosystem of dApps. No special privileges, oracle manipulation, or DAO compromise are needed; a single malicious contract call in the same transaction as the victim's normal interaction is sufficient.

### Recommendation
Remove the `tx-sender`-based authorization branch and require only `(is-eq contract-caller from)` (or an explicit allowance/approval mechanism) in the `transfer` function across all vault contracts, mirroring the stricter `(is-eq contract-caller tx-sender)` pattern already used in `collateral-add`/`supply-collateral-add` in `mainnet/contracts/market/v0-4-market.clar`.

### Proof of Concept
1. Victim deposits into `v0-vault-usdc`, receiving zUSDC balance (`account` = victim). 
2. Attacker deploys `malicious.clar` with a public function `lure()` that internally does: `(contract-call? 'SPXXXX.v0-vault-usdc transfer <victim-zusdc-balance> tx-sender ATTACKER none)` — note `from` argument passed is `tx-sender` inside `malicious.clar`, which Clarity resolves to the original signer (the victim), not `contract-caller`. 
3. Victim is convinced to call `(contract-call? 'ATTACKER.malicious lure)` for some unrelated purpose. 
4. Inside `malicious.clar`'s execution, `contract-caller` at the point of calling the vault is `'ATTACKER.malicious`, but `tx-sender` is still the victim. 
5. The vault's `asserts! (or (is-eq tx-sender from) (is-eq contract-caller from))` passes because `tx-sender == from == victim`. 
6. `ft-transfer?` executes, moving the victim's entire zUSDC balance to `ATTACKER`, without the victim ever directly authorizing a transfer to the vault contract.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdc.clar (L751-757)
```text
  (begin
    (try! (accrue))
    (asserts! (or (is-eq tx-sender from) (is-eq contract-caller from)) (err u4))
    (asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
    (try! (ft-transfer? zft amount from to))
    (match memo to-print (print to-print) 0x)
    (ok true)))
```

**File:** mainnet/contracts/vault/v0-vault-stx.clar (L752-757)
```text
(define-public (transfer (amount uint) (from principal) (to principal) (memo (optional (buff 34))))
  (begin
    (try! (accrue))
    (asserts! (or (is-eq tx-sender from) (is-eq contract-caller from)) (err u4))
    (asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
    (try! (ft-transfer? zft amount from to))
```

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L751-757)
```text
  (begin
    (try! (accrue))
    (asserts! (or (is-eq tx-sender from) (is-eq contract-caller from)) (err u4))
    (asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
    (try! (ft-transfer? zft amount from to))
    (match memo to-print (print to-print) 0x)
    (ok true)))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L751-757)
```text
  (begin
    (try! (accrue))
    (asserts! (or (is-eq tx-sender from) (is-eq contract-caller from)) (err u4))
    (asserts! (not (is-eq current-contract to)) ERR-TOKENIZED-VAULT-PRECONDITIONS)
    (try! (ft-transfer? zft amount from to))
    (match memo to-print (print to-print) 0x)
    (ok true)))
```

**File:** mainnet/contracts/vault/v0-vault-ststx.clar (L752-759)
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

**File:** mainnet/contracts/vault/v0-vault-ststxbtc.clar (L752-759)
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

**File:** mainnet/contracts/market/v0-4-market.clar (L1026-1027)
```text
    (asserts! (get collateral asset) ERR-COLLATERAL-DISABLED)
    (asserts! (is-eq contract-caller tx-sender) ERR-AUTHORIZATION)
```

**File:** mainnet/contracts/market/v0-4-market.clar (L1181-1183)
```text
    ;; Preconditions
    (asserts! (> amount u0) ERR-AMOUNT-ZERO)
    (asserts! (is-eq contract-caller tx-sender) ERR-AUTHORIZATION)
```
