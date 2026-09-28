### Title
Tokens sent directly to the pool or controller are permanently frozen — no recovery path exists - ([File: contracts/pool/src/cache/cash.rs])

### Summary
The UXD report's bug class — a contract that can receive assets but can never send them back — maps directly onto XOXNO Lending. Any unprivileged address can invoke `token.transfer(user -> pool)` or `token.transfer(user -> controller)` on a market's SAC. Neither contract has a sweep/rescue entrypoint, and every outbound path is strictly bounded by tracked cash (pool) or by measured balance deltas (controller), so stray balances can never leave. The donation is permanently frozen.

### Finding Description
- The pool tracks a `cash` book per `(hub_id, asset)` market. `Cache::debit_cash` refuses to spend more than `self.cash`, and the only token-moving helper, `Cache::transfer_out` (`contracts/pool/src/cache/cash.rs:46`), is called exclusively from owner-only entrypoints bounded by the cash book (`withdraw`, `borrow`, `claim_revenue`, `flash_loan`). INV-ACCT-02 (`docs/reference/invariants.md:104`) states "token donations alone do not increase" cash, and `tests/test-harness/tests/pool_money_flow_audit.rs:86` pins that "an unsolicited donation belongs to no market's cash book."
- The only pool outflow not gated by `cash` is the `recapitalize` refund, but the pool is `#[only_owner]` (owner = controller), and `contracts/controller/src/markets.rs`'s `recapitalize` passes a *measured receipt* — the user's own transfer delta — so it can never touch a pre-existing donated balance.
- The controller has no token-recovery entrypoint at all. Its only outbound token paths are explicitly delta-bounded: `refund_controller_balance_delta` (`contracts/controller/src/payments.rs:41-52`) "preserv[es] the pre-existing balance," and `swap_tokens` (`contracts/controller/src/strategies/swap.rs:49-52`) refunds only `amount_in - actual_spent`. The regression test `tests/test-harness/tests/controller/recipient_is_protocol_contract.rs:1-5` documents this explicitly: "the controller holds funds no balance-delta measurement can ever claim," which is why `borrow`/`withdraw` addressed to the pool or controller are rejected — but a *direct SAC transfer* bypasses that check entirely.
- All 14 pool mutators are `#[only_owner]` and there is no `sweep_balance`-equivalent on pool or controller (contrast `contracts/swap-aggregator/src/lib.rs:189`, which does have one — proof the pattern was considered and omitted here).

### Impact Explanation
Permanent freezing of funds: any tokens pushed to the pool or controller addresses are irrecoverable by anyone, including governance. Pool donations additionally sit permanently above the cash book, inflating real balances without ever being spendable. This satisfies the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Reachable by any unprivileged address via a single `token.transfer` SAC call to the pool or controller address — an explicitly allowed path in scope. As in the original report, accidental transfers are uncommon but unrecoverable when they occur. Medium severity.

### Recommendation
Add an owner/governance-gated rescue entrypoint, or — matching the report's recommendation — restrict inbound crediting. For the pool, recover only `token.balance(pool) - sum_of_market_cash` for that asset (never below zero). For the controller, add a governance `sweep` that transfers the full stray balance, since the controller's invariant is to hold zero between calls; all existing flows already preserve only their measured deltas, so sweeping the whole balance is safe.

### Proof of Concept
```rust
// Any user, no privileged auth:
let sac = token::StellarAssetClient::new(&env, &asset);
sac.mint(&user, &1_000);
token::Client::new(&env, &asset).transfer(&user, &pool_addr, &1_000);
// or .transfer(&user, &controller_addr, &1_000);

// Pool: state.cash unchanged (INV-ACCT-02); every outflow asserts
// self.cash >= amount (cash.rs:15-21) — the 1_000 can never leave.
// Controller: refund_controller_balance_delta (payments.rs:41) only
// refunds deltas above balance_before; swap_tokens only refunds
// amount_in - actual_spent (swap.rs:49). No entrypoint touches the
// pre-existing 1_000. Balance is stuck forever.
```