### Title
Tokens transferred directly to the pool (wrong token or unsolicited funding) are permanently stranded — the pool never reconciles unbooked balances and exposes no recovery path - ([File: contracts/pool/src/ops/recapitalize.rs](contracts/pool/src/ops/recapitalize.rs))

### Summary
The analog of "bounty accepts arbitrary tokens but can only pay out `payoutTokenAddress`" is the XOXNO liquidity pool's physical custody model: the pool holds one real token balance per token contract, but its accounting is purely book-based (`cash` per `(hub_id, asset)` market). Any token an unprivileged address transfers directly to the pool — including tokens for which no market exists, or tokens sent by mistake — is credited to no book, and no entrypoint in the pool's ABI can ever move it back out. Unlike the OpenQ bounty (where the funds were refundable after expiry), here there is no expiry, no sweep, and no admin rescue: the stranded balance is permanently frozen inside the contract.

### Finding Description
The pool's surface (per `contracts/pool/README.md` surface table) has exactly these outbound legs: `borrow`, `withdraw`, `repay` refund, `recapitalize` refund, `claim_revenue`, `flash_loan`, `create_strategy`. Every one of them debits the per-market `cash` book before transferring:

- `recapitalize` credits `min(amount, backing_shortfall)` and refunds the excess, but `backing_shortfall` is computed from booked claims vs. booked `cash` — not from `token::balance()`. Unbooked donations are invisible to it (`contracts/pool/src/ops/recapitalize.rs:44-67`).
- `claim_revenue` burns claimable revenue shares and debits `cash` (`contracts/pool/src/ops/revenue.rs:39-55`); it cannot touch unbooked balance.
- `withdraw`/`borrow`/`flash_loan` all require `cache.require_reserves(amount)` against booked cash (`contracts/pool/src/ops/flash.rs:85`).
- `flash_loan` does read `token.balance(&pool)`, but only uses it as `pre_balance` for strict-equality checks on its own payout/repayment legs (`contracts/pool/src/ops/flash.rs:53-67`, `183-189`) — the donation rides through `balance_after_payout`/`balance_after_repayment` untouched.

The architecture doc states the property explicitly: "The pool tracks cash in an accounting book. Supply, repayment, and recapitalization credit the tokens actually received; direct donations do not automatically increase booked cash" (`docs/reference/architecture.md:57-61`), and the threat model adds "Direct donations do not rewrite those books" (`docs/explanation/threat-model.md:129-131`). The test `pool_all_money_paths_preserve_books_and_shared_token_custody` confirms a 7-token direct transfer to the pool leaves every market's `cash` unchanged (`tests/test-harness/tests/pool_money_flow_audit.rs:86-103`).

Because the hub/spoke design shares one physical pool balance across all markets of the same token, a stranded token is also not attributable to any single market — there is no book it could later be credited to even manually.

### Impact Explanation
Permanent freezing of funds: any unprivileged user who transfers tokens directly to the pool address (wrong token, mistaken "funding", misconfigured integration, or a receiver/callback that pushes tokens into the pool during `execute_flash_loan`) loses them irrevocably. No controller entrypoint can reach them — `recapitalize` refunds excess prefunding to the payer but only books up to the shortfall (`contracts/controller/src/markets.rs:140-164`), and governance has no pool-side sweep operation to execute. The funds also sit on top of `token.balance(pool)`, so they superficially appear as liquidity while being unclaimable by suppliers, borrowers, and revenue.

### Likelihood Explanation
Direct transfers are a listed unprivileged path and require no special state. Accidental funding is realistic: the pool address is public, SAC token transfers to it succeed unconditionally, and integrations may assume "send tokens, then call" semantics like OpenQ's `receiveFunds`. The trigger is a single ordinary `token.transfer(from, pool, amount)`.

### Recommendation
Give the pool an owner-only sweep entrypoint for unbooked balance: compute `token.balance(pool)` minus the sum of booked `cash` across all markets of that asset (tracked in a per-token aggregate or reconciled at call time), and allow the owner (controller) to transfer out only the excess. Alternatively, document and enforce on the controller that all funding must go through measured-transfer entrypoints, and add a rescue path at least for tokens with no listed market.

### Proof of Concept
1. Any address calls `token.transfer(payer, pool_address, X)` for an asset `A` (this is exactly what the test does at `pool_money_flow_audit.rs:87-88`).
2. Observe `token.balance(pool) == Σ cash(markets of A) + X` while every market's `cash` is unchanged (asserted at lines 93-96).
3. Call `recapitalize(hub_asset, payer, X)` via the controller: `applied = min(X, backing_shortfall)`. With no shortfall, `applied = 0` and only the prefunded amount is refunded — the earlier `X` stays locked (same pattern as the "healthy recap refund" case, `pool_money_flow_audit.rs:257-267`).
4. Enumerate the pool ABI: no entrypoint references `token.balance` for outbound transfer other than `flash_loan`'s equality guard. `X` is permanently unrecoverable.