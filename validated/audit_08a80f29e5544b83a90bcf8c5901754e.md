### Title
Tokens transferred directly to the pool (or controller) are permanently locked because all exits are gated by the internal `cash` book and no sweep entrypoint exists - (contracts/pool/src/cache/cash.rs)

### Summary
The bug class: a contract that accepts token transfers outside its accounting paths, combined with withdrawal logic that is bounded strictly by internal accounting, permanently locks the unaccounted balance. In XOXNO Lending the pool keeps a `cash` book that is credited only through measured-receipt paths (`supply`, `repay`, `net_settle`, `recapitalize`, flash-fee booking). Any tokens that arrive at the pool address without going through those paths — a direct SAC `transfer`, a rebasing/fee-on-transfer residual, or an over-delivery between the measured baseline and settlement — raise the token balance but not `cash`. Since `withdraw`, `borrow` and `claim_revenue` all debit `cash` via `Cache::require_reserves`/`debit_cash` and the pool exposes no `sweep`/rescue entrypoint (and the controller explicitly has none either), the excess is unspendable forever.

### Finding Description
`docs/reference/invariants.md` INV-ACCT-02 states it directly: "Cash is the reserve book … token donations alone do not increase it." The harness test `pool_all_money_paths_preserve_books_and_shared_token_custody` (`tests/test-harness/tests/pool_money_flow_audit.rs`) demonstrates the split: after `token.transfer(&payer, &market.pool, &(7 * UNIT))`, the assertion is `token.balance(pool) == state.cash + other.cash + 7 * UNIT` — the donation sits in custody belonging to no market.

Every outflow is book-gated:

- `withdraw` computes `net_transfer` from shares and calls `gate_and_debit` → `require_reserves` → `debit_cash`, then `transfer_out` (contracts/pool/src/ops/withdraw.rs:57-89).
- `borrow` calls `cache.require_reserves(amount)` (contracts/pool/src/ops/flash.rs:85 uses the same guard for flash loans).
- `claim_revenue` caps payout at tracked cash (INV-ACCT-06).
- `recapitalize` credits only its own measured balance delta up to the backing shortfall and refunds the remainder (INV-ACCT-03/04); it never adopts a pre-existing surplus.
- `flash_loan` uses exact-equality balance checks against a baseline measured at call start (contracts/pool/src/ops/flash.rs:53-67, 183-188), so a donation merely shifts the baseline — it is neither credited nor drainable.

The pool's endpoint list contains no `sweep`/`rescue` function, and `docs/reference/endpoints.md` states "There is no controller sweep endpoint", so a direct transfer to the controller is equally locked (undeclared callback assets "receive neither credit nor refunds").

Scenario mirroring the original: a user (or an integrating contract refunding to the wrong address) transfers N tokens directly to the pool. `cash` is unchanged; every supplier's `withdraw` is still capped by the cash book; the N tokens can never leave.

### Impact Explanation
Permanent freezing of funds. Any unaccounted inflow — user error, a misbehaving integrator, a positive rebase, or rounding residue from taxed/fee-on-transfer tokens where the pool debits less than it received — becomes inaccessible forever. Unlike the Solidity original this is not limited to a mis-accounted `poolAmount`: the token balance simply has no corresponding book entry and no privileged or unprivileged path releases it.

### Likelihood Explanation
Low-to-medium frequency, deterministic severity once it occurs. Direct `transfer` to a contract address is a common mistake/integration pattern; the flash-callback refund surface (`refund_controller_balance_delta` in contracts/controller/src/payments.rs:41-52 only refunds the delta above `balance_before`, so concurrent inbound transfers during a strategy also strand value) provides additional non-malicious paths that leave residuals.

### Recommendation
Add an owner- or governance-gated `sweep(hub_asset, recipient)` on the pool that transfers `token.balance(pool) - Σ cash` for the asset's markets, and a controller sweep for stray balances. Alternatively, credit unsolicited receipts: make `recapitalize` adopt measured surplus above the shortfall into `cash`/revenue rather than leaving it orphaned.

### Proof of Concept
Existing test demonstrates the divergence: `pool_all_money_paths_preserve_books_and_shared_token_custody` mints and transfers 7 units directly to the pool and asserts `balance == cash_market1 + cash_market2 + 7` — the 7 units are never bookable or withdrawable.

```rust
// contracts/pool/tests/flows.rs-style scenario
let donation = 7 * UNIT;
token_admin.mint(&payer, &donation);
token.transfer(&payer, &market.pool, &donation); // balance up, cash unchanged

// Every exit checks the cash book, not the balance:
// withdraw -> gate_and_debit -> require_reserves -> debit_cash
// borrow   -> cache.require_reserves(amount)
// No entrypoint exposes (balance - cash); funds are locked.
```

Uncertainty note: I did not fully enumerate whether `net_settle` or liquidation `Credit`-mode share movements could ever route value against untracked custody; all inspected paths debit the cash book, so no reachable release of the surplus was found.