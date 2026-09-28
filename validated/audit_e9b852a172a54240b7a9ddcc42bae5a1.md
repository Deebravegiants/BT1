### Title
Tokens transferred directly to the pool are permanently stranded — no crediting or recovery path exists - (File: contracts/pool/src/lib.rs)

### Summary
The DODO finding class — value attached to a call that is neither used nor refunded — maps onto XOXNO Lending's custody model as unsolicited token transfers to the pool contract. The pool's entire entrypoint surface (`supply`, `borrow`, `withdraw`, `repay`, `net_settle`, `seize_positions`, `claim_revenue`, `recapitalize`, `flash_loan`, `create_strategy`) is owner-gated to the controller and every inbound leg is pre-funded by the controller before the call; there is no sweep, rescue, or donation-crediting entrypoint. Any token an unprivileged address pushes directly to the pool via `token.transfer` belongs to no market's `cash` book and can never be withdrawn.

### Finding Description
The pool tracks liquidity in a bookkeeping variable `state.cash` per `(hub_id, asset)` market, while all markets of a token (across hubs) share one physical token balance. Inbound entrypoints only credit `cash`; they never reconcile it against `token.balance(pool)`:

- `supply` / `repay` / `recapitalize` credit `cash` on the controller's word — "Tokens arrived before any cash-crediting call" is listed as an upstream guarantee, not something the pool verifies (contracts/pool/README.md).
- `flash_loan` is the only function that reads `token.balance(pool)`, and it uses the live balance (donation included) as the baseline `pre_balance` in `terms()` (`contracts/pool/src/ops/flash.rs:107-121`), then asserts deltas via `require_balance` (`contracts/pool/src/ops/flash.rs:183-188`). So stray balances do not break flash loans — they are simply absorbed into the expected balances and remain untracked.

The test `pool_all_money_paths_preserve_books_and_shared_token_custody` proves the behavior: after `token.transfer(payer, pool, 7 * UNIT)`, every market's `cash` is unchanged and `token.balance(pool) == cash_market1 + cash_market2 + donation` — the donation "belongs to no market's cash book" (`tests/test-harness/tests/pool_money_flow_audit.rs:86-96`). No code path ever consumes the surplus: `claim_revenue` pays out only booked revenue shares, `withdraw`/`borrow` debit `cash`, and there is no `sweep`/`rescue` function on the pool (the only sweep is `sweep_balance` on the swap-aggregator, a different contract). The same applies to Aquarius venue rewards that anyone can permissionlessly push to the pool for LP-collateral markets — they arrive as unbooked donations (docs/explanation/threat-model.md).

### Impact Explanation
Permanent freezing of funds. Tokens sent to the pool outside the controller's payment path — user error, front-end bugs, misconfigured integrators, or permissionlessly pushed venue rewards — are locked in the contract forever. Unlike the original DODO case where ETH sat unused, here the loss is total and unrecoverable by design: no privileged or unprivileged entrypoint can release the surplus. For LP-collateral markets this also constitutes freezing of unclaimed yield, since reward tokens pushed by any third party become unbooked pool balance that neither suppliers nor the protocol can claim.

### Likelihood Explanation
Low-to-medium frequency, identical to the source finding: it requires an out-of-band direct transfer rather than a protocol call (the controller's `supply`/`repay`/`recapitalize` pull exact amounts via `transfer_amount_measured`, so no in-protocol overpayment is possible). However the venue-reward vector requires no user error at all — any caller can push accrued Aquarius rewards into the pool for LP-token markets, and gauge/other rewards already accrue to an address that cannot claim them, so the strand grows autonomously over time.

### Recommendation
Add an owner-gated `sweep(hub_asset, token, amount)`-style entrypoint (or a controller-mediated route) that releases `token.balance(pool) − Σ cash(across all hubs of that token)` to a treasury address, or alternatively book pushed donations into protocol revenue via `seize_positions`-style accounting so suppliers/revenue claim them. At minimum, expose a view reporting `balance − total_cash` so operators can detect stranded funds.

### Proof of Concept
```rust
// Any unprivileged address; pool has no entrypoint that can release these funds.
let pool = /* LiquidityPool contract address */;
token::Client::new(&env, &usdc).transfer(&alice, &pool, &1_000_000_000);
// Every market's state.cash is unchanged; balance(pool) - Σ cash = donation forever.
// Confirmed by tests/test-harness/tests/pool_money_flow_audit.rs lines 86-96:
// "An unsolicited donation belongs to no market's cash book."
```