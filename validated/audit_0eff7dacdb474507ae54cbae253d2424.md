### Title
Attacker-controlled swap route injects arbitrary contract calls beneath the caller's authorization tree, draining unrelated wallet funds - (File: contracts/controller/src/strategies/swap.rs)

### Summary

The CVE class is injection of attacker-controlled input that escapes the intended query/validation boundary (arbitrary SQL via combined `keywords`/`topic_id` parameters). The on-chain analog is attacker-controlled route bytes (`swap: Bytes` / `StrategySwap`) that escape the intended "swap tokens" boundary: the controller authorizes the router to execute whatever pool addresses and calls the payload names, with no venue or pool allowlist, so a malicious "pool" contract runs inside the victim's signed authorization tree and can transfer any of the victim's tokens.

### Finding Description

`swap_tokens` grants the swap-aggregator router exactly one authorized input transfer, wraps `router.execute_strategy` in the flash guard, and validates only controller-side balance deltas (`RouterOverspend`, `NoSwapOutput`). Nothing in the controller inspects the route payload's contents. [1](#0-0) 

The router executes whichever `pool`/`token` addresses the decoded `StrategyPayload` names; it "keeps no allowlist" of them, so a route can put arbitrary third-party contract code on the call stack below the caller's authorization. [2](#0-1) 

The test harness demonstrates the primitive end to end: a router double invokes a route-named `RogueHopPool`, whose `swap()` calls `token.transfer(victim, attacker, amount)` on an unrelated wallet token. The recorded auth tree shows that transfer executing as a child of Alice's `swap_collateral` invocation, and her wallet balance goes to zero while the swap itself pays out fairly. [3](#0-2) [4](#0-3) 

This is the injection shape of the CVE: like `keywords` + `topic_id` being concatenated into SQL, the `swap` bytes are spliced into a privileged execution context (the caller's auth tree) with no syntactic containment — the payload's declared pools/tokens are executed, not merely read.

### Impact Explanation

Theft of user funds. Any token the signing user holds can be transferred to the attacker during `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply` (via `swap`/`convert_swap`), or a direct `execute_strategy` call. The loss is the caller's whole wallet balance in that token, unbounded by the routed amount, the payload `min_out`, or the post-swap health-factor gate — the theft happens inside venue code and is invisible to the controller's measured-delta checks. In the harness PoC, `WALLET_BALANCE` of an unrelated token moves from Alice to the attacker while the swap still delivers `FAIR_OUT_ETH` and the account passes all risk gates.

### Likelihood Explanation

Reachable by any unprivileged address that can get a victim to sign a route: the attacker crafts `swap_xdr` naming a rogue pool contract, and the honest simulation records the malicious `transfer` as a child of the victim's own auth entry — so the signed transaction executes it. Mitigations exist but are external: the threat model states a client "must decode the route it signs and refuse an authorization tree with any other child," placing the defense on wallet/dapp behavior rather than contract enforcement. Users signing routes from an untrusted or compromised quote source are exposed; a user who only ever signs exact minimal auth trees produced by a verifying client is not. This matches Medium: real theft path, but requires luring a victim into signing a crafted payload.

### Recommendation

Enforce containment on-chain rather than relying on client-side auth-tree inspection:

- Have the controller (or router) validate the decoded route before execution: require every hop's `pool`/`token_in`/`token_out` to come from a governed venue/pool registry, or at minimum require each hop's `token_in`/`token_out` to be listed hub assets.
- Alternatively, have the router forbid any sub-invocation by hop pools other than the venue's expected calls by constraining the invoker-auth entries it supplies (the Comet adapter pattern already scopes auth to a specific function + nested `transfer_from`; extend that scoping to all venues and to a fixed function signature so a pool cannot issue arbitrary `transfer`s under the caller's tree).

### Proof of Concept

Existing harness: `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`. `simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry` registers `RogueHopPool` (which transfers the victim's wallet token to the attacker), builds route bytes naming it, calls `swap_collateral` as Alice, and asserts the recorded authorization tree contains the theft `transfer` as a child of Alice's controller invocation, `wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`, while the strategy itself completes normally.

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L30-55)
```rust
    let in_before = token_in_client.balance(&controller);
    let out_before = token::Client::new(env, token_out).balance(&controller);

    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });

    // Reject input gains or overspending; refund only this swap's unused input.
    let in_after = token_in_client.balance(&controller);
    assert_with_error!(env, in_after <= in_before, StrategyError::RouterOverspend);
    let actual_spent = in_before - in_after;
    assert_with_error!(
        env,
        actual_spent <= amount_in,
        StrategyError::RouterOverspend
    );
    let leftover = amount_in - actual_spent;
    if leftover > 0 {
        token_in_client.transfer(&controller, refund_to, &leftover);
    }

    verify_router_output(env, token_out, out_before)
}
```

**File:** docs/explanation/threat-model.md (L154-165)
```markdown
That bound covers the controller's own grant only. The router calls the pool
and token addresses its payload names and keeps no allowlist of them, so a
route can put third-party code on the call stack below the caller's
authorization. A token transfer that such code makes from the caller is
recorded by an honest simulation as a child of the caller's authorization
entry, and it executes if the caller signs that tree. The loss is then the
caller's wallet, not the routed amount, and neither the payload minimum nor the
final risk gate bounds it. An honest swap strategy gives the caller no child
entry, and a direct router swap gives exactly one input transfer. A client must
decode the route it signs and refuse an authorization tree with any other
child. The direct `execute_strategy` path has the same exposure for every swap
user.
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L56-71)
```rust
    pub fn __constructor(env: Env, victim: Address, token: Address, to: Address, amount: i128) {
        env.storage()
            .instance()
            .set(&symbol_short!("PLAN"), &(victim, token, to, amount));
    }

    pub fn swap(env: Env) {
        let (victim, wallet_token, to, amount): (Address, Address, Address, i128) = env
            .storage()
            .instance()
            .get(&symbol_short!("PLAN"))
            .expect("plan is set by the constructor");
        if amount > 0 {
            token::Client::new(&env, &wallet_token).transfer(&victim, &to, &amount);
        }
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L195-226)
```rust
fn simulation_records_the_rogue_pool_wallet_transfer_under_the_callers_swap_collateral_entry() {
    let s = Scene::new();
    let route = s.route_through_pool_stealing(WALLET_BALANCE);

    // `simulateTransaction` runs recording mode with non-root auth disabled.
    s.t.env.mock_all_auths();
    s.try_swap(&route)
        .expect("recording mode accepts the route");
    let recorded = s.t.env.auths();
    std::println!("recorded auth tree = {recorded:#?}");

    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        )),
        sub_invocations: std::vec![],
    };
    let poisoned_root = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.t.controller.clone(),
            Symbol::new(&s.t.env, "swap_collateral"),
            s.swap_args(&route),
        )),
        sub_invocations: std::vec![stolen_transfer],
    };
    assert_eq!(recorded, std::vec![(s.alice.clone(), poisoned_root)]);

    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
    assert_eq!(s.t.supply_balance_raw(ALICE, "ETH"), FAIR_OUT_ETH);
```
