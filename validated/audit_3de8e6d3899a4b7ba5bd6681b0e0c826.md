### Title

Stale pre-callback oracle prices let `flash_position` persist post-oracle-change insolvency - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary

`flash_position` caches all debt and collateral prices before forwarding newly minted debt to an arbitrary Wasm receiver, then reuses those cached prices for post-callback solvency checks. [1](#0-0)  A receiver can execute an unrelated external state transition during the callback, including a ready governance operation that changes the relevant oracle configuration or price, while the controller still evaluates the final position with the pre-callback values. [2](#0-1)  This can leave a newly opened account undercollateralized immediately after it is persisted while the receiver retains the borrowed assets. [3](#0-2) 

### Finding Description

`process_flash_position` builds one `Context`, validates the account and requested collateral, and calls `prefetch_strategy_prices` before any external callback. [4](#0-3)  `prefetch_strategy_prices` calls `Context::fetch_prices`, and `fetch_prices` only requests assets missing from the invocation-local `token_prices` map; it never refreshes a cached value. [5](#0-4) [6](#0-5) 

Inside `with_flash_guard`, `mint_and_forward` mints the requested debt to the controller, verifies the measured receipt, and transfers the measured amount to the receiver. [7](#0-6)  The controller then snapshots declared collateral and refund balances and invokes `execute_flash_position` on the caller-selected receiver. [8](#0-7) [9](#0-8)  Controller reentry is blocked, but the callback can invoke unrelated contracts, including the configured router and other non-controller contracts. [10](#0-9)  A ready governance operation is an allowed external transition in scope. 

After the callback returns, the controller measures declared collateral deltas and deposits them through `process_deposit`. [11](#0-10) [12](#0-11)  `strategy_finalize` then calls `enforce_post_pool_solvency`, and the solvency calculation reads each asset through `cached_price` rather than querying the aggregator again. [13](#0-12) [14](#0-13)  The resulting debt total and health factor are therefore computed from the stale `PriceFeedRaw` values fetched before the callback. [15](#0-14) 

The vulnerable sequence is: price cache → mint and forward debt → receiver changes oracle state through a separate contract → controller deposits collateral → stale cached-price solvency gate → persist debt and supply. [16](#0-15)  This is the same defect class as the referenced kernel issue: a mutable condition is checked or captured before a wait/callback, and the changed condition is not rechecked after execution resumes. 

### Impact Explanation

An attacker can create an account with `account_id = 0`, choose a flash-loan-enabled debt market, mint fee-free debt, and keep the forwarded debt in the receiver because `flash_position` does not pull repayment. [17](#0-16) [18](#0-17)  If the callback executes a ready oracle-changing operation that lowers the collateral price or raises the debt price, finalization can pass using the obsolete price while a fresh valuation would fail the LTV or health-factor gates. [19](#0-18) 

The account can then hold less current collateral value than outstanding debt, while the borrowed tokens have already left the pool. [20](#0-19)  A later liquidation may seize the collateral but fail to cover the debt, and residual insolvency can be socialized through the bad-debt path, imposing the loss on suppliers. [21](#0-20)  The impact is theft of pool funds or protocol insolvency, with scale bounded by market liquidity, utilization/cap checks, and the magnitude of the oracle transition. [22](#0-21) 

### Likelihood Explanation

The attack requires a governance operation affecting a relevant price to be ready for execution during the callback, so the attacker cannot choose arbitrary oracle values on demand.  When such an operation is pending, an unprivileged caller can time `flash_position` around it and use a custom Wasm receiver to execute it inside the callback. [23](#0-22)  No controller reentry, privileged key, malicious token, or protocol parameter change controlled directly by the attacker is needed. [10](#0-9) 

`flash_position` is the strongest affected path because it both mints debt and gives it to attacker-controlled code before the stale final risk evaluation. [24](#0-23)  The same stale-cache pattern also exists around router and Blend calls in `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, and `migrate_from_blend`, which likewise prefetch prices before external execution and call `strategy_finalize` afterward. [25](#0-24) [26](#0-25) 

### Recommendation

Do not reuse pre-callback prices for post-callback solvency decisions. [2](#0-1)  After `invoke_receiver` returns, force-refresh every price used by finalization—either by adding a `Context::refresh_prices` path that overwrites existing entries or by performing final risk checks with a fresh price context. [3](#0-2)  Apply the same refresh-after-external-call rule to the router and Blend strategy paths before `strategy_finalize`. [27](#0-26) 

Alternatively, record a governance/oracle configuration epoch before external execution and reject the transaction if that epoch changes, but a refreshed strict price read is more direct and also covers non-governance state transitions. 

### Proof of Concept

Assume a listed collateral token `COL`, a flash-loan-enabled debt token `DEBT`, and a ready governance operation `op_id` whose execution changes `COL`’s resolved price from `P_old` to `P_new < P_old`. 

1. Deploy receiver contract `R`, which implements `execute_flash_position(initiator, account_id, asset, amount, fee, amount_received, controller, data)` and holds or obtains `C` units of `COL`. [9](#0-8) 
2. Choose `A` and `C` such that `A * P_debt <= C * P_old * LTV`, so the stale valuation passes, but `A * P_debt > C * P_new * liquidation_threshold`, so the fresh health factor is below one. [28](#0-27) 
3. The attacker calls `controller.flash_position(caller, 0, spoke_id, PositionMode::Multiply, {hub_id, DEBT}, A, R, data, vec![({hub_id, COL}, C)], vec![])`. [29](#0-28) 
4. The controller caches `COL` at `P_old` and `DEBT` at `P_debt` before the callback. [30](#0-29) 
5. The controller mints `A` units of debt to the account, sends the measured amount to `R`, and invokes `R.execute_flash_position`. [31](#0-30) 
6. Inside the callback, `R` executes `op_id` through governance, changing the `COL` oracle result to `P_new`, then transfers `C` units of `COL` to the controller. 
7. After the callback, the controller measures and deposits `C`, but `strategy_finalize` still uses cached `P_old`, so the LTV and health-factor gates pass. [3](#0-2) [2](#0-1) 
8. The transaction persists an account with positive `DEBT` and `COL` positions; `require_flash_position_still_open` confirms both sides remain open, but it does not recheck oracle freshness. [32](#0-31) 
9. A subsequent fresh valuation returns `P_new`, reports health factor below one, and liquidation of the deposited `COL` cannot cover the outstanding `DEBT`. [33](#0-32)

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L40-57)
```rust
pub(crate) fn process_flash_position(
    env: &Env,
    caller: &Address,
    params: FlashPositionParams<'_>,
) -> u64 {
    require_authorized_caller(env, caller);

    let FlashPositionParams {
        account_id,
        spoke_id,
        mode,
        debt,
        amount,
        receiver,
        data,
        collaterals,
        refund_assets,
    } = params;
```

**File:** contracts/controller/src/strategies/flash_position.rs (L59-153)
```rust
    require_positive_amount(env, amount);
    config::require_hub_active(env, debt.hub_id);
    assert_with_error!(
        env,
        matches!(
            mode,
            PositionMode::Multiply | PositionMode::Long | PositionMode::Short
        ),
        CollateralError::InvalidPositionMode
    );
    require_wasm_receiver(env, receiver);

    let controller = env.current_contract_address();
    assert_with_error!(
        env,
        *receiver != controller,
        FlashLoanError::InvalidFlashloanReceiver
    );

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    assert_with_error!(
        env,
        *receiver != pool_addr,
        FlashLoanError::InvalidFlashloanReceiver
    );
    // Caller-selected receivers require flash loans enabled; multiply uses
    // the configured router and does not require this flag.
    assert_with_error!(
        env,
        cache.cached_pool_sync_data(debt).params.is_flashloanable,
        FlashLoanError::FlashloanNotEnabled
    );

    let (account_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        mode,
        account::AccountGuard::Multiply,
        &mut cache,
    );

    validate_collaterals(env, &mut cache, &account, collaterals);
    validate_refund_assets(
        env,
        &mut cache,
        account.spoke_id,
        debt.hub_id,
        collaterals,
        refund_assets,
    );

    let mut extra_assets = vec![env, debt.asset.clone()];
    for (hub_asset, _) in collaterals.iter() {
        extra_assets.push_back(hub_asset.asset.clone());
    }
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    // Guard both forwarding and the callback: token hooks can reenter first.
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });

    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L260-323)
```rust
fn mint_and_forward(
    env: &Env,
    account: &mut Account,
    debt: &HubAssetKey,
    amount: i128,
    receiver: &Address,
    cache: &mut Context,
) -> i128 {
    let controller = env.current_contract_address();
    let before = token::Client::new(env, &debt.asset).balance(&controller);

    let reported = borrow_into_controller(
        env,
        account,
        debt,
        amount,
        false,
        PositionAction::FlashPos,
        cache,
    );

    let measured = balance_delta_since(env, &debt.asset, &controller, before);
    assert_with_error!(env, measured == reported, GenericError::InternalError);
    assert_with_error!(env, measured > 0, GenericError::AmountMustBePositive);

    let forwarded = transfer_amount_measured(
        env,
        &debt.asset,
        &controller,
        receiver,
        measured,
        GenericError::AmountMustBePositive,
    );
    assert_with_error!(env, forwarded > 0, GenericError::AmountMustBePositive);
    forwarded
}

fn invoke_receiver(
    env: &Env,
    receiver: &Address,
    initiator: &Address,
    account_id: u64,
    asset: &Address,
    amount: i128,
    amount_received: i128,
    controller: &Address,
    data: &Bytes,
) {
    env.invoke_contract::<()>(
        receiver,
        &Symbol::new(env, "execute_flash_position"),
        (
            initiator.clone(),
            account_id,
            asset.clone(),
            amount,
            0i128,
            amount_received,
            controller.clone(),
            data.clone(),
        )
            .into_val(env),
    );
}
```

**File:** contracts/controller/src/strategies/flash_position.rs (L325-351)
```rust
fn collect_collateral_deposits(
    env: &Env,
    controller: &Address,
    collaterals: &Vec<(HubAssetKey, i128)>,
    before: &Map<Address, i128>,
) -> Vec<(HubAssetKey, i128)> {
    let mut deposits: Vec<(HubAssetKey, i128)> = Vec::new(env);
    for (hub_asset, min_amount) in collaterals.iter() {
        let baseline = before
            .get(hub_asset.asset.clone())
            .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError));
        let delta = balance_delta_since(env, &hub_asset.asset, controller, baseline);
        assert_with_error!(
            env,
            delta >= min_amount,
            StrategyError::CollateralMinimumNotMet
        );
        if delta > 0 {
            deposits.push_back((hub_asset, delta));
        }
    }
    assert_with_error!(
        env,
        !deposits.is_empty(),
        StrategyError::CollateralMinimumNotMet
    );
    deposits
```

**File:** contracts/controller/src/strategies/flash_position.rs (L354-370)
```rust
/// Requires positive scaled debt in the borrowed market and remaining supply
/// so the flash-position flow cannot finish as an empty round trip.
pub(crate) fn require_flash_position_still_open(env: &Env, account: &Account, debt: &HubAssetKey) {
    assert_with_error!(
        env,
        !account.is_empty() && !account.debt_free(),
        StrategyError::FlashPositionClosed
    );
    let Some(pos) = account.borrow_positions.get(debt.clone()) else {
        panic_with_error!(env, StrategyError::FlashPositionClosed);
    };
    assert_with_error!(
        env,
        pos.scaled_amount > 0 && !account.supply_positions.is_empty(),
        StrategyError::FlashPositionClosed
    );
}
```

**File:** contracts/controller/src/context.rs (L141-159)
```rust
    /// Fetches missing prices in one aggregator call; retains cached prices.
    pub(crate) fn fetch_prices(&mut self, assets: &Vec<Address>) {
        let missing = collect_uncached_keys(&self.env, assets, &self.token_prices);
        if missing.is_empty() {
            return;
        }
        let fetched = external::price_aggregator::fetch_prices(&self.env, &missing);
        for (asset, feed) in fetched.iter() {
            self.token_prices.set(asset, feed);
        }
    }

    /// Returns a previously loaded price; fails if the cache has no entry.
    pub(crate) fn cached_price(&mut self, asset: &Address) -> PriceFeed {
        let raw = self
            .token_prices
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(&self.env, OracleError::OracleNotConfigured));
        (&raw).into()
```

**File:** contracts/controller/src/strategies/mod.rs (L35-55)
```rust
/// Caches account and extra-asset prices before strategy funding or callbacks.
pub(crate) fn prefetch_strategy_prices(
    cache: &mut Context,
    account: &Account,
    extra_assets: &Vec<Address>,
) {
    let assets = account_price_assets(cache.env(), account, extra_assets);
    cache.fetch_prices(&assets);
}

/// Refreshes listed collateral LTV, checks solvency, health and collateral floor,
/// then persists positions and spoke usage, removes an empty account, and emits
/// the position batch.
pub(crate) fn strategy_finalize(
    env: &Env,
    account_id: u64,
    account: &mut Account,
    cache: &mut Context,
) {
    let _ = enforce_post_pool_solvency(env, cache, account);
    finalize_position_flow(env, account_id, account, cache, PositionSides::Both, true);
```

**File:** skills/xoxno-lending-contracts/flash-loans.md (L203-214)
```markdown
## Reentrancy

The Soroban host rejects a call into a contract that is already on the call
stack with `Error(Context, InvalidAction)`. A callback therefore cannot call
the controller, including its views, and a `flash_loan` callback cannot call
the pool. The controller flash guard is a second layer: it blocks user
position verbs, strategy verbs, keeper updates, revenue claims, liquidation,
bad-debt cleanup, and recapitalization. Do not design a callback that calls
the controller.

The router is a separate contract and may be called inside a callback with its
own exact token authorization.
```

**File:** contracts/controller/src/positions/supply.rs (L114-134)
```rust
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolSupplyEntry> = Vec::new(env);
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_supply_leg(env, account, &entry.action, &result, cache);
```

**File:** contracts/controller/src/risk/totals.rs (L171-180)
```rust
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );
```

**File:** contracts/controller/src/risk/totals.rs (L188-207)
```rust
        total_collateral = total_collateral.checked_add(env, value);
        // A gated threshold can stay below refreshed LTV; clamp the borrow limit to it.
        let effective_ltv = position.loan_to_value.min(position.liquidation_threshold);
        ltv_collateral =
            ltv_collateral.checked_add(env, effective_ltv.apply_to_wad_floor(env, gate_value));
        weighted_collateral = weighted_collateral.checked_add(
            env,
            position
                .liquidation_threshold
                .apply_to_wad_floor(env, gate_value),
        );
    }

    let total_debt = sum_debt_usd_loaded(env, cache, borrow_positions, position_value_ceil);

    let health_factor = if total_debt == Wad::ZERO {
        Wad::from(i128::MAX)
    } else {
        weighted_collateral.div_floor_saturating(env, total_debt)
    };
```

**File:** contracts/controller/src/risk/validation.rs (L29-58)
```rust
pub(crate) fn require_post_pool_risk_gates(env: &Env, cache: &mut Context, account: &Account) {
    if account.debt_free() {
        return;
    }

    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    assert_with_error!(
        env,
        totals.ltv_collateral >= totals.total_debt,
        CollateralError::InsufficientCollateral
    );

    spec_hooks::solvency_gate_checked(account);

    assert_with_error!(
        env,
        totals.health_factor >= Wad::ONE,
        CollateralError::InsufficientCollateral
    );

    let floor = storage::get_min_borrow_collateral_usd_wad(env);
    if floor != 0 && totals.ltv_collateral.raw() < floor {
        panic_with_error!(env, CollateralError::MinBorrowCollateralNotMet);
    }
```

**File:** contracts/controller/src/positions/debt.rs (L279-307)
```rust
    let position = account.get_or_create_debt_position(hub_debt);
    let pool_addr = cache.cached_pool_address();
    let pool_action = make_pool_action(&position, amount, hub_debt.clone());
    let controller = env.current_contract_address();
    let before = token::Client::new(env, &hub_debt.asset).balance(&controller);
    // Block token-hook reentry during funding, before the strategy swap guard.
    let result = storage::with_flash_guard(env, || {
        pool_create_strategy_call(env, &pool_addr, &controller, pool_action, charge_fee)
    });
    let measured = payments::balance_delta_since(env, &hub_debt.asset, &controller, before);
    assert_with_error!(
        env,
        measured == result.amount_received,
        GenericError::InternalError
    );
    assert_with_error!(env, measured > 0, GenericError::AmountMustBePositive);
    let mutation = PoolPositionMutation::from(&result);
    merge_debt_leg(
        env,
        account,
        action,
        hub_debt,
        LegDirection::Entry {
            asset_decimals: mutation.asset_decimals,
        },
        &LegOutcome::from(&mutation),
        cache,
    );
    measured
```

**File:** contracts/controller/README.md (L77-79)
```markdown
| `liquidate` | `fn liquidate( env: Env, liquidator: Address, account_id: u64, debt_payments: Vec<(HubAssetKey, i128)>, seize_mode: SeizeMode, ) -> u64` | — | Liquidates `account_id` by having `liquidator` repay `debt_payments` and seizing collateral at a bonus scaled by the account's health factor. Returns the `Credit` receiver's account id, or 0 for `Transfer`. |
| `clean_bad_debt` | `fn clean_bad_debt(env: Env, caller: Address, account_id: u64)` | — | Socializes `account_id`'s debt into the supply index and removes the account when it is insolvent and its remaining collateral value is at or below the dust threshold; reverts otherwise. |

```

**File:** contracts/pool/src/ops/borrow.rs (L63-79)
```rust
pub(crate) fn mint_debt(env: &Env, cache: &mut Cache, position: &mut Ray, amount: i128) {
    require_positive_amount(env, amount);
    cache.require_reserves(amount);
    guards::require_liquidation_buffer(env, cache, amount);

    let minted = cache.calculate_scaled_borrow(amount);

    assert_with_error!(
        env,
        minted.raw() > 0,
        GenericError::BorrowRoundsToZeroShares
    );

    *position = position.checked_add(env, minted);
    cache.mint_debt(minted);
    guards::require_utilization_below_max(env, cache);
}
```

**File:** contracts/controller/src/strategies/multiply.rs (L60-112)
```rust
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

    let total_collateral = collateral_amount
        .checked_add(swapped_collateral)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    let deposit_assets = vec![env, (collateral.clone(), total_collateral)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L52-87)
```rust
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

    repay_debt_from_controller(
        env,
        &mut account,
        &mut cache,
        caller,
        StrategyRepay {
            debt: existing_debt,
            debt_available: repay_amount,
            debt_pos: &existing_pos,
            action: PositionAction::SwDebtR,
        },
    );

    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/views.rs (L29-49)
```rust
/// debt or does not exist.
pub(crate) fn health_factor(env: &Env, account_id: u64) -> i128 {
    let mut cache = Context::new_view(env);
    match storage::try_get_account(env, account_id) {
        Some(account) if !account.debt_free() => risk::calculate_account_risk_totals(
            env,
            &mut cache,
            &account.supply_positions,
            &account.borrow_positions,
        )
        .health_factor
        .raw(),
        _ => i128::MAX,
    }
}

/// Returns whether the account's health factor is below 1.0 (WAD), making it
/// eligible for liquidation.
pub(crate) fn can_be_liquidated(env: &Env, account_id: u64) -> bool {
    health_factor(env, account_id) < WAD
}
```
