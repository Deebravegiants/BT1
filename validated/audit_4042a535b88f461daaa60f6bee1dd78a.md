### Title
Unvalidated route lets attacker-supplied contracts execute under the caller's signed authorization tree and drain wallet funds - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The strategy entrypoints (`swap_collateral`, `swap_debt`, `multiply`, `repay_debt_with_collateral`, `flash_position` paths that route) forward a fully caller-supplied `swap` XDR to the configured swap aggregator. The router keeps no allowlist of the pool or token addresses named in that payload and invokes them directly, so an attacker can put arbitrary deployed Wasm on the call stack beneath the caller's `require_auth`. Any `require_auth` on the caller performed by that rogue code is recorded as a child of the caller's own strategy authorization entry; once the caller signs the simulated tree, it executes — the DeFi equivalent of executing uploaded code in a trusted context.

### Finding Description
`swap_tokens` at `contracts/controller/src/strategies/swap.rs:13-55` takes the caller's opaque `StrategySwap` bytes and passes them unchanged to `router.execute_strategy(&controller, &amount_in, swap)` (line 37). The controller's protections bound only the controller's own funds: it authorizes exactly one input transfer (`authorize_transfer_as_current`, line 34), measures input spend (`RouterOverspend`, lines 42-48), and measures output (`NoSwapOutput`, lines 74-84). None of these constrain what the payload-named contracts do below the call.

In `contracts/swap-aggregator/src/venues/mod.rs:23-58`, `dispatch_hop` invokes `ctx.hop.pool` — an address taken verbatim from the attacker's payload — and `ctx.hop.token_in`/`token_out` are likewise payload-controlled. There is no registry or allowlist of venues, pools, or tokens. `docs/explanation/threat-model.md:154-165` confirms the exposure explicitly: "The router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization... The loss is then the caller's wallet, not the routed amount, and neither the payload minimum nor the final risk gate bounds it."

The harness test `tests/test-harness/tests/controller/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` pins the exact mechanism: a route whose `hop_pool` is an attacker-deployed contract calls `token.transfer(alice, attacker, WALLET_BALANCE)` on an unrelated token Alice holds; the host records that transfer as a sub-invocation of Alice's `swap_collateral` auth entry, and in enforcing mode it succeeds if Alice signed the simulated tree (lines 194-227 assert the recorded tree and the drained balance).

### Impact Explanation
Theft of user funds. A victim who signs a routed strategy transaction built from an attacker-supplied route (malicious frontend, poisoned quote, phishing) authorizes arbitrary `require_auth`-gated actions on their own address — `transfer` of any wallet token, `approve`, NFT moves — none of which touch the routed amount or violate `RouterOverspend`/`NoSwapOutput`/health-factor gates. The loss is unbounded by the swap size and by any protocol check.

### Likelihood Explanation
Exploitation needs the victim to sign a transaction whose authorization tree contains the malicious sub-invocation. Honest clients that decode and verify the route (as `skills/xoxno-swap-aggregator/payload.md:154-210` recommends) reject it, but nothing in the protocol rejects it — `simulateTransaction` faithfully produces a signable tree and the contracts execute it. Any unprivileged attacker can deploy the rogue pool and hand out the crafted `swap_xdr` at zero cost; success depends on social/signing UX, which is why this is not unconditional. Medium likelihood.

### Recommendation
Enforce allowlists at execution time, not at the client:
- In the router, maintain an owner-governed registry of permitted pool/token addresses (or venue attestations) and reject payload-named addresses absent from it, so a route can never place non-venue code under the caller's auth.
- Alternatively/additionally, in `swap_tokens` and the other strategy call sites, decode the `StrategySwap` and validate every referenced address against known market assets and approved pools before invoking the router.
- Document and enforce the client-side invariant (exactly one child `transfer` beneath the strategy entry) so wallets surface unexpected sub-invocations.

### Proof of Concept
Pinned in `tests/test-harness/tests/controller/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs:194-227`:
1. Attacker deploys `RogueHopPool` (lines 51-72) whose `swap` calls `wallet_token.transfer(alice, attacker, WALLET_BALANCE)`, and crafts a `RoutedSwap` XDR naming that pool (lines 111-125).
2. Alice calls `ctrl.swap_collateral(alice, account_id, USDC, 5_000e7, ETH, route)`; the controller authorizes only the 5,000 USDC input transfer to the router, then executes the route.
3. Recording mode shows the rogue transfer recorded as a child of Alice's `swap_collateral` entry (lines 206-222). Signing that tree yields `alice wallet = 0`, `attacker wallet = WALLET_BALANCE`, while the swap still delivers fair output and passes every protocol check (lines 224-226).