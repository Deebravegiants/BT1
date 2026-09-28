### Title
Unfunded `recapitalize` "refund" is paid from the pool's own token balance - ([File: contracts/pool/src/ops/recapitalize.rs])

### Summary
The external report describes a function that assigns a computed amount larger than the available balance instead of clamping to the real balance. The same class exists in the pool's `recapitalize`: it computes `refund = amount - applied` and transfers that refund to the `payer` without ever verifying that `amount` tokens were actually received first. When the market has no backing shortfall (`applied == 0`), the full caller-supplied `amount` is treated as the refund and paid out of the pool's existing custody — a computed value assigned over a balance that was never delivered.

### Finding Description
`recapitalize::accounting` (contracts/pool/src/ops/recapitalize.rs:44-67) does:

```rust
let applied = amount.min(guards::backing_shortfall(&cache));
let refund = amount.checked_sub(applied)...;
cache.credit_cash(applied);
```

and `apply` (lines 26-38) then executes `outcome.cache.transfer_out(&payer, outcome.refund)`, which calls `token::transfer` from the pool contract address (cache/cash.rs:46-53).

The doc comment states "The controller transfers `amount` into the pool before this call" (line 4), but nothing in the pool enforces that. The refund is not bounded by a measured balance delta, by `cash`, or by anything else — it is `amount - applied` unconditionally. The pool contract exposes `recapitalize` as a public entrypoint, so any unprivileged address can call it directly without the controller's pre-funding step. On a healthy market where `backing_shortfall` returns 0, `applied = 0` and `refund = amount`, so the attacker simply sets `amount` to the pool's full token balance and receives it all.

This behavior is already demonstrated in the protocol's own test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` (contracts/pool/tests/flows.rs:3408-3483): a supplier deposits 10_000_000_000, then `client().recapitalize(&hub(&t.asset), &payer, &custody)` is called and `token.balance(&t.pool) == 0` — "Drain every token via an unfunded refund." The test frames it as a bookkeeping issue (cash book still claims the funds, so subsequent withdrawals fail inside the SAC transfer), but the root cause is that tokens left the pool as a "refund" for tokens that never arrived.

Additionally, even in the legitimate controller path, `credit_cash(applied)` inflates the cash book regardless of whether tokens were received; after the drain, `require_reserves` still passes for the real supplier, whose withdrawal then reverts inside the token transfer (SAC `BalanceError = 10`), as the same test asserts — a permanent freezing/theft consequence for depositors.

### Impact Explanation
Theft of user funds. A single unprivileged call drains every token held by the pool for a market asset (the physical balance is shared across hub markets on the same asset, so one call can take the entire balance). Depositors' supply shares remain on the books, but their withdrawals can never be paid — the funds are gone and the cash book overstates custody.

### Likelihood Explanation
- `recapitalize` is reachable by any address directly on the pool contract (the in-scope list includes it; the test calls it with no privileges).
- No timing, state, or economic prerequisites: the attack works on any market where `backing_shortfall < amount`, including `shortfall == 0`.
- The caller only needs to pass `amount = token.balance(pool)`; the protocol's own test reproduces the drain verbatim.

### Recommendation
Clamp the refund to tokens actually received, matching the "assign balance, not the computed amount" fix in the report:

- Measure the pool's token balance before and after (pull pattern): have `recapitalize` itself pull `amount` from `payer` via `transfer_from`/auth, or snapshot `token.balance(self)` and require that the balance increased by at least `applied` before crediting cash; `refund` should be `received - applied`, not `amount - applied`.
- Alternatively, split into two functions: a permissionless `apply_recapitalization` that only credits shortfall based on measured balance delta, and restrict the current trusted-input version to the controller.
- At minimum, `require_reserves`-style check that `refund <= balance_received` and revert otherwise.

### Proof of Concept
```
1. Market exists for asset A; pool holds B tokens of A (B = token.balance(pool)),
   market is healthy so backing_shortfall(&cache) == 0.
2. Attacker calls pool.recapitalize(hub_asset_A, attacker, B)
   - applied  = min(B, 0) = 0
   - refund   = B - 0 = B
   - credit_cash(0)  // no cash credited
   - transfer_out(attacker, B)  // pool sends its entire balance
3. token.balance(pool) == 0; attacker gains B.
4. A supplier calls withdraw(...) -> require_reserves passes (cash book unchanged)
   -> token::transfer fails with SAC BalanceError; suppliers' funds are lost.
```

This is exactly the sequence executed by `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` in contracts/pool/tests/flows.rs:3408-3483, which asserts `token.balance(&t.pool) == 0` after the unfunded `recapitalize` call and that the supplier's subsequent withdrawal fails inside the SAC transfer rather than at any pool guard.