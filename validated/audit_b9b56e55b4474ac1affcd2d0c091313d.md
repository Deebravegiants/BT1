### Title
User-supplied swap route can inject arbitrary `token.transfer` calls into the caller's signed auth tree, draining the caller's wallet - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller's routed strategies (`multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`) accept caller-supplied route bytes and execute them through the configured router. The route names arbitrary hop-pool contract addresses that are never validated against an allowlist. Any code invoked anywhere inside the strategy executes under the caller's root `require_auth`, so a malicious hop pool can call `token.transfer(caller, attacker, amount)` on any unrelated token in the caller's wallet. The stolen transfer is folded into the recorded authorization tree that `simulateTransaction` returns; a wallet that signs the returned tree (the standard flow) authorizes the theft. This is the SSRF analog: a user-controlled "URL" (route pool address) causes the contract to make an attacker-chosen external invocation carrying the victim's authority.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs:13-55` snapshots balances, authorizes exactly one `token_in.transfer(controller, router, amount_in)` via `authorize_transfer_as_current`, and calls `router.execute_strategy(&controller, &amount_in, swap)` where `swap` is raw caller-supplied route bytes. The controller binds its own contract auth narrowly (`authorize_transfer_as_current` with no sub-invocations), but nothing binds the *caller's* auth: `caller.require_auth()` at the strategy root covers the entire invocation subtree, including every contract the route reaches.

Because route venue addresses are unallowlisted, an attacker-prepared (or attacker-advertised) route passes through a rogue "pool" whose `swap` performs `token::Client::transfer(victim, attacker, victim_balance)` on an unrelated token. The harness test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` demonstrates exactly this end-to-end against `swap_collateral`:

- In recording mode the rogue transfer lands as a child of the caller's `swap_collateral` authorized invocation, and Alice's wallet is drained (lines 194-227: `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`).
- Signing only the honest root-only tree rejects the theft (lines 239-256), but signing the tree simulation produced — the normal wallet flow — authorizes it (lines 258-268).
- The same holds with `SourceAccount` credentials (lines 322-367).

`flash_position`'s `invoke_receiver` (`contracts/controller/src/strategies/flash_position.rs:297-323`) is the same shape but the receiver is the initiator's own contract, so it is self-targeted. The router path is the dangerous one because route bytes are arbitrary and venues are unallowlisted by design (ADR-0018, `docs/explanation/decisions.md:221-228`).

### Impact Explanation
Theft of user funds: any token balance held by the caller's address can be moved to the attacker inside a transaction the caller believes is only a collateral/debt swap. The rogue pool needs to return a fair-looking swap output (the test's router double pays `min_out` of ETH, so the victim's account ends up correctly collateralized and every controller check passes — measured input spend, positive measured output, and final solvency gates in `swap_tokens` all succeed). The theft is invisible to the protocol's own accounting; it only appears as an extra node in the signed auth tree, which most wallets do not render per-invocation.

### Likelihood Explanation
Medium. Exploitation requires the victim to submit a crafted route. That is realistic because route bytes are opaque XDR produced off-chain by integrators or aggregators, and the standard `simulateTransaction` → sign returned auth tree flow will present the poisoned tree as valid. An attacker can distribute a malicious route via a phishing front-end, a compromised or malicious quote service, or a poisoned route payload shared to a victim. No protocol privilege is needed by the attacker; the rogue pool is just a deployed contract.

### Recommendation
Constrain the caller's authorization scope or the reachable call graph for routed strategies:

- Enumerate or allowlist permitted venue pool addresses (e.g., verified at admission, or a governed venue registry the router must check before invoking any `hop.pool` address).
- Alternatively, run the router hop in a frame that cannot see the caller's auth — e.g., have the controller pull/approve only its own contract-auth tree and document/reject routes whose simulation adds `transfer(caller, ...)` children, or surface a wallet-facing warning when the recorded auth tree contains calls not structurally implied by the route's declared token legs.
- At minimum, detect post-hoc that no `require_auth` on `caller` was consumed by an address outside the declared route's token/router set (not directly enforceable on-chain, so the allowlist approach is the robust fix).

### Proof of Concept
The repository already contains the executable demonstration:

- `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:
  - `RogueHopPool::swap` (lines 62-71) performs `token.transfer(victim, to, amount)` inside the route hop.
  - `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` (lines 194-227) shows the stolen `transfer` recorded as a sub-invocation of Alice's `swap_collateral` auth and the wallet drained.
  - `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` (lines 229-269) shows signing the simulation-produced tree authorizes the theft.

Steps (as in the test):

1. Alice holds `WALLET_BALANCE` of an unrelated token and supplies USDC as collateral.
2. Attacker deploys `RogueHopPool` with plan `(alice, wallet_token, attacker, WALLET_BALANCE)` and a router executing `execute_strategy` that calls `hop_pool.swap` and pays `min_out`.
3. Victim submits `swap_collateral(alice, account_id, USDC, amount, ETH, route)` where the route's hop pool is `RogueHopPool`.
4. Simulation records the auth tree containing `wallet_token.transfer(alice → attacker, WALLET_BALANCE)`; the wallet signs the returned tree.
5. Result: Alice receives fair ETH collateral, every controller check passes, and her entire unrelated wallet balance is transferred to the attacker.