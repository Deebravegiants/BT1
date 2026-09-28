### Title
Direct token transfers to the pool are permanently unrecoverable — no excess-balance recovery path exists - (File: contracts/pool/src/lib.rs)

### Summary
The pool contract custodies every market's tokens but accounts for them through an internal `cash` book that only moves on owner-initiated calls (`supply`, `repay`, `recapitalize`, `flash_loan`, `create_strategy`). Tokens transferred directly to the pool address — outside any crediting call — are never booked, and no entrypoint exists to return or sweep them. Since every outbound transfer is bounded by the `cash` book, donated/excess tokens can never leave the contract again. This is the exact analog of unrecoverable excess `stETH` in `wstETH`, reachable by any unprivileged address via a plain token `transfer`.

### Finding Description
The pool's accounting model explicitly separates the token balance from the book: "Cash is an accounting book, separate from the token balance" (contracts/pool/src/lib.rs:34) and "direct donations do not automatically increase booked cash" (docs/reference/architecture.md:57-58). The test suite pins that an unsolicited transfer inflates the SAC balance above all markets' combined books (`token.balance(pool) == cash_h1 + cash_h2 + donation`, tests/test-harness/tests/pool_money_flow_audit.rs:86-96).

Every outbound path is book-bounded:
- `withdraw` / `borrow` transfer at most the debited `cash` amount (contracts/pool/src/lib.rs:140-163).
- `repay` refunds only the overpayment declared in that call, not prior balances (lib.rs:168).
- `recapitalize` credits only up to `backing_shortfall` and refunds the excess of that call's declared `amount` (lib.rs:187-194).
- `claim_revenue` pays `min(cash, revenue)` to the owner — cash-bounded again (lib.rs:250).
- `flash_loan` checks `token.balance` with strict equality but restores, never drains, the excess.

The complete mutator surface (lib.rs:100-252) contains no `sweep`, `skim`, `rescue`, or excess-recovery function — unlike the swap-aggregator's `sweep_balance` (contracts/swap-aggregator/src/lib.rs:188-203), which exists precisely because that contract acknowledges stray balances. The controller has the same gap: refund logic covers "only positive callback deltas of refund-listed tokens… Neither category sweeps prior balances" (docs/explanation/threat-model.md:172-173), and the DeFindex adapter "has no recovery path for arbitrary stranded assets" (docs/reference/architecture.md:53).

### Impact Explanation
Permanent freezing of funds. Any token amount sent to the pool address by direct `token.transfer(sender, pool, amount)` — whether by user mistake, a misconfigured integration, or a venue pushing LP rewards to the pool (the threat model confirms "any caller can push accrued rewards into the pool address as an unbooked donation", docs/explanation/threat-model.md:134-138) — raises `balance(pool)` above `Σ cash` forever. No privileged or unprivileged call can extract the difference: payouts are capped by per-market books that never saw the deposit, and the owner (controller) has no instruction that transfers out unbooked balance. The funds are not even socially distributed to suppliers; they are simply locked.

### Likelihood Explanation
Medium-low likelihood, direct execution. The path is a single unprivileged SAC `transfer` — explicitly within the allowed attack surface ("direct token transfers to the pool or controller"). Loss requires a mistaken or misdirected transfer rather than an exploitable profit path, but the protocol makes the error irreversible by design, mirroring the referenced `wstETH` issue. The pool is also the documented holder of Aquarius LP collateral whose venue rewards accrue to the pool address, so unsolicited inbound balances are an expected, recurring occurrence rather than a hypothetical.

### Recommendation
Add an owner-gated excess-recovery entrypoint to the pool, e.g. `sweep_excess(hub_asset, recipient) -> i128`, that computes `token.balance(pool) - total_booked_cash_for_that_token` (summing `cash` across every hub sharing the token, since custody is shared per docs/reference/architecture.md:63-64) and transfers only the unbooked surplus — never touching any market's `cash`. Equivalently, governance could expose a matching controller passthrough. For shared-custody tokens the sweep must subtract the sum of all hub books for that asset, not a single market's.

### Proof of Concept
1. Deploy controller + pool; create a market for token `T` in hub 0. Have a supplier `supply` 1,000 T (books: `cash = 1000`, `balance(pool) = 1000`).
2. Unprivileged user calls `T.transfer(user, pool, 500)` — `balance(pool) = 1500`, `cash` still `1000` (pinned by tests/test-harness/tests/pool_money_flow_audit.rs:86-96).
3. Enumerate every pool entrypoint (`supply`, `borrow`, `withdraw`, `repay`, `recapitalize`, `flash_loan`, `create_strategy`, `seize_positions`, `net_settle`, `claim_revenue`): each is `#[only_owner]`, and each outbound leg is bounded by the book — none transfers the 500 T excess.
4. Enumerate every controller entrypoint (`supply`, `repay`, `recapitalize`, `claim_revenue`, swaps, flash paths): refunds cover only in-call deltas; no entrypoint instructs the pool to pay unbooked balance.
5. The 500 T remains at the pool address permanently, with no code path that can move it — even a Wasm `upgrade` is the only theoretical escape, which is out of scope.