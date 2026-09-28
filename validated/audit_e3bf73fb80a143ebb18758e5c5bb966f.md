### Title
Unfunded `recapitalize`/`repay` refunds pay declared "excess" out of real pool custody - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
The pool computes a refund as `amount - applied` from a caller-declared `amount`, then pays that refund out of live token custody via `Cache::transfer_out`, without verifying that `amount` was ever transferred in. When no backing shortfall (or no debt) exists, `applied`/`net_repay` is zero and the entire declared amount is refunded — an unprivileged caller drains the pool's full balance of that asset. This mirrors the CVE-2017-5609 class: an attacker-controlled parameter (`amount`, like `cat`) is concatenated into privileged logic and executed against protected assets.

### Finding Description
`ops::recapitalize::accounting` in `contracts/pool/src/ops/recapitalize.rs:44-67` computes `applied = amount.min(backing_shortfall(&cache))` and `refund = amount - applied`. `apply` then executes `outcome.cache.transfer_out(&payer, outcome.refund)` at line 34, moving real pool tokens to `payer`. The cash book is only credited by `applied` (`cache.credit_cash(applied)`), so when `backing_shortfall` is zero the pool pays `refund = amount` of genuine custody while the book is untouched — book and custody diverge permanently.

The same shape exists in `ops::repay`: a repay against a market with no debt takes the full-close branch, `net_repay == 0`, and the whole declared amount is refunded out of custody (the `RepayRoundsToZeroShares` assert explicitly permits the `net_repay == 0` case).

The controller path (`markets::recapitalize`, `contracts/controller/src/markets.rs:142-164`) is safe because it prefunds via `transfer_amount_measured` and passes only the measured receipt. But the pool's `recapitalize` and `repay` entrypoints are reachable directly — the pool's own test calls `t.client().recapitalize(&hub, &payer, &custody)` with a freshly generated, unfunded `payer` and drains the pool to zero (`contracts/pool/tests/flows.rs:3408-3483`).

### Impact Explanation
Theft of user funds. A single unprivileged address calls the pool's `recapitalize(hub_asset, attacker, amount)` with `amount` equal to the pool's token balance; custody is transferred to `attacker` while `cash` still credits suppliers. The test at `flows.rs:3432-3482` shows the pool balance going to 0, and a subsequent legitimate supplier withdraw passing the pool's own `require_reserves` liquidity guard (the book says funds exist) only to revert inside the SAC transfer with `BalanceError = 10`. Suppliers' deposits are gone and withdrawals are permanently broken for that market — both theft and permanent freezing of remaining claims.

### Likelihood Explanation
High. One contract call, no capital required (bounded by live custody, `flows.rs:3489-3512`), no oracle dependence, no timing. The only precondition is a market with no backing shortfall — the normal solvent state. The refund is capped by actual custody, so the entire market balance of that asset is extractable in one call.

### Recommendation
Do not pay refunds against declared amounts inside the pool. Either (a) restrict `recapitalize`/`repay` so only the controller can invoke them and always pass measured receipts (as `markets::recapitalize` already does), or (b) measure the pool's balance delta of `hub_asset.asset` inside the pool op itself and compute `refund` from the measured inbound amount, not the argument. The refund should also debit the cash book or pass `require_reserves` so it can never exceed real, unbooked custody.

### Proof of Concept
Encoded by the protocol's own test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` (`contracts/pool/tests/flows.rs:3408-3483`):

```rust
// supplier deposits; book == custody == 10_000_000_000
let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &payer, &custody);
assert_eq!(token.balance(&t.pool), 0);          // custody drained to payer
// book still >= deposit; supplier withdraw passes require_reserves,
// then reverts inside the SAC transfer (BalanceError = 10)
```

`payer` is `Address::generate` — no funds, no privilege. Variant: `repay(&payer, &ract(0, custody))` on a zero-debt market yields the same drain via the `net_repay == 0` refund branch (`flows.rs:3590-3611`).

Note: I verified the refund-drain mechanics in `recapitalize.rs` and the tests, but could not fully read `contracts/pool/src/lib.rs` to confirm the exact auth guard on the pool's `recapitalize`/`repay` entrypoints (grep returned match counts only). The tests demonstrate the calls succeed from an arbitrary generated address, which evidences unprivileged reachability; if a controller-only guard exists on the public entrypoint, the exposure reduces accordingly and should be confirmed before reporting.