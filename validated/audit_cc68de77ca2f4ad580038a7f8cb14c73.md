### Title
Pool accepts direct token transfers that are never credited to `cash` and can never be recovered - (File: contracts/pool/src/cache/cash.rs)

### Summary
The XOXNO Lending pool is the physical custodian of every market's tokens, but its accounting is a pure bookkeeping number (`cash`) that only moves through controller-authorized operations. Any address can call `token.transfer(sender, pool, amount)` directly. The pool has no `sweep`, `rescue`, `skim`, or admin withdrawal entrypoint, and no code path ever reconciles `token.balance(pool)` against booked `cash` to the donor's benefit. Donated tokens are therefore locked in the pool contract permanently.

### Finding Description
The pool tracks reserves in `Cache::cash`, mutated only by `credit_cash`/`debit_cash` under controller-authorized calls. `transfer_out` deliberately does not touch accounting, and inbound flows (`supply`, `repay`, `recapitalize`) credit `cash` from a measured balance delta inside the same call, so tokens already sitting on the pool address are invisible to every crediting path (`contracts/pool/src/cache/cash.rs:23-53`, `contracts/pool/src/ops/recapitalize.rs:44-67`).

The docs confirm this is by design but also confirm there is no escape: "direct donations do not automatically increase booked cash" (`docs/reference/architecture.md`), "Direct donations do not rewrite those books" (`docs/explanation/threat-model.md`), and the pool README's complete entrypoint table (`create_market`, `update_params`, `update_indexes`, `supply`, `borrow`, `withdraw`, `repay`, `net_settle`, `seize_positions`, `claim_revenue`, `recapitalize`, `flash_loan`, `create_strategy`, `upgrade`) contains no function that can move unbooked balance to anyone. `claim_revenue` pays out only booked revenue shares bounded by `cash`; `recapitalize` credits at most the backing shortfall and is unreachable without a controller-coordinated transfer. Even `flash_loan`'s strict equality checks compute expected balances from the *live* pre-loan balance (`contracts/pool/src/ops/flash.rs:53-61`, `107-120`), so the donation rides along harmlessly and remains unbooked — it neither gets absorbed into `cash` nor returns to anyone.

The same trap exists on the controller for stray balances pushed outside the declared flash-position legs: "Refunds cover only positive callback deltas of refund-listed tokens… Neither category sweeps prior balances" (`docs/explanation/threat-model.md`), and `withdraw`/`borrow` explicitly reject the pool and controller as recipients *because* funds sent there would be stranded (`tests/test-harness/tests/controller/recipient_is_protocol_contract.rs`).

### Impact Explanation
High within the donation class: any unprivileged address that transfers a supported (or arbitrary) token directly to the pool contract — a natural mistake given that `supply`, `repay`, and `recapitalize` all settle by transferring tokens *to the pool address* — loses those funds permanently. No governance action, owner call, or user entrypoint can ever move them, because every outbound transfer is bounded by booked `cash` and the donation never enters the books.

### Likelihood Explanation
Low, mirroring the external report: it requires a user error (a raw `token.transfer` to the pool or controller instead of going through `supply`/`repay`/`recapitalize`, or pushing undeclared collateral to the controller outside `flash_position`). The integration docs explicitly warn that "transferring repayment directly to the pool is a donation," which shows the scenario is realistic enough to document.

### Recommendation
Add a controller- or governance-gated sweep entrypoint on the pool that transfers `token.balance(pool) - Σ cash(across all markets sharing the asset)` to a treasury address. Since `cash` is per-market while the token balance is shared across hubs, the sweepable amount is the physical balance minus the sum of all markets' `cash` for that asset. Similarly, a sweep on the controller for non-custodied stray balances would cover the flash-position leftover case.

### Proof of Concept
```rust
// An unprivileged address sends tokens straight to the pool.
token::Client::new(env, &usdc).transfer(&alice, &pool_address, &1_000_000_000);

// Pool books never change:
let state = pool.get_sync_data(&hub_asset).state;
assert_eq!(state.cash, cash_before);                       // cash unchanged
assert_eq!(token.balance(&pool_address), cash_before + 1_000_000_000);
// Mirrors tests/test-harness/tests/pool_money_flow_audit.rs:86-96,
// where a 7*UNIT donation is asserted to belong to no market's cash book.

// No reachable call releases it:
// - pool.withdraw / claim_revenue / borrow are bounded by `cash` (Cache::require_reserves)
// - pool.recapitalize credits at most backing_shortfall from a fresh measured receipt
// - flash_loan's require_balance uses live pre-balance, so the donation is untouched
// - there is no sweep/rescue entrypoint on the pool or controller ABI
// => the 1_000_000_000 units are permanently frozen
```