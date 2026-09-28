### Title
Route-supplied pool contracts execute arbitrary code inside the caller's `require_auth` scope, letting a malicious hop drain tokens from the caller's wallet via auth-tree poisoning - (File: contracts/swap-aggregator/src/execute/mod.rs)

### Summary
Analogous to TimescaleDB resolving functions through a user-writable `search_path`, the swap router resolves **pool addresses from the caller-supplied `assets` registry** and invokes them with no allowlist or contract-identity check. Any account calling controller `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, or `multiply` (or the router directly) causes the protocol to execute whatever contract the route names — inside a transaction whose only authorization is the caller's own `require_auth()` tree. A rogue "pool" contract can emit `token.transfer(victim, attacker, amount)` against any token the victim holds; the Soroban host records that invocation under the caller's auth entry during simulation, and a wallet that signs the simulated tree authorizes the theft. The repository's own harness test proves this end-to-end.

### Finding Description
`execute_strategy` decodes `StrategyPayload.assets` — a caller-controlled `Vec<Address>` — and builds each `SwapHop.pool` straight from it:

```rust
// contracts/swap-aggregator/src/execute/mod.rs:152-157
Opcode::Swap(venue) => {
    let hop = SwapHop {
        pool: ctx.assets.get_unchecked(op.idx_a),
        ...
```

`dispatch_hop` then invokes `pool.swap` (Aquarius) or equivalent venue functions on that arbitrary address (`contracts/swap-aggregator/src/venues/mod.rs:34-40`), and `invoke_pool_swap` calls `env.invoke_contract(pool, "swap", ...)` (`contracts/swap-aggregator/src/venues/aquarius/pool.rs:34`). There is no venue/pool allowlist — by design, per the README ("Unallowlisted route venues").

On the controller side, `swap_tokens` forwards the caller's `StrategySwap` bytes verbatim into `router.execute_strategy` under the controller's self-auth for the input transfer, while the strategy entrypoints (`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`'s `convert_swap`) are gated only by `caller.require_auth()` (`contracts/controller/src/strategies/swap.rs:36-38`, `multiply.rs:33-34`).

Because the malicious pool executes within the same transaction, any `require_auth` it triggers on the *caller* is recorded as a sub-invocation of the caller's auth entry. The harness test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates exactly this: a `RogueHopPool` embedded in a `swap_collateral` route calls `token.transfer(alice, attacker, WALLET_BALANCE)` on an unrelated wallet token; recording mode attaches it under Alice's `swap_collateral` root (lines 194-227), and in enforcing mode the transfer succeeds whenever the signed tree contains it (lines 258-269), while it is refused only if the user inspects and rejects the poisoned tree (lines 239-256).

This mirrors the CVE precisely: an attacker-controlled "schema" (the route's address registry) causes privileged-context code (a transaction authorized by the victim) to resolve and run attacker-chosen code instead of a trusted object (a real DEX pool).

### Impact Explanation
Theft of user funds. The rogue contract can transfer **any** token the victim holds — not just the swap input — up to the victim's full balances, since each `token.transfer(victim, …)` only needs a `require_auth` child in the victim's tree. The standard signing flow (simulate → wallet signs the returned auth tree) makes the malicious entry indistinguishable to a non-expert user, so the route doubles as a phishing payload that drains the wallet while still delivering a fair-looking swap output.

### Likelihood Explanation
Reachable by a single unprivileged address: the attacker only needs to get a victim to submit a poisoned `swap`/`swap_xdr` (e.g., via a malicious frontend, Discord-pasted route XDR, or a compromised quote response — the `assets` registry accepts any addresses). The on-chain path itself is fully permissionless and deterministic; the only external dependency is the victim signing the simulated auth tree, which is the default wallet UX and exactly what the test shows succeeds in enforcing mode. No privileged role, leaked key, or off-chain service compromise is required at the contract layer.

### Recommendation
- Pin the hop `pool` to a venue-verified registry or derive it deterministically (e.g., validate Soroswap pools against the factory, Aquarius pools against its router/pool contract id list) instead of trusting raw `assets` entries.
- Constrain the victim's auth surface: document/SDK-enforce that wallets and the SDK must reject simulated auth trees containing sub-invocations on contracts outside the expected input-transfer set, and emit the expected auth tree in SDK helpers so integrators can diff it.
- Alternatively, run venue calls through `authorize_as_current_contract` with an explicit invocation boundary so that a pool's nested `require_auth(sender)` cannot be recorded beneath the caller's root — e.g., never propagate caller-auth-requiring calls into venue code (venue adapters currently self-authorize only router pulls, but nothing stops the venue itself from issuing `victim.require_auth()`).

### Proof of Concept
The repository already contains a working PoC: `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`.

1. Alice holds 10 000 USDC supplied plus 77 770 units of an unrelated `wallet_token` (`Scene::new`, lines 83-108).
2. Attacker deploys `RogueHopPool` whose `swap()` executes `token.transfer(alice, attacker, WALLET_BALANCE)` (lines 52-72) and crafts a route XDR naming it as the hop pool (lines 111-125). The route still delivers a fair `min_out` in ETH so the swap looks legitimate.
3. `simulateTransaction` on `swap_collateral(alice, …, route)` records the rogue `wallet_token.transfer` as a child of Alice's auth entry (lines 195-227).
4. With the tree that simulation returned signed by Alice's wallet, enforcing mode executes the theft: Alice's wallet token balance → 0, attacker's → `WALLET_BALANCE` (lines 258-269). The honest tree (root only) is the only thing that blocks it (lines 239-256).