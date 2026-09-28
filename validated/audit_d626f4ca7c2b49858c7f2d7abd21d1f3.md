### Title
Pool `repay` pays an unearned "overpayment refund" out of shared custody, letting any caller drain supplier funds - (File: contracts/pool/src/ops/repay.rs)

### Summary
The pool's `repay` leg computes an `overpayment` purely from the *declared* `action.amount` versus the position's outstanding debt, then transfers that surplus back to the caller via `cache.transfer_out(payer, overpayment)`. The refund is not tied to any measured inbound transfer — it is paid out of the pool's real token custody. When the controller drives `repay`, it pre-funds the pool, so the refund is covered. But `repay` is callable directly on the pool contract with a `payer` argument, and on a market with zero debt the entire declared amount is classified as overpayment: `net_repay` is 0, no shares are burned, the cash book is untouched, and the full declared amount is paid to the caller out of suppliers' funds.

### Finding Description
In `contracts/pool/src/ops/repay.rs`, `accounting` resolves the repay into `(burned, overpayment)` via `cache.resolve_repay(amount, position)` and credits only `net_repay = amount - overpayment` to cash. `apply` then executes `outcome.cache.transfer_out(payer, outcome.overpayment)` unconditionally. With `borrowed == 0`, `resolve_repay` takes the full-close branch and returns `overpayment == amount`, so `net_repay == 0`. The `RepayRoundsToZeroShares` assertion passes on its `net_repay == 0` disjunct, `commit` leaves the book unchanged, and `transfer_out` moves `amount` tokens from the pool to the arbitrary `payer`.

The protocol's own test suite pins this behavior: `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` in `contracts/pool/tests/flows.rs` calls `client().repay(&payer, &ract(0, custody_before))` with **nothing transferred in** and asserts custody is drained by the full amount while `actual_amount == 0`. The external report's bug class (settlement trusting a declared amount instead of a measured inbound receipt) maps here as the mirror-image settlement hole: the refund leg trusts the declared `amount` rather than the balance delta of what was actually received. The same gap is documented for `ops/recapitalize::apply` (excess over the shortfall refunded without funding) in the same test file's comments.

### Impact Explanation
An unprivileged caller directly invokes `pool.repay(payer_self, [(hub_asset, pool_balance)])` on any market carrying no debt (or declares an amount exceeding their funded transfer on a market with small debt). The pool pays out up to its entire token balance to the caller while the cash book, supply shares, and borrow positions are unchanged. This is direct theft of supplier funds; iterating or repeating drains the pool to zero. If the pool enforces a controller-only check not visible in the indexed source, severity drops, but the dedicated harness test exercising exactly this path without any controller pre-funding indicates it is reachable.

### Likelihood Explanation
Reachable by any address in a single call: no position, collateral, oracle state, or timing is required — only a market with `borrowed == 0` (fresh or fully-repaid markets) and pool custody holding user deposits. The refund amount is bounded only by the caller's declared `amount` (clamped by `i128`), so the entire pool balance is extractable in one transaction.

### Recommendation
Refund only what was actually received: measure the pool's balance delta for the asset across the repay call (the same `transfer_amount_measured`/`balance_delta_since` pattern used elsewhere in `payments.rs`), and cap `overpayment` at `min(declared excess, measured_inbound)`. Alternatively, gate `repay`/`recapitalize` to the controller address, or require `cash` to have increased by at least `net_repay` before honoring `transfer_out`. Apply the same fix to `ops::recapitalize::apply`.

### Proof of Concept
Already encoded as `contracts/pool/tests/flows.rs:3590`:

```rust
// contracts/pool/tests/flows.rs — test_unfunded_repay_overpayment_refund_also_pays_out_of_custody
let t = TestSetup::new();
let token = token::Client::new(&t.env, &t.asset);
let payer = Address::generate(&t.env);

let custody_before = token.balance(&t.pool); // supplier funds, no debt
// Nothing transferred in, no debt to retire: the whole amount is "excess".
let credited = t.client()
    .repay(&payer, &t.ract(0, custody_before))
    .get_unchecked(0)
    .actual_amount;
assert_eq!(credited, 0);                       // book untouched
assert_unfunded_refund_drained_custody(&t, &payer, custody_before, &before);
// payer now holds the pool's entire token balance
```

Root cause lines: `contracts/pool/src/ops/repay.rs:32` (`transfer_out(payer, overpayment)` from custody) and `:44-52` (`resolve_repay` + `net_repay == 0` branch), with `repay` reachable per the pool client used in `flows.rs:3604-3608`.