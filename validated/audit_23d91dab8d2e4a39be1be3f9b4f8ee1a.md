### Title
Tokens transferred directly to the liquidity pool are permanently locked as uncredited custody surplus - (File: contracts/pool/src/cache/cash.rs)

### Summary
The external report describes ETH being irreversibly trapped in Allo strategies because the contract accepts `msg.value` it cannot return or account for. XOXNO Lending's pool has the same structural defect in Soroban form: any address can call `token.transfer(user, pool, amount)` directly, and the pool has no sweep, skim, or donation-recognition path. The pool only ever pays out against its `cash` book, so tokens sitting above the book are permanently stranded.

### Finding Description
The pool's entire outbound surface is book-driven. `Cache::require_reserves` caps every outflow at the accounting `cash` value (contracts/pool/src/cache/cash.rs:15-21), and `transfer_out` — used by `borrow`, `withdraw`, `repay` refunds, `recapitalize` refunds, `claim_revenue`, and flash loans — only moves amounts the book has already decremented or decided to refund (contracts/pool/src/cache/cash.rs:46-53). The README confirms `cash` "is a bookkeeping number" and the only live `token.balance()` reconciliation is the strict-equality check inside `flash_loan` (contracts/pool/src/ops/flash.rs:61-66, 183-189).

There is no `sweep`, `skim`, `recover`, or donation function anywhere in `contracts/pool`. All mutating pool entrypoints are `only_owner` (the controller), and even the controller cannot extract custody above `cash`: `withdraw` and `borrow` go through `require_reserves`, `claim_revenue` is capped by booked revenue shares, `repay`/`recapitalize` refunds are bounded by the payer's own declared inbound amount, and `seize_positions` only rebooks existing bad debt rather than paying tokens out.

The same strand applies to tokens sent directly to the controller: `refund_controller_balance_delta` explicitly "preserv[es] the pre-existing balance" — it refunds only the delta measured inside one call, so anything already sitting at the controller address is permanently unretrievable (contracts/controller/src/payments.rs:39-52).

### Impact Explanation
Permanent freezing of user funds. A user who mistakenly `transfer`s a market asset directly to the pool (e.g., intending to pre-fund a repay the way the pool's prefunded model suggests, or sending to the wrong address) loses the tokens forever: they are never credited to `cash`, never claimable by the sender, and cannot be recovered by the controller or governance. They only marginally over-collateralize the market — no one can withdraw them. This matches the report's "locked ETH in strategies" impact.

### Likelihood Explanation
Medium. It requires user error, but the pool's own design actively invites the mistake: `repay` and `recapitalize` both operate on a "prefund the pool, then call" model (pool/src/ops/repay.rs:3-4), so a user replicating that flow with a raw `token.transfer` — rather than through `controller.repay`, which prefunds and refunds in one transaction — strands the funds. There is no entrypoint-level guard that rejects or refunds unexpected inbound tokens.

### Recommendation
Add a permissionless surplus-recovery entrypoint on the pool (e.g., `sweep_excess(hub_asset, recipient)`) that transfers `token.balance(pool) - cash` to a designated recovery address, mirroring how `flash_loan` already reads live balances; or document and enforce the prefund invariant by exposing a controller-side `recover_stranded` governance operation. At minimum, surface in `repay`/`recapitalize` documentation that direct transfers are unrecoverable.

### Proof of Concept
```rust
// Setup: pool with cash == custody == 1000 tokens.
let user = Address::generate(&env);
token_admin.mint(&user, &500);

// User error: direct transfer to the pool instead of controller.repay.
token::Client::new(&env, &asset).transfer(&user, &pool_addr, &500);

// Custody is now 1500, cash book still 1000.
assert_eq!(tok.balance(&pool_addr), 1500);
assert_eq!(pool_client.get_reserves(&key), 1000);

// Every outflow is book-bound:
// - withdraw/borrow hit require_reserves (cash.rs:18) -> capped at 1000
// - claim_revenue capped by booked revenue shares -> 0 available
// - repay/recapitalize refunds bounded by the payer's own inbound amount
// - no sweep/recover entrypoint exists on pool or controller
// Result: the 500 tokens are permanently locked.
```