### Title
Tokens transferred directly to the Liquidity Pool or Controller are permanently locked — no sweep or recovery path exists - (contracts/pool/src/lib.rs)

### Summary
The bug class from the reference report — "funds held by the contract can never be withdrawn because the only payout path is tied to a different accounting unit" — maps onto XOXNO Lending as a stranded-balance issue. In the pool, every payout (`withdraw`, `borrow`, `claim_revenue`, `flash_loan`, `recapitalize` refund) is bounded by the `cash` accounting book, not by the actual token balance. Tokens pushed into the pool or controller by a direct `token::transfer` inflate the real balance but are never credited to `cash`, `supplied`, or `revenue`, and no sweep/rescue entrypoint exists in either contract to recover them.

### Finding Description
The pool's docs state: "Cash is an accounting book, separate from the token balance" (`contracts/pool/src/lib.rs:34`). All mutators are `#[only_owner]` (the controller), and the complete entrypoint surface (`contracts/pool/src/lib.rs:99-252`) contains no function that pays out `token_balance - cash`. Concretely:

- `withdraw` pays out only up to the recorded `cash` book; the test asserts `tok.balance(&contract) == state.cash` after payout (`contracts/pool/tests/withdraw.rs:194-196`), so surplus balance is never touched.
- `recapitalize` credits `min(amount, backing_shortfall)` to cash and *refunds the rest* (`contracts/pool/src/ops/recapitalize.rs:52-57`), so it cannot be used to claim or recover a pre-existing stray balance — the applied part is booked as a donation to cover the shortfall, and a stray donation does not change the shortfall-vs-cash relationship in a way that releases it.
- `claim_revenue` pays `min(cash, revenue)` — strictly the revenue share book (`contracts/pool/src/lib.rs:243-252`).
- `flash_loan` measures the token balance only to enforce repayment; it does not disburse surplus (`contracts/pool/src/lib.rs:196-210`).
- The controller has no sweep either; strategy paths (multiply, flash_position) measure balance *deltas* across the call, so pre-existing stray tokens on the controller are invisible to them and remain parked.
- The SDK docs themselves acknowledge the hazard: "never sets `to` to the pool or controller address … and would strand tokens" (`skills/evals/scenarios/xoxno-lending-contracts/07-unwind-repay-withdraw-all.json:10`). That specific route reverts, but a plain `token.transfer(user -> pool)` or `token.transfer(user -> controller)` does not.

Any holder can execute `token.transfer(their_address, pool_address, amount)` — explicitly in the allowed action set — and those tokens become permanently unrecoverable: not by the sender, not by other users, and not even by the owner/controller, since no entrypoint transfers out non-booked balance.

### Impact Explanation
Permanent freezing of funds. Unlike the reference case where a rescue could be patched in, here the pooled "dust" accumulates in the real token balance while every accounting view (`get_reserves`, `get_sync_data.cash`, supply index math) ignores it. There is no privileged escape hatch either — the owner is the controller contract, which exposes no sweep — so the freeze is absolute under the deployed code.

### Likelihood Explanation
Requires a mistaken or forced direct transfer rather than an exploit. Classic Stellar users routinely send to contract addresses by accident, and SAC `transfer` to the pool/controller cannot be blocked by the receiving contract. Individually low-probability, non-zero over the contract lifetime; severity is bounded to Medium because the loss is self-inflicted and there is no mechanism for one user to strand another's funds.

### Recommendation
Add an owner-gated `sweep(asset, to, amount)` on the pool that transfers out `min(amount, token_balance - cash_headroom)` — i.e., only the surplus above booked cash (plus any unclaimed revenue already inside `cash`), so it can never touch user backing. For the controller, a governance-only recovery entrypoint achieves the same. Alternatively, document and accept the loss, but the current state has no recourse at all.

### Proof of Concept
```rust
// Any unprivileged user pushes tokens straight into the pool.
let token = token::Client::new(&env, &asset);
token::StellarAssetClient::new(&env, &asset).mint(&user, &1_000_000_000);
token.transfer(&user, &pool, &1_000_000_000);   // succeeds — SAC transfer

// Pool state is unchanged: cash/supplied/revenue do not reflect the donation.
let state = pool_client.get_sync_data(&hub(&asset)).state;
// token.balance(pool) == state.cash + 1_000_000_000

// No reachable entrypoint releases the surplus:
//  - withdraw pays only up to `cash` (share-burn bounded);
//  - recapitalize(user, amount) refunds amount - min(amount, backing_shortfall),
//    and backing_shortfall does not grow because cash/balance accounting is unchanged;
//  - claim_revenue pays min(cash, revenue), unaffected;
//  - no sweep/rescue/recover function exists in LiquidityPoolInterface
//    (contracts/pool/src/lib.rs) or the controller.
// The 1_000_000_000 is permanently locked.
```

Caveat: I could not exhaustively verify every controller-side token holding path (e.g., whether any strategy entrypoint opportunistically absorbs a pre-existing balance rather than measuring deltas). If any strategy does measure absolute balance rather than a delta, the finding would upgrade from freezing to theft, since the next unprivileged caller could capture the stray tokens.