### Title
Pool `repay` refunds a declared-but-never-received amount out of real token custody — (File: contracts/pool/src/ops/repay.rs)

### Summary
`ops::repay` trusts the caller-supplied `action.amount` as if the pool had already received it. When the declared amount exceeds the position's outstanding debt, `resolve_repay` classifies the difference as `overpayment` and `apply` pays it back to the payer with `cache.transfer_out(payer, overpayment)` — a real token transfer out of pool custody. Because the pool never verifies that `amount` tokens were actually transferred in, any unprivileged address can call `repay` directly on a market with little or no debt and withdraw the entire declared amount from supplier funds. This mirrors the advisory's class: a verification/settlement routine accepts the declared structure without enforcing that the required real input exists.

### Finding Description
`contracts/pool/src/ops/repay.rs:40-67` (`accounting`) resolves `action.amount` into `(burned, overpayment)` purely from book state — `current_debt_ceil` for the passed-in position — with no measurement of the pool's token balance. `contracts/pool/src/ops/repay.rs:25-34` (`apply`) then executes `outcome.cache.transfer_out(payer, outcome.overpayment)`, moving real tokens. In the intended flow the controller performs a measured transfer into the pool before calling `repay`, but the pool itself performs no inbound-balance check and the `repay` entrypoint is callable directly (the test harness invokes `client.repay(&payer, &t.ract(0, custody_before))` with no prior transfer).

When the market carries no debt for the position, `resolve_repay` returns the full amount as overpayment; `net_repay == 0` passes the `RepayRoundsToZeroShares` assert via its `net_repay == 0` disjunct, `credit_cash(0)` changes nothing, and the entire declared sum is paid out of custody. The existing regression test `test_unfunded_repay_overpayment_refund_also_pays_out_of_custody` (`contracts/pool/tests/flows.rs:3590-3611`) demonstrates exactly this: `assert_unfunded_refund_drained_custody` confirms book `cash` stays in sync while real token custody decreases. The same gap exists in `ops::recapitalize` (`contracts/pool/src/ops/recapitalize.rs:26-67`), which refunds `amount - applied` to the payer without verifying receipt.

### Impact Explanation
Theft of user funds. An attacker calls the pool's `repay` entrypoint with a `PoolAction` carrying a zero-debt `scaled_position` and `amount` equal to the pool's token balance. The pool treats the whole amount as overpayment and transfers it out of supplier liquidity to the attacker. No collateral, debt, or prior deposit is required. Repeating across markets drains each pool's cash.

### Likelihood Explanation
Fully unprivileged and self-contained: the attacker supplies only the `repay` call arguments — a `PoolAction` with a zero scaled position and a large `amount`. No price manipulation, timing, or privileged role is needed; a market with zero debt on the passed position maximizes the refund. The only prerequisite is a pool holding token custody, which any supplied market satisfies.

### Recommendation
Verify receipt before refunding. Either restrict `repay`/`recapitalize` to the controller and snapshot the pool balance before/after the inbound transfer (measuring actual received amount, as `transfer_amount_measured` does), or compute `overpayment`/`refund` against the measured pool balance delta rather than the declared `amount`. At minimum, assert `token.balance(pool) >= cash + received` before any `transfer_out` of the refund, and skip the refund transfer entirely when nothing was received.

### Proof of Concept
Adapted from the existing failing-invariant test in `contracts/pool/tests/flows.rs`:

```rust
let t = TestSetup::new();
let token = token::Client::new(&t.env, &t.asset);
let payer = Address::generate(&t.env); // attacker, no deposits

t.client().supply(&t.sup(0, 10_000_000_000i128)); // supplier funds custody
let custody = token.balance(&t.pool);

// No tokens transferred in; market has no debt for this position.
let credited = t
    .client()
    .repay(&payer, &t.ract(0, custody))
    .get_unchecked(0)
    .actual_amount;

assert_eq!(credited, 0);                     // no debt retired
assert_eq!(token.balance(&t.pool), 0);       // custody drained to attacker
assert_eq!(token.balance(&payer), custody);
```

Note: I could not fully confirm within the available iterations whether the pool's `repay` entrypoint applies an auth check restricting it to the controller address; if such a gate exists, the reachable surface narrows to the controller paths, but the pool still performs no receipt verification and relies entirely on the caller ordering transfers correctly.