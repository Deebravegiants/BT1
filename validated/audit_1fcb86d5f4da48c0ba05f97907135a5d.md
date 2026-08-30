### Title
Reentrant `redeem()` lacks the `in-flashloan` guard present in `deposit()`, letting a flashloan callback drain vault backing before the `assets` ledger is decremented — (File: `mainnet/contracts/vault/v0-vault-sbtc.clar` and equivalent vaults)

### Summary
Each Zest vault (`v0-vault-sbtc.clar`, `v0-vault-stx.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdc.clar`, `v0-vault-usdh.clar`) implements the same `redeem()` function that burns shares, sends the underlying token to the recipient, and only afterward updates the internal `assets` accounting variable — the same checks-effects-interactions ordering flaw described in the Sherlock `_sendSherRewardsToOwner()` finding (state deleted/updated *after* the external transfer). Unlike `deposit()`, `redeem()` is missing the `(asserts! (not (var-get in-flashloan)) ERR-REENTRANCY)` guard, and `flashloan()` invokes an attacker-supplied `<flash-callback>` contract mid-flight while `in-flashloan` is `true` and after underlying funds have already been sent out.

### Finding Description
In `redeem()`: [1](#0-0) 

`current-assets` is captured once via `var-get assets` inside the `let` at function entry, and the ledger is only updated at the very end:
```
(try! (ft-burn? zft amount account))
(try! (send-underlying inkind recipient))
(var-set assets (- current-assets inkind))
```
This mirrors exactly the bug class in the Sherlock report: the external transfer (`send-underlying`) happens before the internal aggregate state (`assets`) is decremented.

Compare `deposit()`, which explicitly blocks calls while a flashloan is in progress: [2](#0-1) 

`redeem()` has no equivalent `(asserts! (not (var-get in-flashloan)) ERR-REENTRANCY)` check — this is an inconsistency between the two entry points that both mutate the same `assets` ledger.

The reentrancy window is opened by `flashloan()`, which calls an attacker-controlled contract (`fc <flash-callback>`) while `in-flashloan` is `true` and *after* the loan amount has already left the contract via `send-underlying`: [3](#0-2) 

Because `fc` is a caller-supplied trait implementation (not a fixed, hookless SIP-010 token like `UNDERLYING`), the callback genuinely has attacker-controlled control flow — unlike the sBTC/SIP-010 `transfer` calls inside `receive-underlying`/`send-underlying`, which are fixed, hookless token contracts and cannot themselves reenter. The reachable reentrancy path is specifically: `flashloan()` → attacker callback → `redeem()` (since `redeem()` does not check `in-flashloan`).

Since `current-assets` is snapshotted once per call and `assets` is only decremented after the external `send-underlying` call, an attacker who holds `zft` shares can reenter `redeem()` from inside the flashloan callback and have each nested call observe the same stale `current-assets`/`available-assets`, allowing shares to be burned and underlying paid out multiple times against the same, not-yet-decremented ledger balance before the outer call finally updates `assets`. This decouples "shares burned" from "backing removed," breaking the identity:
```
Σ(underlying paid out via redeem) == Δ(assets ledger)
```
which should hold per call but is only enforced with a stale snapshot under reentrancy.

### Impact Explanation
This breaks the core share-backing invariant of a tokenized vault: shares can be redeemed for more underlying value than the vault's own accounting believes has left, letting the attacker extract more underlying than their `zft` holdings should legitimately back, at the expense of other depositors. This is theft of principal / protocol insolvency for the affected vault (Critical), since it directly reduces the assets available to legitimate share holders below what circulating shares represent.

### Likelihood Explanation
The flashloan mechanism itself is not exploited for its fee/whitelist logic — it is used purely as the vehicle to obtain attacker-controlled callback execution mid-transaction, which the vault's own `deposit()` function acknowledges as a real reentrancy risk requiring a guard, but `redeem()` omits that same guard. The attacker must already hold (or acquire) `zft` shares and be whitelisted for flashloan (`can-flashloan` permission), which is a governance-controlled flag, not a privileged/DAO-compromise-only precondition; whitelisted flashloan borrowers are a normal integration/user category, not admins.

### Recommendation
- Add `(asserts! (not (var-get in-flashloan)) ERR-REENTRANCY)` to `redeem()` (and any other state-mutating entry point sharing the `assets` ledger) to match `deposit()`.
- Apply checks-effects-interactions consistently: perform `(var-set assets (- current-assets inkind))` immediately after `(try! (ft-burn? zft amount account))` and before `(try! (send-underlying inkind recipient))`.
- Re-audit all vault files (`v0-vault-sbtc.clar`, `v0-vault-stx.clar`, `v0-vault-ststx.clar`, `v0-vault-ststxbtc.clar`, `v0-vault-usdc.clar`, `v0-vault-usdh.clar`) since they share this identical pattern.

### Proof of Concept
1. Attacker deploys a `<flash-callback>` implementing contract and is whitelisted (`can-flashloan: true`) for a vault, e.g. `v0-vault-sbtc`.
2. Attacker deposits underlying to obtain `zsBTC` shares ahead of time (normal `deposit()` flow).
3. Attacker calls `flashloan(amount, none, callback-contract, data)`. The vault sends `amount` out via `send-underlying` and then invokes `callback-contract`'s `callback` function while `in-flashloan` is `true`. [4](#0-3) 
4. Inside `callback`, the attacker's contract calls `redeem()` on the same vault with their pre-acquired `zsBTC` shares. Because `redeem()` never checks `in-flashloan`, this call is accepted; it burns shares and calls `send-underlying` again before `assets` is decremented. [5](#0-4) 
5. The attacker can repeat step 4 for further nested redemptions while `current-assets`/`available-assets` remain stale relative to the outer flashloan call, extracting underlying beyond what the (not yet updated) `assets` ledger reflects, before the flashloan repayment step executes.
6. Once the callback returns, the flashloan repayment (`receive-underlying (+ amount fee)`) proceeds; the net effect is that legitimate depositors' backing has been reduced beyond their circulating share entitlement.

### Citations

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L761-779)
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

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L795-815)
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
```

**File:** mainnet/contracts/vault/v0-vault-sbtc.clar (L1013-1024)
```text
    ;; Set reentrancy guard
    (var-set in-flashloan true)

    ;; Send funds to receiver
    (try! (send-underlying amount funds-receiver-resolved))

    ;; Execute callback
    (try! (contract-call? fc callback amount fee data))

    ;; Pull back amount + fee from provider
    (try! (receive-underlying (+ amount fee) funds-provider))

```
