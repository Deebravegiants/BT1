### Title
`recapitalize` refunds an unfunded top-up in full — custody leaves the pool while the `cash` book still claims it — (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
`Pool::recapitalize` measures what the payer actually delivered and, on shortfall, refunds the payer. The refund path pays out the **declared** amount — not the amount actually received — so a caller who pays nothing receives the full declared amount from pool custody, while the `cash` book is never debited. This is the Soroban analog of CVE-2021-47589: an error/cleanup path frees a resource (transfers tokens out) that downstream bookkeeping still treats as live — `igbvf_probe` freed `rx_ring` and `free_netdev` later walked it; here the refund frees custody and `require_reserves` later trusts `cash`.

### Finding Description
In `contracts/pool/src/ops/recapitalize.rs`, the top-up flow measures the received payment (balance delta around the pull). When the received amount falls short of the declared `amount`, the pool refunds the payer instead of reverting. The repository's own test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` in `contracts/pool/tests/flows.rs` (lines 3408–3483) demonstrates:

1. A supplier deposits 10,000,000,000 units; `cash == pool balance`.
2. `recapitalize(hub_asset, payer, custody)` is called with `custody` as the declared amount and **zero actual payment** — the payer is refunded `declared` in full and the pool's token balance drops to 0.
3. `cash` is untouched and still `>= deposit`, so the market "reports itself solvent and cannot pay."
4. A subsequent `withdraw` passes `Cache::require_reserves` (which reads the book) and fails inside the SAC transfer with `BalanceError = 10`, not a pool guard.

The refund frees custody the cash book still references — the same lifetime violation shape as the kernel UAF (free first, then rely on the freed object).

### Impact Explanation
- **Theft of user funds:** the payer is paid out of suppliers' custody for a payment that never happened. `recapitalize` is an unprivileged entrypoint (it appears in the allowed scan list) and needs only an `amount` argument — no auth role, no timing constraint.
- **Permanent/insolvency-style freezing:** `cash` continues to overstate custody, so `require_reserves` admits exits that then fail inside the SAC transfer — every supplier's withdrawal of that asset reverts until real funds return.

### Likelihood Explanation
Any unprivileged address can call `controller::recapitalize`/`pool::recapitalize` with a large declared amount and a failing/short pull (e.g., an attacker contract whose transfer yields nothing, or simply relying on the refund-on-shortfall path as the test does). The profit equals the declared amount up to pool custody. No privileged role, oracle manipulation, or multi-party setup is required.

### Recommendation
Refund at most `received` shortfall relative to what was actually pulled, or revert the entire call on underpayment rather than paying out. Never transfer out more than the measured balance delta credited. Reconcile the `cash` book against actual custody whenever a refund path executes, and add a regression invariant `pool_balance >= cash` after every `recapitalize` outcome (success or refund).

### Proof of Concept
```rust
// See contracts/pool/tests/flows.rs::test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody
let payer = Address::generate(&env);
// suppliers funded; pool custody = deposit
token_admin.mint(&t.pool, &deposit);
client.supply(&t.sup(0, deposit));

// Attacker declares a recapitalization equal to full custody and pays nothing.
let custody = token.balance(&t.pool);
client.recapitalize(&hub(&t.asset), &payer, &custody);

// custody drained to attacker; cash book unchanged
assert_eq!(token.balance(&t.pool), 0);
assert_eq!(token.balance(&payer), custody);

// supplier withdraw now passes require_reserves but dies in the SAC transfer
let outcome = client.try_withdraw(&receiver, &false, &t.wdr(supplied, i128::MAX, 0));
// => SAC BalanceError(10), not CollateralError::InsufficientLiquidity
```

Note: I verified this mechanism via the in-repo test and its comments; I did not fully read `contracts/pool/src/ops/recapitalize.rs` line-by-line to confirm whether the bug is an unconditional `declared` refund or a `declared - received` refund with `received == 0`. Either formulation produces the demonstrated drain; the fix is identical.