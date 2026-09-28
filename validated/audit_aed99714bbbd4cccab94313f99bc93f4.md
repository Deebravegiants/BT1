### Title
`recapitalize` pays an unfunded refund of the declared excess from existing pool custody — ([File: contracts/pool/src/ops/recapitalize.rs])

### Summary
`pool::recapitalize` computes `refund = amount - applied` from the **declared** `amount` parameter and transfers it to `payer` unconditionally via `Cache::transfer_out`, without verifying that `amount` was actually received. `applied` is capped at `backing_shortfall`, so on a market with no (or small) shortfall almost the entire declared amount is refunded out of pre-existing reserves. The permissionless `controller::recapitalize` entrypoint reaches this code, letting an unprivileged payer declare an amount larger than what it actually funded and walk away with other suppliers' tokens.

### Finding Description
In `contracts/pool/src/ops/recapitalize.rs`, `accounting` caps the credit at the backing shortfall:

```rust
let applied = amount.min(guards::backing_shortfall(&cache));
let refund = amount.checked_sub(applied)...;
```

`apply` then pays `outcome.cache.transfer_out(&payer, outcome.refund)` — a raw token transfer of pool custody (`contracts/pool/src/cache/cash.rs:46-52`), which "does not adjust accounting cash". The pool never measures a balance delta; it trusts the caller's claim that `amount` was transferred in. The in-repo test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` (`contracts/pool/tests/flows.rs:3407-3483`) demonstrates this exactly: calling `recapitalize` with a declared `amount` equal to the pool's whole balance and **zero tokens paid in** leaves `token.balance(&t.pool) == 0`, pays the payer `declared` in full, and leaves `cash` untouched so the book still reports the drained funds as present. `recapitalize` is declared caller-auth in `scripts/permissionless_entrypoints.txt:73`, so an unprivileged address can nominate itself as `payer`. Whenever the shortfall does not cover the declared amount, the excess refund is drawn from honest suppliers' reserves rather than from what the payer deposited.

### Impact Explanation
Theft of user funds / protocol insolvency. Each call moves `amount − min(amount, shortfall)` of real custody to an arbitrary payer; repeated calls, or one call with `amount` equal to total reserves on a healthy market (shortfall = 0 → `refund = amount`), drain the pool's entire token balance while the `cash` book is unchanged. Subsequent supplier withdrawals then fail inside the SAC transfer (balance error 10), as the test proves — permanent freezing of remaining funds and instant insolvency.

### Likelihood Explanation
Single unprivileged transaction through `controller::recapitalize`; no oracle manipulation, no health-factor precondition, no liquidity precondition. The only requirement is that the declared amount exceed the market's backing shortfall — which is trivially satisfied on any solvent market, where the shortfall is zero and the full declared amount is refunded.

### Recommendation
Bind the refund to the measured receipt: read the pool token balance before and after the inbound transfer (as `repay`/`supply` measured-receipt paths do via `transfer_amount_measured`), cap `refund` at the actual balance increase, and prefer pulling `amount` into the pool inside the same call rather than relying on a prior transfer. At minimum, assert `token.balance(pool) - cash >= refund` before `transfer_out`.

### Proof of Concept
Adapted from `contracts/pool/tests/flows.rs:3407-3440`:

1. Supplier deposits `10_000_000_000` units; `cash == balance == deposit`.
2. Attacker calls `recapitalize(hub_asset, payer=attacker, amount=pool_balance)` without funding the pool (or with a receipt smaller than declared).
3. `applied = min(amount, 0 shortfall) = 0` on a solvent market; `refund = amount`; `transfer_out` sends the entire custody to the attacker. `token.balance(pool) == 0`, `cash` still `>= deposit`.
4. Supplier calls `withdraw(supplied)` — passes `require_reserves` (book is stale), reverts inside the SAC `transfer` with `BalanceError = 10`. Custody is gone and the book insists it isn't.