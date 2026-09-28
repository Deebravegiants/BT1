### Title
Unvalidated route bytes let a swap pool run arbitrary code beneath the caller's signed auth tree and drain the caller's wallet - (File: contracts/controller/src/strategies/swap.rs)

### Summary
The controller passes the caller-supplied `swap`/`swap_xdr` payload verbatim to the swap aggregator without validating which contracts the route invokes. Because the router calls whatever pool/token addresses the payload names and keeps no venue allowlist, a malicious route embeds attacker-deployed code on the call stack *below* the caller's `require_auth`. Any `require_auth`-protected call that rogue code makes (e.g., `token.transfer(victim → attacker)`) is recorded during simulation as a child of the caller's authorization entry and executes once the caller signs the simulated tree. The result is theft of wallet tokens unrelated to the swap — the exact Soroban analogue of the CVE's unvalidated-string-to-external-program argument injection: untrusted input selects the invoked program and its arguments inside a trusted privileged context.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs` authenticates the strategy caller upstream (`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`), then forwards `swap` to `router.execute_strategy(&controller, &amount_in, swap)` unchanged. It constrains only the controller's *own* grant — one exact `authorize_transfer_as_current` of `token_in` for `amount_in` (line 34) — and afterwards checks the controller's measured spend/output (`RouterOverspend`, `NoSwapOutput`). Neither check constrains what the route payload does with the *caller's* auth frame above the whole call.

The threat model states the exposure directly: the router "calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization. A token transfer that such code makes from the caller is recorded by an honest simulation as a child of the caller's authorization entry, and it executes if the caller signs that tree. The loss is then the caller's wallet, not the routed amount" (`docs/explanation/threat-model.md:154-165`). Like `BROWSER` in the CVE, the payload chooses which external program runs with authority derived from the caller.

### Impact Explanation
Theft of user funds. Any token the victim holds — including assets the protocol never listed — can be moved to the attacker. The harness test `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` proves it end-to-end: in recording/simulation mode a `RogueHopPool` embedded in the route executes `token.transfer(alice, attacker, WALLET_BALANCE)`, the transfer is attached under Alice's `swap_collateral` auth entry, the swap still pays out fairly (`FAIR_OUT_ETH` lands in her supply position), and enforcing mode executes the theft when she signs the recorded tree (`assert_eq!(s.wallet(&s.alice), 0)`). Neither `min_out` nor the controller's post-swap risk gates bound the loss.

### Likelihood Explanation
Any unprivileged attacker can craft a route (the payload format is public; pool/token registry indices are caller-controlled `u8` indices into the `assets` registry) and get a victim to submit `swap_collateral`/`swap_debt`/`repay_debt_with_collateral`/`multiply` — e.g., via a spoofed quote UI or a doctored `routeXdr`. The theft is invisible at the envelope level: the transaction delivers the promised swap output, so it passes simulation-based slippage checks. Exploitation requires the victim to sign the simulation-returned auth tree containing the extra child entry; wallets/clients that do not diff child invocations against an expected single input transfer will sign it. This mirrors the CVE's UI:R condition and keeps it reachable rather than automatic.

### Recommendation
Give callers a way to constrain route side-effects on-chain, since the controller currently validates nothing inside `swap`:
- Have the router enforce a venue/pool allowlist (or per-venue known-pool registry) so hop targets cannot be arbitrary attacker contracts.
- Alternatively, have the controller require the route's declared token set to be limited to `token_in`, `token_out`, and protocol-listed assets, rejecting payloads that reference other tokens.
- At minimum, document and enforce in the SDK/client that a signed auth tree for a strategy verb must contain exactly the input-transfer child and no other sub-invocation; reject any simulation whose tree has additional children before signing.

### Proof of Concept
```rust
// Attacker-deployed "pool" referenced by the route payload (see
// tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs)
#[contract]
pub struct RogueHopPool;

#[contractimpl]
impl RogueHopPool {
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage().instance().set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }
    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) =
            env.storage().instance().get(&symbol_short!("PLAN")).unwrap();
        // Runs below the victim's require_auth frame; recorded as a child of
        // the victim's swap_collateral auth entry during simulation.
        token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
    }
}
```
Attack flow:
1. Victim requests a `swap_collateral` route; attacker returns `swap_xdr` naming `RogueHopPool` as a hop pool while still producing a fair output.
2. Victim calls `controller.swap_collateral(caller, account_id, usdc, amount_in, eth, swap_xdr)`; `swap_tokens` forwards the bytes to the router.
3. The router invokes `RogueHopPool.swap`, which calls `token.transfer(victim → attacker)`. Simulation records it under the victim's auth entry; the victim signs the tree.
4. The swap completes normally (positive measured output, healthy account), and the victim's unrelated wallet token is emptied — confirmed by `assert_eq!(s.wallet(&s.alice), 0)` in the harness test.