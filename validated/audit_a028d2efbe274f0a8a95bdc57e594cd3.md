### Title
Pool `recapitalize` refunds unfunded amounts out of supplier custody — unprivileged drain of the cash book - (File: contracts/pool/src/ops/recapitalize.rs)

### Summary
The kernel bug allocates a resource (`mpol_dup`) and returns early without releasing it (`mpol_put`), letting any user leak it. The analog in the pool: `recapitalize::apply` commits a cash credit and then pays out the un-applied "refund" to the caller, without ever verifying that the caller actually transferred `amount` into the pool. On a market with no backing shortfall, `applied = 0` and `refund = amount`, so any unprivileged address can pull real supplier funds out of the pool simply by naming an `amount`. The refund leg is the "release" that was never conditioned on the corresponding deposit — funds allocated to the book's custody are released to the caller with no matching input.

### Finding Description
`accounting` in `contracts/pool/src/ops/recapitalize.rs:44-67` computes `applied = amount.min(backing_shortfall(&cache))`, commits `credit_cash(applied)` at lines 57-58, and returns `refund = amount - applied`. `apply` at lines 32-36 then calls `outcome.cache.transfer_out(&payer, outcome.refund)` — a real token transfer to the caller — with the doc comment "The controller transfers `amount` into the pool before this call" (line 4) being a trust assumption, not an enforced check. Unlike the flash paths, there is no measured-receipt settlement: nothing reads the pool's actual token balance before/after, so a direct call with no prior deposit is indistinguishable from a funded one. When the market is healthy (shortfall 0), `applied` is 0 and the full `amount` is refunded out of existing custody. The repository's own regression test `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` in `contracts/pool/tests/flows.rs:3408-3433` demonstrates exactly this: a caller invokes `recapitalize` with `amount = pool balance`, walks away with every token, and the cash book still reports the funds as present.

### Impact Explanation
Theft of user funds, reachable by a single unprivileged address. After the drain, `cash` on the book still claims the deposits are backed (`flows.rs:3435-3439`), so withdrawals pass the pool's own liquidity guards and then fail inside the SAC transfer (`flows.rs:3441-3477`) — honest suppliers' exits revert while the attacker holds the tokens. This is both direct theft and a permanent book/custody divergence that makes the market unpayable.

### Likelihood Explanation
Certain and trivially repeatable whenever a market has a shortfall smaller than custody — including the common case of zero shortfall. The entrypoint takes `(hub_asset, payer, amount)`; the caller controls `payer` (recipient of the refund) and `amount` (capped only by pool custody). No privilege, timing, price manipulation, or multi-transaction setup is required. The only uncertainty is whether the deployed pool entrypoint gates `recapitalize` to the controller; the test suite calls it directly on the pool client with a generated `payer`, indicating it is externally reachable.

### Recommendation
Measure the receipt instead of trusting it: record the pool's token balance before crediting, require the post-call balance to be at least `before + applied`, or take `amount` as the actual measured delta like other settlement paths. Alternatively, gate `recapitalize` (and any refund-emitting op) to the controller, and have the controller pull the tokens via `transfer_from` before invoking the pool. At minimum, cap `refund` at the amount actually observed arriving in custody during the call.

### Proof of Concept
```rust
// From contracts/pool/tests/flows.rs:3408-3433 — already pinned in-tree.
let token = token::Client::new(&t.env, &t.asset);
let token_admin = token::StellarAssetClient::new(&t.env, &t.asset);
let payer = Address::generate(&t.env);          // unprivileged, zero balance

token_admin.mint(&t.pool, &10_000_000_000i128); // suppliers' real custody
t.client().supply(&t.sup(0, 10_000_000_000));   // market is healthy: shortfall == 0

let custody = token.balance(&t.pool);
t.client().recapitalize(&hub(&t.asset), &payer, &custody);
// applied = min(custody, 0) = 0; refund = custody
assert_eq!(token.balance(&t.pool), 0);          // drained to `payer`
assert!(t.state_snapshot().cash >= 10_000_000_000); // book still claims solvency
// A supplier withdraw now passes require_reserves but fails in the SAC
// transfer (BalanceError #10) — funds are gone.
```