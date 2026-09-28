### Title
Tokens Sent Directly to the Liquidity Pool Are Permanently Locked With No Recovery Path - (File: contracts/pool/src/lib.rs)

### Summary
The XOXNO Lending `LiquidityPool` tracks solvency through an internal `cash` accounting book that is deliberately decoupled from the contract's actual token balance. Any token transfer sent directly to the pool address (or otherwise stranded in its balance) is invisible to every write path, and no entrypoint — privileged or permissionless — can withdraw the excess. This is the same bug class as the Optimism `donateETH()` finding: assets held by the contract that are permanently unrecoverable.

### Finding Description
The pool's own architecture doc states: "Cash is an accounting book, separate from the token balance" (`contracts/pool/src/lib.rs` line 34–36). Cash is only mutated through owner-gated ops:

- `supply` / `repay` / `create_strategy` credit `cash` after the controller has transferred a *specified* amount in.
- `withdraw` / `borrow` / `flash_loan` / `claim_revenue` debit `cash` and transfer out only what the book authorizes. `claim_revenue` pays `min(cash, revenue)` — bounded by the book, not the balance.
- `recapitalize` (`contracts/pool/src/ops/recapitalize.rs:44-67`) is the only path that injects cash without minting shares, but it is pull-based: it credits `min(amount, backing_shortfall)` where `amount` is what the controller transferred in for this call, and refunds `amount - applied` to `payer`. It never inspects the contract's token balance, so a pre-existing surplus of token balance over `cash` is not absorbed.

An unprivileged user can invoke the controller's `recapitalize` entrypoint, but that function pulls `amount` from the payer — it cannot act on tokens already sitting in the pool's balance. Any tokens pushed directly to the pool address via a plain `token::transfer` are therefore permanently stranded: they inflate the physical balance but are backed by no cash entry, no supply shares, no debt write-down trigger, and no sweep function.

### Impact Explanation
Permanent freezing of funds. Donated or misdirected tokens remain on the pool's balance forever — the only outflows (`withdraw`, `borrow`, `flash_loan`, `claim_revenue`, `net_settle`) are all capped by the internal `cash` book and cannot touch the untracked surplus. There is no `sweep`/`recover`/`rescue` entrypoint anywhere in `contracts/pool` or `contracts/controller`; a grep for such functions returns only governance timelock recovery (operation scheduling, not token recovery) and swap-aggregator `sweep` (out of scope and a different contract's balance). The loss is unbounded — it scales with whatever amount is sent.

### Likelihood Explanation
Medium-to-low: realization requires user error or an intentional donation (a direct `token::transfer` to the pool address), which is the same trigger profile as the Optimism report. Notably, even an *intentional* rescue attempt fails: a donor who sends tokens to fix a backing shortfall and then calls controller `recapitalize` gets nothing credited — `recapitalize::accounting` only applies the `amount` the controller pulls in that call, so the pre-sent tokens stay untracked while still being unrecoverable.

### Recommendation
Add a permissionless `skim`/`sync` entrypoint that measures `token_balance - cash` and either (a) credits the surplus to protocol revenue shares (making it claimable via `claim_revenue`), or (b) applies it to `backing_shortfall` like `recapitalize` does, with any remainder booked as revenue. Alternatively, add an owner-gated `sweep(to, amount)` capped at `balance - cash` so stray funds can never drain supplier backing.

### Proof of Concept
1. Pool market (hub `H`, token `T`) has `cash = 1000`, matching token balance `1000`.
2. Any unprivileged address calls `T.transfer(pool, 500)`. Pool token balance is now `1500`; `cash` remains `1000`.
3. Donor calls controller `recapitalize(H_T, 0)` — `applied = min(0, shortfall) = 0`, nothing happens; the `500` surplus is not detected because `accounting` never reads `token::balance`.
4. All withdrawal/borrow/claim paths are bounded by `cash`; the `500` units can never leave the contract. No function in the pool or controller interface transfers out untracked balance.