### Title

`flash_position` lets users avoid the strategy origination fee charged by `multiply` - ([File: contracts/controller/src/strategies/flash_position.rs])

### Summary

An unprivileged user can open the same leveraged account through `flash_position` without paying the `flashloan_fee` withheld when opening it through `multiply`. [1](#0-0) [2](#0-1) 

### Finding Description

`multiply` calls `borrow_into_controller` with `charge_fee = true`, causing the pool to withhold `flashloan_fee` basis points of the borrowed principal as protocol revenue and forward only `amount - fee`. [1](#0-0) [3](#0-2) [4](#0-3) 

`flash_position` accepts `PositionMode::Multiply`, `Long`, or `Short`, mints the same type of strategy debt, but calls `borrow_into_controller` with `charge_fee = false`. [5](#0-4) [2](#0-1) 

The attacker-controlled Wasm receiver receives the full measured debt proceeds, returns collateral to the controller, and the controller deposits those measured receipts before running the same account solvency finalization used by `multiply`. [6](#0-5) [7](#0-6) [8](#0-7) 

A caller can therefore submit `flash_position(caller, account_id=0, spoke_id, mode=Multiply, debt, amount, receiver=attacker_contract, data, collaterals=[(collateral_asset, min_amount)], refund_assets=[])` and obtain comparable debt and collateral without the origination fee. [9](#0-8) [10](#0-9) 

### Impact Explanation

The bypassed fee is protocol revenue that `multiply` would have retained in pool cash and minted as revenue shares, while `flash_position` books no fee and emits `fee: 0`. [11](#0-10) [12](#0-11) 

The attacker captures the skipped fee as additional borrowed proceeds and ending collateral while incurring the same debt principal. [13](#0-12) 

This is repeatable for every strategy opened through the fee-free path and directly transfers value that would otherwise become protocol revenue to the position owner. [14](#0-13) [15](#0-14) 

### Likelihood Explanation

Only caller authorization, a Wasm receiver, a positive amount, an eligible strategy mode, a flash-loanable debt market, collateral that meets the caller-provided minimums, and post-operation solvency are required. [16](#0-15) [17](#0-16) [10](#0-9) [18](#0-17) 

No privileged role, timing window, oracle manipulation, or special receiver approval is needed because the attacker may deploy and specify the receiver contract. [19](#0-18) [20](#0-19) 

### Recommendation

Charge the same `flashloan_fee` in `flash_position::mint_and_forward` by passing `charge_fee = true` to `borrow_into_controller`. [21](#0-20) 

Propagate the actual withheld fee, derived as `amount - amount_received` or returned by the pool, to the receiver callback and `FlashPositionEvent` instead of the currently hard-coded zero. [22](#0-21) [12](#0-11) 

Alternatively, disable `PositionMode::Multiply`, `Long`, and `Short` account creation through `flash_position` if fee-free debt is intentionally reserved for a separate migration mechanism rather than arbitrary user-selected receivers. [23](#0-22) 

### Proof of Concept

The repository already contains a parity test that opens comparable leverage through both routes. [24](#0-23) 

For the charged route, `multiply` borrows 1 ETH, swaps the fee-reduced proceeds for USDC collateral, and books the configured fee as ETH-market revenue. [25](#0-24) 

For the bypass route, a deployed receiver returns 3,000 USDC and the caller invokes `flash_position` in `Multiply` mode with a 2,990 USDC minimum collateral receipt. [26](#0-25) 

The test asserts comparable debt, exact nonzero revenue for `multiply`, zero revenue for `flash_position`, and greater final collateral for `flash_position`. [13](#0-12)

### Citations

**File:** contracts/controller/src/strategies/multiply.rs (L76-84)
```rust
    let amount_received = borrow_into_controller(
        env,
        &mut account,
        debt,
        debt_to_flash_loan,
        true,
        PositionAction::Multiply,
        &mut cache,
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L40-45)
```rust
pub(crate) fn process_flash_position(
    env: &Env,
    caller: &Address,
    params: FlashPositionParams<'_>,
) -> u64 {
    require_authorized_caller(env, caller);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L59-84)
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L85-90)
```rust
    // Caller-selected receivers require flash loans enabled; multiply uses
    // the configured router and does not require this flag.
    assert_with_error!(
        env,
        cache.cached_pool_sync_data(debt).params.is_flashloanable,
        FlashLoanError::FlashloanNotEnabled
```

**File:** contracts/controller/src/strategies/flash_position.rs (L119-143)
```rust
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L145-154)
```rust
    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
    require_flash_position_still_open(env, &account, debt);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L156-166)
```rust
    FlashPositionEvent {
        account_id,
        hub_id: debt.hub_id,
        asset: debt.asset.clone(),
        receiver: receiver.clone(),
        caller: caller.clone(),
        amount,
        amount_received,
        fee: 0,
    }
    .publish(env);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L258-279)
```rust
/// Mints fee-free debt, verifies the controller receipt against the pool result,
/// then forwards it and returns the receiver's measured receipt.
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L297-322)
```rust
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
```

**File:** contracts/pool/src/ops/strategy.rs (L53-57)
```rust
/// Computes the fee, mints debt for `action.amount`, and debits cash for
/// `amount - fee`.
///
/// The fee stays in the pool as protocol revenue via
/// [`interest::add_protocol_revenue`].
```

**File:** contracts/pool/src/ops/strategy.rs (L67-79)
```rust
    let fee = compute_fee(env, &cache, amount, charge_fee);

    let mut position = Ray::from(position.scaled_amount);
    borrow::mint_debt(env, &mut cache, &mut position, amount);

    let protocol_fee = Ray::from_asset(env, fee, cache.params().asset_decimals);
    interest::add_protocol_revenue(&mut cache, protocol_fee);

    let amount_to_send = amount
        .checked_sub(fee)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.debit_cash(amount_to_send);
```

**File:** contracts/pool/src/ops/strategy.rs (L94-100)
```rust
fn compute_fee(env: &Env, cache: &Cache, amount: i128, charge_fee: bool) -> i128 {
    if !charge_fee {
        return 0;
    }
    let fee = Bps::from(i128::from(cache.params().flashloan_fee)).flash_loan_fee_on(env, amount);
    assert_with_error!(env, fee <= amount, FlashLoanError::StrategyFeeExceeds);
    fee
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

**File:** contracts/controller/src/lib.rs (L189-201)
```rust
    fn flash_position(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        mode: PositionMode,
        debt: HubAssetKey,
        amount: i128,
        receiver: Address,
        data: Bytes,
        collaterals: Vec<(HubAssetKey, i128)>,
        refund_assets: Vec<Address>,
    ) -> u64 {
```

**File:** tests/test-harness/tests/strategy_origination_fee_parity.rs (L1-7)
```rust
//! `flash_position` opens the same leveraged position as `multiply` without the
//! strategy origination fee.
//!
//! `multiply` mints strategy debt with `charge_fee = true`, so the pool withholds
//! `flashloan_fee` bps as protocol revenue. `flash_position` mints the same
//! strategy debt with `charge_fee = false`. Both routes end with new debt and new
//! measured collateral on one account, checked by the same `strategy_finalize`.
```

**File:** tests/test-harness/tests/strategy_origination_fee_parity.rs (L33-50)
```rust
fn open_via_multiply() -> (f64, f64, i128) {
    let mut t = setup();
    t.fund_router("USDC", 3_000.0);

    let net_in = apply_flash_fee(10_000_000);
    // The mock router pays exactly `min_out`. Scale it by the fee the pool
    // withholds: `multiply` has only `amount - fee` of ETH to sell.
    let steps = build_aggregator_swap(&t, "ETH", "USDC", net_in, apply_flash_fee(30_000_000_000));

    let revenue_before = t.snapshot_revenue("ETH");
    let account_id = t.multiply(ALICE, "USDC", 1.0, "ETH", PositionMode::Multiply, &steps);
    let revenue_after = t.snapshot_revenue("ETH");

    (
        t.supply_balance_for(ALICE, account_id, "USDC"),
        t.borrow_balance_for(ALICE, account_id, "ETH"),
        revenue_after - revenue_before,
    )
```

**File:** tests/test-harness/tests/strategy_origination_fee_parity.rs (L56-86)
```rust
fn open_via_flash_position() -> (f64, f64, i128) {
    let mut t = setup();
    let receiver = t.deploy_flash_position_receiver();

    // The receiver mints and pushes back 3_000 USDC: the `multiply` router
    // output for 1.0 ETH with no fee withheld.
    let request = FlashPositionRequest {
        mode: FlashPositionMode::Success,
        collateral: t.resolve_asset("USDC"),
        collateral_amount: f64_to_i128(3_000.0, t.resolve_market("USDC").decimals),
        extra_asset: Address::generate(&t.env),
        extra_amount: 0,
        reenter_spoke_id: HARNESS_SPOKE,
        reenter_account_id: 0,
    };
    let payload: Bytes = request.to_xdr(&t.env);
    let mins = collaterals(&t, "USDC", 2_990.0);
    let refunds = Vec::new(&t.env);

    let revenue_before = t.snapshot_revenue("ETH");
    let account_id = t.flash_position(
        ALICE,
        0,
        PositionMode::Multiply,
        "ETH",
        1.0,
        &receiver,
        &payload,
        &mins,
        &refunds,
    );
```

**File:** tests/test-harness/tests/strategy_origination_fee_parity.rs (L104-129)
```rust
    // Same debt taken on both routes.
    assert!(
        (mul_debt - fp_debt).abs() < 0.01,
        "routes should take comparable debt: multiply={mul_debt} flash_position={fp_debt}"
    );

    // `multiply` books exactly the fee on 1.0 ETH of strategy debt at
    // `DEFAULT_FLASHLOAN_FEE_BPS`; `flash_position` books nothing.
    let strategy_debt_raw = 10_000_000i128;
    let expected_fee = strategy_debt_raw - apply_flash_fee(strategy_debt_raw);
    assert_eq!(
        mul_revenue, expected_fee,
        "multiply must book exactly the origination fee on {strategy_debt_raw} \
         raw ETH of debt: expected {expected_fee}, got {mul_revenue}"
    );
    assert_eq!(
        fp_revenue, 0,
        "flash_position books no protocol revenue, got {fp_revenue}"
    );

    // The fee-free route ends with more collateral for the same debt.
    assert!(
        fp_collateral > mul_collateral,
        "flash_position should yield more collateral for the same debt: \
         multiply={mul_collateral} flash_position={fp_collateral}"
    );
```
