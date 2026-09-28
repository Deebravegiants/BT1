### Title
Opaque router payload lets a signed strategy include unauthorized child transfers that drain unrelated wallet tokens - (File: contracts/controller/src/strategies/swap.rs)

### Summary
Controller strategy entrypoints accept `swap: Bytes` as an opaque payload and forward it to the configured aggregator while checking only controller input/output balances and final account risk; a poisoned payload can make route code place an extra `token.transfer(victim -> attacker)` under the victim's signed authorization tree and steal unrelated wallet funds. [1](#0-0) [2](#0-1) 

### Finding Description
`swap_collateral`, `swap_debt`, `multiply`, and `repay_debt_with_collateral` all require caller/account authority but pass attacker-influenced `swap` bytes into the shared router boundary without parsing venue addresses, token addresses, or the invocation tree implied by the payload. [3](#0-2) [4](#0-3) [5](#0-4)   
The shared `swap_tokens` snapshots balances, authorizes only the exact input transfer to `router_addr`, calls `router.execute_strategy(&controller, &amount_in, swap)`, then accepts the call if input spend is bounded and measured output is positive. [6](#0-5)   
Those checks constrain the controller's balances, but they do not enumerate or reject additional sub-invocations that the signed root authorization may contain, so a route-selected venue can execute a separately signed child transfer of any token the victim holds while the swap still appears to settle correctly. [7](#0-6) [8](#0-7) 

### Impact Explanation
A victim who signs a presented `swap_collateral`/`multiply` authorization tree can lose arbitrary wallet tokens unrelated to the protocol's listed markets, while the lending operation itself still produces positive measured output and passes final risk checks. [9](#0-8) [10](#0-9)   
This is theft of user funds under a user-interaction precondition, matching the report class where attacker-controlled content causes an unexpected outbound action despite the user's protective configuration/intent. [7](#0-6) 

### Likelihood Explanation
Likelihood is moderate: exploitation needs the victim to sign a poisoned route/auth tree rather than merely call the controller, but the controller gives users no on-chain allowlist or decoded-route bound for venues invoked below the router call, and the measured-input/measured-output checks cannot detect extra signed side effects. [1](#0-0) [11](#0-10) 

### Recommendation
Require a decoded route bound at the controller boundary or require the router to commit to a hash/whitelist of every contract it may invoke, and surface the exact expected authorization tree so clients can reject any child call other than the single intended input transfer. [7](#0-6)   
If opaque routes remain supported, document and enforce that wallets must refuse signatures whose recorded root contains sub-invocations beyond the expected input transfer. [8](#0-7) 

### Proof of Concept
1. Victim owns an account with `USDC` collateral and holds an unrelated `wallet_token`; attacker prepares `swap` bytes whose route names a rogue hop contract. [12](#0-11) 
2. Victim calls `swap_collateral(caller=victim, account_id, current=hub_asset(USDC), amount, new=hub_asset(ETH), swap=poisoned)`; `require_authorized_caller` and `require_owner_or_delegate` pass because it is the victim's own account. [13](#0-12) 
3. `withdraw_and_swap_from_supply` reaches `swap_tokens`, which authorizes only the USDC input transfer but invokes `router.execute_strategy` with the opaque payload. [14](#0-13) 
4. The payload-named rogue venue executes `token.transfer(victim_wallet, attacker, wallet_token_balance)`; if simulation recorded this child under the victim's `swap_collateral` root and the victim signs that tree, the host accepts it while controller balance checks still see bounded input spend and positive ETH output. [9](#0-8) 
5. Result: fair collateral conversion posts normally while the victim's unrelated wallet token is drained. [15](#0-14)

### Citations

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

**File:** contracts/controller/src/strategies/swap.rs (L74-83)
```rust
/// Returns the output balance increase; rejects zero or negative receipts.
fn verify_router_output(env: &Env, token_out: &Address, balance_before: i128) -> i128 {
    let received = balance_delta_since(
        env,
        token_out,
        &env.current_contract_address(),
        balance_before,
    );
    assert_with_error!(env, received > 0, StrategyError::NoSwapOutput);
    received
```

**File:** contracts/controller/src/lib.rs (L280-302)
```rust
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
```

**File:** contracts/controller/src/strategies/swap_collateral.rs (L40-76)
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

**File:** contracts/controller/src/strategies/multiply.rs (L48-97)
```rust
    validate_multiply_request(env, collateral, debt, mode, debt_to_flash_loan);

    let mut cache = Context::new(env);
    let (account_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        mode,
        account::AccountGuard::Multiply,
        &mut cache,
    );
    require_can_supply(env, &mut cache, account.spoke_id, collateral);
    let mut extra_assets = vec![env, collateral.asset.clone(), debt.asset.clone()];
    if let Some((payment, _)) = initial_payment.as_ref() {
        extra_assets.push_back(payment.asset.clone());
    }
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    let (collateral_amount, debt_extra) = collect_initial_multiply_payment(
        env,
        caller,
        collateral,
        debt,
        &initial_payment,
        &convert_swap,
    );

    let amount_received = borrow_into_controller(
        env,
        &mut account,
        debt,
        debt_to_flash_loan,
        true,
        PositionAction::Multiply,
        &mut cache,
    );

    let swap_amount_in = amount_received
        .checked_add(debt_extra)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    let swapped_collateral = swap_tokens_or_passthrough(
        env,
        caller,
        &debt.asset,
        swap_amount_in,
        &collateral.asset,
        swap,
    );
```
