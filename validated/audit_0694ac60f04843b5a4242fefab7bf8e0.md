### Title
Attacker-supplied route XDR executes arbitrary contract code inside the victim's authorization tree and drains unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Analogous to `@cgauge/yaml` evaluating attacker-controlled input with the parser's full authority, `swap_tokens` passes a fully attacker-crafted `StrategySwap` payload to the router, which invokes whatever pool/token addresses the payload names — with no allowlist — while the caller's `require_auth` is still active on the call stack. A malicious "hop pool" can then call `token.transfer(victim, attacker, amount)` on any token, and Soroban records that transfer as a child of the victim's signed authorization entry. If the victim signs the auth tree simulation produced (the normal flow for `simulateTransaction`-built transactions), the transfer executes. The result is theft of arbitrary wallet tokens unrelated to the swap, bounded by neither the routed `amount_in`, the route's `min_out`, nor the controller's final health-factor gates.

### Finding Description
`swap_tokens` in `contracts/controller/src/strategies/swap.rs` authorizes only one exact input transfer (`authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in)`) and then calls `router.execute_strategy(&controller, &amount_in, swap)` inside the flash guard (swap.rs:33-38). The `swap` bytes are supplied verbatim by the caller of `swap_collateral` / `multiply` / `swap_debt` / `repay_debt_with_collateral` — i.e. built off-chain and never validated for which contract addresses it names.

The router "calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization" (docs/explanation/threat-model.md:154-165). Because `sender.require_auth()` runs in the controller's root frame, any `require_auth`-protected call made by hop code is attributed to the victim's entry. An honest simulation attaches the rogue `token.transfer(victim, attacker, X)` as a child of the victim's `swap_collateral` invocation; if the victim signs that tree (which is exactly what `simulateTransaction` produces and what clients normally relay), the transfer executes and the victim's wallet tokens are stolen.

This is proven end-to-end by `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:
- `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` shows the rogue `RogueHopPool::swap` issuing `wallet_token.transfer(alice, attacker, WALLET_BALANCE)` inside `swap_collateral`, the host recording it under Alice's auth entry, and Alice's wallet balance going to 0 while the swap still credits her fair ETH output and passes all risk gates (lines 194-227).
- `enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer` confirms the host accepts the theft exactly when the signed tree contains the recorded child (lines 229-269).

None of the controller's defenses bound this: `RouterOverspend`/`NoSwapOutput` only measure `token_in`/`token_out` controller balances (swap.rs:40-54), the payload `min_out` is checked by the router not the controller, and the final HF/LT gates see a perfectly solvent account.

### Impact Explanation
Theft of user funds. A victim who executes a single attacker-crafted route through `swap_collateral`, `multiply`, `swap_debt`, or `repay_debt_with_collateral` loses every token of every type the malicious hop addresses, up to the full wallet balance — independent of how much collateral they routed. The in-scope acceptance criterion "theft of user funds" is met directly; the recorded auth tree makes the theft indistinguishable from a legitimate swap to a non-specialist signer.

### Likelihood Explanation
A single unprivileged attacker deploys a malicious "pool" contract and gets the route XDR to the victim — routes are built off-chain, so any compromised/malicious quoting channel or phishing route suffices; no protocol privilege is needed. The only mitigation is client-side: the signer must decode the route and reject any auth tree with extra children (threat-model.md:161-165). There is no on-chain defense: the controller grants scoped invocation authority (INV-STRAT-01) but that scoping applies to the controller's own grant, not to the victim's root-frame `require_auth`, which remains live for the whole call. Likelihood is gated by the victim signing a poisoned tree, which honest simulation actively constructs for them.

### Recommendation
Validate the route's invoked addresses on-chain or eliminate the exposure:
- Reject route payloads whose hop pool/token addresses are not the listed market tokens or a governance-allowlisted venue set, enforced in `swap_tokens` before `execute_strategy`.
- Alternatively, have the controller invoke the router via a sub-account/invoker pattern so the user's `require_auth` is not the root frame during arbitrary third-party code execution.
- At minimum, surface the child-invocation count in the client so a route adding any transfer beyond the single input transfer is refused before signing.

### Proof of Concept
```
// tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs
// Attacker contract invoked by the route payload; steals any token from victim.
#[contract]
pub struct RogueHopPool;
#[contractimpl]
impl RogueHopPool {
    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) =
            env.storage().instance().get(&symbol_short!("PLAN")).unwrap();
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
    }
}
```
Attack flow:
1. Attacker deploys `RogueHopPool` with `PLAN = (alice, wallet_token, attacker, wallet_balance)` and constructs route XDR naming it as a hop pool.
2. Alice calls `controller.swap_collateral(alice, account_id, USDC, 5_000e7, ETH, route)`. Simulation records the rogue `wallet_token.transfer(alice, attacker, balance)` as a child of her `swap_collateral` auth entry; she signs the returned tree.
3. `swap_tokens` authorizes the exact USDC input and calls `execute_strategy`; the rogue pool executes the wallet transfer under Alice's live `require_auth`.
4. The swap still returns fair output (`FAIR_OUT_ETH`), all controller risk gates pass, but `wallet_token.balance(alice) == 0` and `balance(attacker) == WALLET_BALANCE` — asserted at test lines 224-227 and 265-268.