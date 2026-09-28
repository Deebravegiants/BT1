### Title
Router executes arbitrary pool code under the caller's authorization tree, enabling wallet drain via crafted route - ([File: contracts/swap-aggregator/src/venues/mod.rs])

### Summary
The Electron advisory's class is "code loaded from an attacker-controlled location runs inside the victim's trusted context." The on-chain analog is real and demonstrated in the repo's own test suite: the swap router (and by extension the controller's `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` strategies) invokes whatever pool/token addresses the route payload names, with no venue or pool allowlist. A rogue hop pool executes inside the same transaction where the caller's `require_auth` root is active, so any `token.transfer(victim, attacker, amount)` the rogue contract issues is recorded as a child of the caller's `swap_collateral` auth entry and succeeds once the caller signs that tree.

### Finding Description
`dispatch_hop` in `contracts/swap-aggregator/src/venues/mod.rs` dispatches hops to venue adapters that call pool addresses taken verbatim from the payload's `assets` registry; the program decoder validates index bounds and modes but never checks a pool/token allowlist (`docs/explanation/threat-model.md` states this explicitly: "The router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization"). The controller grants only `token_in.transfer(controller, router, amount_in)` (`contracts/controller/src/strategies/swap.rs:34`), but that narrowing protects the controller's own grant — it does nothing about the caller's root auth entry, under which the rogue callee's `require_auth`-gated calls are recorded.

The dedicated test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` proves the mechanics end-to-end:

- `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` (lines 194-227): a `RogueHopPool` whose `swap()` calls `token.transfer(alice, attacker, WALLET_BALANCE)` drains Alice's entire balance of an unrelated, never-listed token (77,770 units) during `swap_collateral`, while still paying a fair `min_out` so every protocol-side check (measured output, final risk gate) passes.
- `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` (lines 229-269): under enforcing auth the transfer is rejected only when the caller signs an honest root-only tree; when the caller signs the tree simulation produced — which now contains the malicious `transfer` child — the theft executes.

### Impact Explanation
Theft of user funds. The stolen amount is unbounded by the routed amount, the payload `min_out`, or the final account risk gate: the rogue contract can transfer any token the victim holds to any address, because the authorization it rides on is the victim's own signature. The swap still delivers a fair output, so no on-chain check detects the loss.

### Likelihood Explanation
Exploitation requires the victim to submit a route containing the attacker's pool and to sign the resulting authorization tree — the same shape as the Electron advisory's "attacker-controlled working directory + user launches the app" precondition (CVSS `UI:R`). Delivery is realistic through a malicious or compromised route source (spoofed quote response, phishing front-end, poisoned `routeXdr`), since the extra auth child is buried in a tree most clients render only as "N sub-invocations." An unprivileged attacker needs no protocol privilege — only the ability to deploy a contract and get the victim to use their route. Medium likelihood caps this at Medium, consistent with the source advisory's severity.

### Recommendation
Maintain a governance-managed allowlist of venue pool contracts (and possibly token addresses) that the router will invoke, rejecting payload registry entries not on it — mirroring INV-STRAT-03, which already requires approved pools for Blend migration. As defense in depth, document/enforce in the client SDK that an honest strategy produces exactly one input-transfer child and the router's self-authorized venue entries never appear under the caller's signature, and reject any simulated tree with extra children.

### Proof of Concept
Already implemented as `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:

1. Deploy `UnlistedPoolRouter` (a stand-in for the production router's dispatch behavior — it invokes `route.hop_pool` by name) and set it via `set_swap_aggregator`.
2. Deploy `RogueHopPool` initialized with `(victim = alice, wallet_token, to = attacker, amount = WALLET_BALANCE)`; its `swap()` executes `token::Client::new(&env, &wallet_token).transfer(&alice, &attacker, &WALLET_BALANCE)` (lines 62-71).
3. Alice calls `controller.swap_collateral(alice, account_id, usdc, 5_000 USDC, eth, route_xdr)` where `route_xdr` names `RogueHopPool`.
4. Simulation records `transfer(alice → attacker, 77_770_000_000)` as a sub-invocation of Alice's `swap_collateral` auth entry (asserted at line 222); the swap returns a fair 2.5 ETH.
5. Signing the simulated tree: `assert_eq!(s.wallet(&s.alice), 0)` and `assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE)` (lines 267-268) — full wallet drain of an asset the protocol never touched.