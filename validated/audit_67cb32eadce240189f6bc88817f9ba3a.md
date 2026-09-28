### Title
Unfunded `recapitalize` drains pool custody while the cash book stays overstated, permanently freezing supplier withdrawals - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
Analogous to CVE-2018-19890 (a crash on a rarely exercised edge path that turns into denial of service), the pool's `recapitalize` path pays out an "excess refund" from pool custody even when the caller funded nothing. The token transfer succeeds — custody is drained — but the internal `cash` book is left at its pre-call level, so the market reports itself solvent and liquid while every subsequent withdrawal, revenue claim, or borrow draw passes the pool's own guards and then crashes inside the SAC transfer for lack of balance.

### Finding Description
`recapitalize` is an unprivileged pool entrypoint (reachable through the controller). It credits at most the backing shortfall and refunds any excess to `payer` without minting shares. The refund leg is paid out of the pool's token balance based on the *booked* amount, not on what the payer actually transferred in. A caller passing an `amount` equal to (or exceeding) the pool's real token balance while supplying no funding receives a refund transfer of real tokens. Because the cash book is only debited for the credited shortfall — not for custody that left via the refund — `cache.cash()` still claims the drained funds exist.

This is proven by an in-repo regression test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` at `contracts/pool/tests/flows.rs:3408-3483`:

- After a supplier deposits `10_000_000_000`, `t.client().recapitalize(&hub(&t.asset), &payer, &custody)` drains the pool balance to 0 (`assert_eq!(token.balance(&t.pool), 0)` at line 3433).
- The book still claims `cash >= deposit` (lines 3435-3439).
- The supplier's `withdraw` then passes `require_reserves` / `require_backed_market` (which read the book, `contracts/pool/src/guards.rs:52-66`) and reverts with the SAC's own `BalanceError = 10`, not `InsufficientLiquidity` or `PoolInsolvent` (lines 3443-3476).

The guards in `contracts/pool/src/guards.rs` (`require_utilization_below_max`, `require_liquidation_buffer`, `require_backed_market`) all evaluate `cache.cash()` rather than the contract's real token balance, so once custody and book diverge no internal check can catch it — mirroring the FAAC invalid dereference: the code trusts an internal representation that no longer matches reality and dies at the point of use.

### Impact Explanation
Permanent freezing of user funds, plus theft. The recapitalize caller directly receives pool tokens it never funded (theft of user funds). Thereafter, every supplier exit reverts inside the token contract: withdrawals, `SeizeMode::Transfer` liquidation payouts, `claim_revenue` transfers (`contracts/pool/src/ops/revenue.rs:25-31`), and borrow draws all fail at the SAC transfer because the pool has no balance. The state is unrecoverable through user-facing calls — `recapitalize` itself only measures the book shortfall, which is zero by its own accounting, so the hole cannot be repaired by repeating it.

### Likelihood Explanation
Reachable by any unprivileged address in a single call: `pool.recapitalize(hub_asset, payer, amount)` with `amount` up to the pool's full token balance and zero funding. No timing, oracle, or multi-account setup required. Severity is bounded to Medium/High rather than critical insolvency math because the loss is capped at current pool custody, but for the affected market it is total.

### Recommendation
- In `recapitalize`, settle by *measured receipt*: transfer `amount` in from `payer` first, compute the real received delta via `token.balance(contract)` before/after, and only refund the measured excess over the credited shortfall — consistent with the protocol's documented "measured-receipt settlement" pattern used in flash loans and router legs.
- Alternatively, reconcile `cache.cash()` against the actual token balance before paying any refund, and refuse (or clamp to) a refund exceeding `received - credited`.
- Add an invariant guard on commit: `cache.cash() <= token.balance(pool)` for ops that can move tokens out.

### Proof of Concept
The repository already contains the executable PoC at `contracts/pool/tests/flows.rs:3408-3483`:

```rust
// contracts/pool/tests/flows.rs:3416-3483 (abridged)
let deposit = 10_000_000_000i128;
token_admin.mint(&t.pool, &deposit);
let supplied = t.client().supply(&t.sup(0, deposit)).get_unchecked(0)
    .position.scaled_amount;

let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &payer, &custody); // payer funds nothing
assert_eq!(token.balance(&t.pool), 0);                     // custody gone
assert!(t.state_snapshot().cash >= deposit);               // book still solvent

// Withdraw passes pool guards, reverts in SAC with BalanceError = 10
let outcome = t.client().try_withdraw(&receiver, &false,
    &t.wdr(supplied, i128::MAX, 0));
assert!(outcome.is_err());
```

Sequence: (1) supplier deposits; (2) attacker calls `recapitalize(hub_asset, attacker, pool_balance)` with no tokens transferred in — the pool refunds "excess" to `payer` from its own balance; (3) pool balance = 0 while `cash` book ≥ deposits; (4) all subsequent withdrawals revert inside the SAC transfer — permanent freeze.