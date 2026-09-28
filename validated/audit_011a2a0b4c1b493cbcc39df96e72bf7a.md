### Title
Tokens sent directly to the Pool outside of a book-crediting operation are permanently trapped — ([File: contracts/pool/src/ops/repay.rs, contracts/pool/src/cache/cash.rs])

### Summary
The XOXNO Lending pool holds one physical token balance per asset while accounting is kept in per-(hub, asset) `cash` books. Every protocol entrypoint that moves tokens in either pulls an exact amount (`transfer_from` with a measured receipt) or refunds the surplus (`repay` overpayment, `recapitalize` refund). A user who transfers tokens directly to the pool address — the Soroban analog of over-funding `msg.value` — creates a balance that belongs to no market's cash book, and no code path can ever pay it out. The funds are permanently frozen.

### Finding Description
The pool's accounting is strictly book-driven:

- `repay` resolves the offered amount into burned debt shares plus an `overpayment`, credits only the net repay to cash, and transfers the surplus back to the payer — excess input is explicitly returned rather than trapped: `contracts/pool/src/ops/repay.rs:30-34,44-47`.
- `recapitalize` applies `min(amount, backing_shortfall)` to cash and refunds the remainder to the payer: `contracts/pool/src/ops/recapitalize.rs:52-55`, then `transfer_out(&payer, refund)` at line 34.
- Liquidation and strategy repay legs use `transfer_amount_measured` plus `refund_controller_balance_delta`, which refunds the measured controller balance increase to the caller: `contracts/controller/src/payments.rs:41-52`.

A raw `token.transfer(user, pool, amount)` bypasses all of this: no `PoolAction` is processed, no book is credited, and the token balance simply rises above the sum of all markets' `cash`. This is confirmed by the money-flow test, which mints and transfers `7 * UNIT` to the pool and asserts it "belongs to no market's cash book" — the pool balance equals `state.cash + other.cash + 7 * UNIT` forever: `contracts/test-harness/tests/pool_money_flow_audit.rs:86-96`.

Every payout (`transfer_out` in `borrow`, `withdraw`, `repay` refunds, `recapitalize` refunds, flash principal, revenue claim) is bounded by a book mutation; there is no skim/recover/sweep function in `contracts/pool/src` (grep for `skim|recover|sweep|rescue` finds only recapitalize/repay refund logic). Revenue claims are limited to booked revenue shares, so the surplus cannot be claimed by anyone.

### Impact Explanation
Permanent freezing of funds. Any user who transfers tokens to the pool contract — e.g., funding a repayment or supply directly instead of going through the controller, or sending excess — loses them irrevocably. The tokens increase physical custody but are invisible to every accounting path, so no operation can ever withdraw them. This is the same loss class as the reference Allo.sol finding (excess native tokens trapped), realized here through direct token transfer to a contract that has no excess-balance recovery.

### Likelihood Explanation
Reachable by any unprivileged address holding the asset: a single `token.transfer` to the pool address, which the rules explicitly allow as a reachable path ("direct token transfers to the pool or controller"). Unlike Ethereum `msg.value` — where the excess arrives inside the same call — here it requires a separate mistaken transfer, which is the standard way users erroneously fund contracts on Stellar. The protocol mitigates the class on all book-driven entrypoints, but deliberately leaves the raw-transfer hole open with no recovery mechanism.

### Recommendation
Add a `skim`/`recover_surplus` function to the pool that transfers `token.balance(pool) - sum(cash over all market books)` to the treasury or a caller-specified address, callable after all markets are iterated; or document and enforce that the pool must never hold balance above booked cash. Alternatively, since surplus already accrues to no one, an explicit recovery path preserves the mistaken funds.

### Proof of Concept
```rust
// Any user with the asset; no auth needed beyond their own transfer.
let pool_addr = /* pool contract for USDC */;
let tok = token::Client::new(&env, &usdc);

// Mistaken direct funding of the pool (e.g. intending to repay).
tok.transfer(&user, &pool_addr, &1_000_0000000);

// Pool custody rises, but no market's `cash` book moves.
assert_eq!(tok.balance(&pool_addr), prior + 1_000_0000000);
// get_reserves(hub) unchanged for every hub; no entrypoint can pay out
// the surplus — repay/recapitalize refunds are capped by booked
// mutations, and there is no sweep function in contracts/pool/src.
```