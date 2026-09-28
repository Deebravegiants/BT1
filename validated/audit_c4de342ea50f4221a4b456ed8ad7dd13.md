### Title
Omitted `refund_assets` permanently traps receiver-returned tokens - ([File: contracts/controller/src/strategies/flash_position.rs])

### Summary
`flash_position` does not verify that every asset returned by the receiver is either deposited as collateral or listed in `refund_assets`. If the receiver returns an otherwise valid listed asset omitted from `refund_assets`, the controller measures the balance increase but never transfers it back. Because later calls snapshot that trapped balance as their baseline, the funds can remain permanently inaccessible to the user.

### Finding Description
The permissionless `flash_position` entry point accepts a caller-selected `collaterals` list and a separate `refund_assets` list. [1](#0-0) 

After minting and forwarding the debt asset, the controller snapshots balances for both lists and invokes the receiver. [2](#0-1) 

The function then deposits only positive deltas for `collaterals` and refunds only positive deltas for the explicitly supplied `refund_assets`. [3](#0-2) 

There is no post-callback reconciliation that checks for balance increases in other listed assets. `validate_refund_assets` merely rejects duplicates, unlisted assets, and assets already used as collateral; it does not require the list to cover every returned asset. [4](#0-3) 

The refund helper transfers only the increase since the balance snapshot and preserves any pre-existing controller balance. [5](#0-4) 

### Impact Explanation
A caller can permanently lose tokens returned by its own receiver. For example, a receiver can return collateral plus some unspent debt asset while `refund_assets` is empty; the collateral delta is deposited, but the debt-asset delta is never refunded. The account still contains open debt and supply, so the operation succeeds and the omitted refund remains in the controller. [6](#0-5) 

A subsequent `flash_position` call cannot recover that old balance through the same mechanism because its pre-callback snapshot includes the trapped balance, making only a new callback-time increase refundable. [7](#0-6) 

### Likelihood Explanation
This requires a mistaken `refund_assets` argument or a receiver that returns an asset the caller did not list. That is plausible because receiver return assets are dynamic callback behavior while `refund_assets` is fixed before the callback runs. [8](#0-7) 

The affected path is reachable by any authorized caller using `account_id = 0`, a deployed WASM receiver, a positive debt amount, and a flashloan-enabled market. [9](#0-8) 

### Recommendation
After the callback, reconcile all listed-asset balance deltas or require the caller to provide a complete expected-refund set. At minimum, snapshot every spoke-listed asset that can legally be returned and revert if an unclaimed positive delta is not represented by either `collaterals` or `refund_assets`.

Alternatively, add a controller recovery entry point that returns only trapped balance deltas attributable to a completed flash-position call, while preserving unrelated protocol funds.

### Proof of Concept
1. User calls `Controller::flash_position` with `account_id = 0`, a valid `debt` market, positive `amount`, a WASM receiver, `collaterals = [(collateral_asset, min)]`, and `refund_assets = []`.
2. The pool mints debt and the controller forwards the measured proceeds to the receiver. [10](#0-9) 
3. During `execute_flash_position`, the receiver transfers `min` collateral and `x` units of the listed debt asset back to the controller.
4. `collect_collateral_deposits` accepts the collateral delta and `process_deposit` records it. [11](#0-10) 
5. `refund_listed_assets` iterates the empty `refund_assets` list, so the `x` debt-token increase remains in the controller. [12](#0-11) 
6. The position remains open and `strategy_finalize` succeeds, completing the transaction while `x` is trapped. [13](#0-12)

### Citations

**File:** contracts/controller/src/lib.rs (L189-215)
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
        strategies::flash_position::process_flash_position(
            &env,
            &caller,
            FlashPositionParams {
                account_id,
                spoke_id,
                mode,
                debt: &debt,
                amount,
                receiver: &receiver,
                data: &data,
                collaterals: &collaterals,
                refund_assets: &refund_assets,
            },
```

**File:** contracts/controller/src/strategies/flash_position.rs (L59-91)
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L120-168)
```rust
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
    require_flash_position_still_open(env, &account, debt);

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

    account_id
```

**File:** contracts/controller/src/strategies/flash_position.rs (L217-255)
```rust
fn validate_refund_assets(
    env: &Env,
    cache: &mut Context,
    spoke_id: u32,
    hub_id: u32,
    collaterals: &Vec<(HubAssetKey, i128)>,
    refund_assets: &Vec<Address>,
) {
    let limits = storage::get_position_limits(env);
    assert_with_error!(
        env,
        refund_assets.len() <= limits.max_supply_positions,
        GenericError::InvalidPayments
    );

    let mut seen: Map<Address, bool> = Map::new(env);
    for asset in refund_assets.iter() {
        assert_with_error!(
            env,
            !seen.contains_key(asset.clone()),
            GenericError::InvalidPayments
        );
        seen.set(asset.clone(), true);
        // Refund transfers run after the guard; restrict tokens to listed assets.
        cache.require_listed_active_config(
            spoke_id,
            &HubAssetKey {
                hub_id,
                asset: asset.clone(),
            },
        );
        for (collateral, _) in collaterals.iter() {
            assert_with_error!(
                env,
                asset != collateral.asset,
                GenericError::InvalidPayments
            );
        }
    }
```

**File:** contracts/controller/src/strategies/flash_position.rs (L258-294)
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

**File:** contracts/controller/src/strategies/flash_position.rs (L372-384)
```rust
fn refund_listed_assets(
    env: &Env,
    caller: &Address,
    refund_assets: &Vec<Address>,
    before: &Map<Address, i128>,
) {
    for asset in refund_assets.iter() {
        let baseline = before
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError));
        refund_controller_balance_delta(env, &asset, baseline, caller);
    }
}
```

**File:** contracts/controller/src/payments.rs (L39-51)
```rust
/// Refunds only the controller balance increase since `balance_before`,
/// preserving the pre-existing balance; no-op for a nonpositive delta.
pub(crate) fn refund_controller_balance_delta(
    env: &Env,
    asset: &Address,
    balance_before: i128,
    refund_to: &Address,
) {
    let controller = env.current_contract_address();
    let excess = balance_delta_since(env, asset, &controller, balance_before);
    if excess > 0 {
        token::Client::new(env, asset).transfer(&controller, refund_to, &excess);
    }
```
