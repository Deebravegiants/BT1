### Title
`recapitalize` refunds the unapplied surplus unconditionally, letting an unprivileged caller drain pool custody while the cash book still reports solvency - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
The external report's class — a refund path that pays out without regard to the protocol's settled state, leaving claims unfunded — maps directly onto `LiquidityPool::recapitalize`. The pool computes `refund = amount - applied` purely from the *declared* `amount` and the backing shortfall, then unconditionally transfers `refund` to `payer` — without ever measuring how many tokens the caller actually delivered. On a solvent market (shortfall = 0), `applied = 0` and the *entire declared amount is refunded out of the pool's own custody*.

### Finding Description
`accounting` in `contracts/pool/src/ops/recapitalize.rs` computes:

- `applied = amount.min(guards::backing_shortfall(&cache))` (line 52)
- `refund = amount - applied` (lines 53-55)
- `cache.credit_cash(applied)` — only `applied` is booked (line 57)

Then `apply` calls `outcome.cache.transfer_out(&payer, outcome.refund)` (line 34). No balance-delta measurement of the payer's actual transfer occurs anywhere in the pool; the refund is honored against the *declared* `amount`. `recapitalize` is documented as an open (unauthenticated) endpoint (docs/reference/endpoints.md:40).

Like the OpenQ bug — where `refundDeposit` ignored `status` and let depositors pull funds needed for claims — this refund ignores whether the funds being "returned" were ever deposited. An attacker calls `pool.recapitalize(hub_asset, attacker, pool_token_balance)` on a market with zero backing shortfall; the pool pays the attacker its full token balance while `cash` is unchanged. `Cache::require_reserves` reads the `cash` book, not custody, so the market still reports itself solvent; subsequent supplier `withdraw`s pass the liquidity gate and then revert inside the SAC transfer for insufficient balance.

The repository's own test proves this end-to-end: `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` in `contracts/pool/tests/flows.rs:3408-3483` mints custody to the pool, calls `recapitalize` with a payer that never funded anything, observes `token.balance(pool) == 0` with `cash` still ≥ the deposit, and shows a supplier withdraw failing with the SAC balance error rather than any pool guard.

### Impact Explanation
Theft of user funds plus protocol insolvency. A single unprivileged call drains the market's entire token custody to the attacker. The `cash` book is untouched, so supply shares continue to claim the drained funds; honest suppliers' withdrawals revert, permanently freezing their deposits unless the pool is recapitalized externally.

### Likelihood Explanation
Fully deterministic and atomic: the attacker only needs a market whose `backing_shortfall` is zero (the normal, healthy state) and an `amount` equal to the pool's token balance (publicly readable). No oracle manipulation, no privileged role, no timing dependency. One caveat I could not fully verify in the available index: whether `LiquidityPool::recapitalize` additionally enforces a controller-only caller check in `lib.rs`. The committed test invokes it directly on the pool client with no controller auth, indicating the endpoint itself is callable; even if the controller is a mandatory intermediary, the same unmeasured-refund flaw would apply if the controller forwards a declared amount rather than a measured receipt.

### Recommendation
Measure receipts instead of trusting the declaration: snapshot the pool's token balance before accepting the payer's transfer (or have the controller pull funds first and pass the measured delta), set `applied = min(measured_received, backing_shortfall)`, and refund only `measured_received - applied`. Additionally, gate `transfer_out(refund)` so a refund can never exceed tokens actually received in the same transaction, and consider an invariant check that post-call `cash` cannot exceed actual custody attributable to the injection.

### Proof of Concept
```rust
// Solvent market: backing_shortfall == 0, so applied == 0 and
// refund == declared amount — paid from pool custody to an unfunded payer.
let t = TestSetup::new();
let token = token::Client::new(&t.env, &t.asset);
let token_admin = token::StellarAssetClient::new(&t.env, &t.asset);
let attacker = Address::generate(&t.env);

// Seed real supplier custody (what the controller would have done).
token_admin.mint(&t.pool, &10_000_000_000i128);
t.client().supply(&t.sup(0, 10_000_000_000));

let custody = token.balance(&t.pool);
// Attacker never transfers a single token; refund still pays out.
t.client().recapitalize(&hub(&t.asset), &attacker, &custody);

assert_eq!(token.balance(&t.pool), 0);          // custody stolen
assert_eq!(token.balance(&attacker), custody); // attacker's "refund"
assert!(t.state_snapshot().cash > 0);          // book still claims solvency
// Supplier withdraw now passes require_reserves (cash book unchanged)
// and reverts inside the SAC transfer — funds are gone.
```