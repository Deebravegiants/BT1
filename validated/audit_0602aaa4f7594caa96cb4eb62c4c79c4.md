### Title
`send-underlying` in the USDH vault always reverts, permanently freezing all USDH funds - (File: `mainnet/contracts/vault/v0-vault-usdh.clar`)

### Summary
The USDH vault's `send-underlying` helper moves the underlying token out of the vault by calling `transfer` directly on the external `usdh-token-v1` contract with `current-contract` as the sender, but without wrapping the call in `as-contract?`. Every other vault in the protocol (STX, sBTC, stSTX, USDC, ststxbtc) wraps outgoing transfers in `as-contract? ((with-ft ...))` / `as-contract? ((with-stx ...))` so that `tx-sender` becomes the vault contract itself, satisfying the SIP-010 requirement that the caller (`tx-sender`) equal the `sender` argument passed to `transfer`. The USDH vault omits this wrapper, so `tx-sender` remains the original external caller while `sender` is `current-contract` — these can never match, and the transfer must always fail.

### Finding Description
`send-underlying` is defined identically in both the mainnet and local-testing USDH vault contracts: [1](#0-0) [2](#0-1) 

It calls `(contract-call? usdh-token transfer amt current-contract account none)` directly, with no `as-contract?`/`with-ft` wrapper. Compare this to the equivalent function in the STX vault, which does wrap the outgoing transfer: [3](#0-2) 
and the ststxbtc vault: [4](#0-3) 

Per SIP-010, a compliant fungible-token `transfer` function enforces `(is-eq tx-sender sender)` to prevent one principal from moving another principal's balance. In `send-underlying`, `sender` is `current-contract` (the vault), but because the call is not routed through `as-contract?`, `tx-sender` remains whatever principal originated the top-level transaction (the withdrawing user, or the DAO/liquidator/borrower triggering the call). These two values will essentially never be equal, so the underlying token's `transfer` call will revert every time `send-underlying` is invoked for USDH.

This exactly mirrors the reported bug class: an unprivileged-facing function attempts to move tokens held in custody by the contract but is missing the authorization construct needed to actually move them (the Clarity analog of "no allowance set" — missing the `as-contract?`/`with-ft` outflow permission), so the call always fails.

### Impact Explanation
Any code path that pays out the underlying USDH from the vault is broken: user withdrawals/redemptions, borrower disbursement of USDH, and USDH payouts routed through `send-underlying` in the vault (used by the `market` contract's collateral-remove-redeem/vault-redeem flow) will permanently revert. Since the underlying is transferred in via `receive-underlying` normally (deposits work — receiving does not require the `as-contract?` wrapper because `sender` there is the depositing user, not the vault), USDH continues to accumulate in the vault while it can never leave, permanently freezing all deposited USDH principal and any yield. This matches the "permanent freezing of funds" High-impact category.

### Likelihood Explanation
This triggers deterministically and unconditionally on the very first attempt by any unprivileged user to withdraw/redeem USDH or receive a USDH-denominated loan from the vault — no adversarial conditions or special permissions are needed, it is a plain logic/authorization bug reachable by normal protocol usage.

### Recommendation
Wrap the outgoing `usdh-token-v1` transfer call in `send-underlying` with `as-contract?` and an explicit `with-ft` allowance, matching the pattern already used consistently in the other vault contracts (STX, sBTC, stSTX, USDC, ststxbtc), e.g.:
```clarity
(define-private (send-underlying (amt uint) (account principal))
  (begin
    (try! (as-contract? ((with-ft UNDERLYING "usdh" amt))
      (try! (contract-call? 'SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1 transfer amt tx-sender account none))
      true))
    (ok true)))
```

### Proof of Concept
1. A user deposits USDH into the vault via `vault-deposit`/`supply`, which succeeds because `receive-underlying` correctly uses `sender = account` (the depositing user), matching `tx-sender`. [5](#0-4) 
2. The same or another user later calls `redeem`/`withdraw` (or `collateral-remove-redeem` in the market contract, which calls `vault-redeem` for the USDH underlying id) to retrieve USDH.
3. Internally this invokes `send-underlying`, which calls the external token's `transfer` with `sender = current-contract` but `tx-sender` still equal to the calling user's principal (no `as-contract?` wrapper is used).
4. The external SIP-010 token contract's `(asserts! (is-eq tx-sender sender) ...)` check fails, the `transfer` call returns an error, `try!` propagates it, and the entire withdrawal transaction reverts.
5. This happens for every attempted USDH withdrawal, so all USDH held by the vault becomes permanently unretrievable.

### Citations

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L291-294)
```text
(define-private (receive-underlying (amount uint) (account principal))
  (begin
    (try! (contract-call? 'SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1 transfer amount account current-contract none))
    (ok true)))
```

**File:** mainnet/contracts/vault/v0-vault-usdh.clar (L296-299)
```text
(define-private (send-underlying (amt uint) (account principal))
  (begin
    (try! (contract-call? 'SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1 transfer amt current-contract account none))
    (ok true)))
```

**File:** local-testing/contracts/vault/vault-usdh.clar (L298-302)
```text
(define-private (send-underlying (amt uint) (account principal))
  (begin
    ;; @mainnet: (try! (contract-call? 'SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1 transfer amt current-contract account none))
    (try! (contract-call? .usdh transfer amt current-contract account none))
    (ok true)))
```

**File:** local-testing/contracts/vault/vault-stx.clar (L296-301)
```text
(define-private (send-underlying (amt uint) (account principal))
  (begin
    (try! (as-contract? ((with-stx amt))
      (try! (contract-call? .wstx transfer amt tx-sender account none))
      true))
    (ok true)))
```

**File:** mainnet/contracts/vault/v0-vault-ststxbtc.clar (L296-301)
```text
(define-private (send-underlying (amount uint) (account principal))
  (begin
    (try! (as-contract? ((with-ft UNDERLYING "ststxbtc" amount))
      (try! (contract-call? 'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststxbtc-token-v2 transfer amount tx-sender account none))
      true))
    (ok true)))
```
