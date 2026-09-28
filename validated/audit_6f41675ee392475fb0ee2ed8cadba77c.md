### Title
Unfunded repay overpayment refund drains pool custody — refund computed from declared amount, not measured receipt - (File: contracts/pool/src/ops/repay.rs)

### Summary
The pool's `repay` leg refunds the "overpayment" — the portion of the declared `amount` exceeding outstanding debt — directly to the caller via `transfer_out`, without verifying that any tokens were actually transferred in. When a market carries no debt, the entire declared amount is treated as overpayment, letting an unprivileged caller name any `payer`, declare an arbitrary amount, and walk away with real pool custody. This mirrors the report's bug class: an invalid free of a pointer that was never allocated — here, releasing funds that were never received.

### Finding Description
`ops::repay::accounting` resolves `action.amount` against the caller-supplied scaled debt position via `cache.resolve_repay(amount, position)`. With zero debt, `current_debt_ceil` is zero, `resolve_repay` takes the full-close branch, and returns `overpayment == amount`. The `RepayRoundsToZeroShares` assert passes because `net_repay == 0` is an allowed disjunct (`contracts/pool/src/ops/repay.rs:44-52`). `apply` then calls `outcome.cache.transfer_out(payer, outcome.overpayment)` (`repay.rs:32`), paying the refund out of real token custody. The refund never debits the `cash` book and never passes a reserves check — only `net_repay` is credited to cash (`repay.rs:57`).

The pool trusts caller-provided inputs by design (INV-ACCT-10: the pool has no per-account book and trusts the scaled position in each call), but it also never measures the inbound balance delta for this leg. The in-repo test `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` (`contracts/pool/tests/flows.rs:3589-3611`) demonstrates exactly this: calling `repay` with `custody_before` as the declared amount and nothing transferred in credits `0` while `assert_unfunded_refund_drained_custody` confirms custody dropped by the full amount. The same refund pattern exists in `ops::recapitalize::apply` (excess over the shortfall), noted in the test's doc comment at `flows.rs:3578-3582`.

### Impact Explanation
Theft of user funds / protocol insolvency. Every supplier's deposit sits in the pool's token custody; the refund pays out of that custody while leaving the `cash`/`supplied`/`borrowed` book untouched, so the accounting layer cannot see the loss. A single call can extract up to the pool's entire token balance by declaring `amount = pool_balance`. Suppliers' claims then exceed actual holdings — permanent loss and insolvency, not merely a temporary freeze.

### Likelihood Explanation
The path is reachable by a single unprivileged address: the pool `repay` entrypoint takes `(payer, action)` and the test invokes it directly through the pool client with a freshly generated address and no prior transfer. No debt, no position, no timing, and no privileged role is required — only a market that exists, and markets always exist for listed assets. `amount` is attacker-chosen `i128`, so one call drains the full balance. Cost to the attacker is effectively zero; even transaction revert risk is absent since the happy path succeeds.

### Recommendation
Derive the refund from measured inbound value, not the declared `amount`:
- Measure the pool's token balance delta around the leg (snapshot before, compare after the controller's inbound transfer), or require the caller to pass a proven receipt; refund only `min(declared_overpayment, measured_inbound)`.
- Alternatively, make `repay` revert or cap `overpayment` at the amount actually credited: `overpayment <= amount` is insufficient; the bound must be on received funds.
- Apply the same fix to `ops::recapitalize::apply`, which shares the declared-amount refund shape.
- Optionally debit the refund against the `cash` book and enforce `require_reserves` so any residual leakage fails a solvency assertion instead of silently draining custody.

### Proof of Concept
Already exercised by the repository's own test (`contracts/pool/tests/flows.rs:3590`):

```rust
// Market carries no debt; payer has transferred nothing.
let custody_before = token.balance(&t.pool); // == cash book, book/custody in sync

// Unprivileged direct pool call; declared amount == full pool balance.
let credited = t.client()
    .repay(&payer, &t.ract(0, custody_before))
    .get_unchecked(0)
    .actual_amount;

assert_eq!(credited, 0);          // no debt retired, nothing credited
// assert_unfunded_refund_drained_custody confirms:
//   payer's balance increased by custody_before and pool custody dropped
//   by the same amount, with the cash/supplied/borrowed book unchanged.
```

Mechanics: `resolve_repay(amount, position=0)` returns `(burned=0, overpayment=amount)`; `net_repay = 0` satisfies the zero-shares assert; `credit_cash(0)` leaves the book intact; `transfer_out(payer, overpayment)` moves real tokens out of the pool contract. Repeating once with `amount` equal to the pool's entire token balance drains it fully.

One caveat I could not fully verify within the iteration limit: whether the pool's `repay` entrypoint applies an auth gate on `payer` in `contracts/pool/src/lib.rs`. The unit test calls `client().repay` with a generated address and no signing mock, which strongly implies no `require_auth` on that path, and even if `payer.require_auth()` existed, an attacker calls it for themselves — the drain is unchanged.