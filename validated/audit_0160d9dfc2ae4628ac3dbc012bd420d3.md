### Title
A ready governance fee update can race `multiply` and withhold unexpected debt proceeds - (File: contracts/pool/src/ops/strategy.rs)

### Summary
`multiply` mints debt for the caller’s requested gross amount but disburses the amount remaining after the market’s current `flashloan_fee`, without accepting a caller-supplied maximum fee or minimum debt-proceeds bound. [1](#0-0) [2](#0-1)   
An unprivileged caller may execute an already-ready `UpgradeLiquidityPoolParams` governance operation immediately before the victim’s `multiply` transaction, causing the newly effective fee rather than the quoted fee to apply. [3](#0-2) [4](#0-3) 

### Finding Description
The public `multiply` entrypoint accepts `debt_to_flash_loan`, collateral, debt asset, swap payloads, and optional payment data, but no expected fee or minimum borrowed-asset receipt parameter. [5](#0-4)   
It calls `borrow_into_controller` with `charge_fee = true`, which delegates strategy funding to the pool and measures the actual token receipt afterward. [6](#0-5) [7](#0-6)   
The pool mints debt for the full requested `amount`, computes `fee` from mutable `cache.params().flashloan_fee`, books that amount as protocol revenue, and transfers only `amount - fee` to the controller. [8](#0-7) [9](#0-8)   
Governance can schedule `AdminOperation::UpgradeLiquidityPoolParams`, whose payload contains an `InterestRateModel` with `flashloan_fee`. [10](#0-9) [11](#0-10)   
Once the timelock operation is ready, `Governance::execute` permits `executor = None`, imposing no executor authentication or role check. [3](#0-2) [4](#0-3)   
The executed controller call replaces the market’s rate model and flash-loan settings before `multiply` reads them. [12](#0-11) [13](#0-12) 

### Impact Explanation
A victim who constructs a `multiply` transaction when the fee is `F_old` can have a ready fee update executed first and therefore receive `amount * (1 - F_new / 10_000)` while owing the full gross `amount`. [14](#0-13)   
The validated maximum fee is `MAX_FLASHLOAN_FEE_BPS = 500`, permitting a legitimate ready operation to withhold up to 5% of the requested debt proceeds. [15](#0-14) [16](#0-15)   
For example, a 1,000-unit strategy borrow at a newly applied 500-bps fee mints 1,000 units of debt but delivers only 950 units to the strategy swap and collateral deposit. [17](#0-16) [18](#0-17)   
This is a Medium-severity unexpected-fee loss because the value is retained as protocol revenue rather than paid directly to the transaction-ordering caller, and the maximum loss is capped at 5%. [19](#0-18) 

### Likelihood Explanation
The attack requires a valid governance operation changing `flashloan_fee` to already be scheduled and in the ready state; an unprivileged attacker cannot choose the new parameter value or execute it before its delay. [20](#0-19) [21](#0-20)   
When such an operation is ready, however, any address can call `execute` with `executor = None` and order that transaction before a pending `multiply`. [3](#0-2) [4](#0-3)   
The victim has no transaction-level bound on the fee because `multiply` lacks a maximum-fee or minimum-debt-proceeds argument and the pool reads the live market parameter at execution. [5](#0-4) [9](#0-8) 

### Recommendation
Add a caller-supplied `max_flashloan_fee_bps` or `min_debt_received` parameter to `multiply` and revert before minting debt if the effective `flashloan_fee` or measured proceeds violate that bound. [6](#0-5) [22](#0-21)   
Alternatively, include the expected market-parameter version or fee value in the signed strategy request and compare it with the value used by `create_strategy`. [23](#0-22) 

### Proof of Concept
1. Governance has a ready, non-expired `UpgradeLiquidityPoolParams` operation for `(hub_id, debt_asset)` whose validated `InterestRateModel.flashloan_fee` is `500`. [10](#0-9) [16](#0-15) 
2. A victim submits `Controller::multiply(caller, account_id, spoke_id, collateral, debt_to_flash_loan = A, debt, mode, swap, initial_payment, convert_swap)` while the active fee is lower. [5](#0-4) 
3. An unprivileged account orders `Governance::execute(None, controller, "upgrade_liquidity_pool_params", [hub_asset, params], predecessor, salt)` before the victim transaction; `None` bypasses executor authorization after readiness and expiry checks. [3](#0-2) [24](#0-23) 
4. The victim’s `multiply` calls `create_strategy` with `charge_fee = true`, mints debt for `A`, computes a 5% fee, books it as revenue, and sends only `0.95 * A` to the controller. [6](#0-5) [25](#0-24) 
5. The controller swaps and deposits only the reduced measured receipt, while the account retains debt corresponding to the full `A`; no argument lets the victim revert on the changed fee. [26](#0-25) [27](#0-26)

### Citations

**File:** contracts/controller/src/strategies/multiply.rs (L76-112)
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

**File:** contracts/pool/src/ops/strategy.rs (L58-82)
```rust
pub(crate) fn accounting(env: &Env, action: PoolAction, charge_fee: bool) -> StrategyOutcome {
    let PoolAction {
        position,
        amount,
        hub_asset,
    } = action;
    require_nonneg_amount(env, amount);

    let mut cache = ops::renewed_market(env, &hub_asset);
    let fee = compute_fee(env, &cache, amount, charge_fee);

    let mut position = Ray::from(position.scaled_amount);
    borrow::mint_debt(env, &mut cache, &mut position, amount);

    let protocol_fee = Ray::from_asset(env, fee, cache.params().asset_decimals);
    interest::add_protocol_revenue(&mut cache, protocol_fee);

    let amount_to_send = amount
        .checked_sub(fee)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.debit_cash(amount_to_send);

    cache.commit();
    let mutation = cache.strategy_mutation(position, amount, amount_to_send);
```

**File:** contracts/pool/src/ops/strategy.rs (L90-100)
```rust
/// Computes the strategy fee from `flashloan_fee` bps when `charge_fee` is true;
/// returns 0 otherwise (does not consult the market flash-loan enable flag).
///
/// Panics if the fee would exceed principal when charging.
fn compute_fee(env: &Env, cache: &Cache, amount: i128, charge_fee: bool) -> i128 {
    if !charge_fee {
        return 0;
    }
    let fee = Bps::from(i128::from(cache.params().flashloan_fee)).flash_loan_fee_on(env, amount);
    assert_with_error!(env, fee <= amount, FlashLoanError::StrategyFeeExceeds);
    fee
```

**File:** contracts/governance/src/api.rs (L53-66)
```rust
    /// Executes a ready, non-expired scheduled op against `target` (not this
    /// contract). If `executor` is `Some`, requires that address to auth and
    /// hold `EXECUTOR_ROLE`; if `None`, no executor role check (anyone may
    /// drive execution of a ready op). Clears scheduled state on success.
    fn execute(
        env: Env,
        executor: Option<Address>,
        target: Address,
        function: Symbol,
        args: Vec<Val>,
        predecessor: BytesN<32>,
        salt: BytesN<32>,
    ) -> Val {
        lifecycle::execute(&env, executor, target, function, args, predecessor, salt)
```

**File:** contracts/governance/src/timelock/mod.rs (L39-48)
```rust
/// Returns the delay, in ledgers, required for operations in `tier`. `Standard`
/// uses the configured minimum delay; `Sensitive` and `Recovery` use that minimum
/// raised to their respective floor constants.
pub(crate) fn operation_delay(env: &Env, tier: DelayTier) -> u32 {
    let min = get_min_delay(env);
    match tier {
        DelayTier::Standard => min,
        DelayTier::Sensitive => min.max(constants::TIMELOCK_SENSITIVE_MIN_DELAY_LEDGERS),
        DelayTier::Recovery => min.max(constants::TIMELOCK_RECOVERY_MIN_DELAY_LEDGERS),
    }
```

**File:** contracts/governance/src/timelock/mod.rs (L75-80)
```rust
/// When `Some(exec)`, requires `exec` auth + `EXECUTOR_ROLE`. When `None`,
/// performs no auth or role check (anyone may drive execution of a ready op).
pub(crate) fn authorize_executor(env: &Env, executor: Option<&Address>) {
    if let Some(exec) = executor {
        exec.require_auth();
        access_control::ensure_role(env, &Symbol::new(env, EXECUTOR_ROLE), exec);
```

**File:** contracts/governance/src/timelock/mod.rs (L179-187)
```rust
/// Renews the governance instance's storage TTL, authorizes `executor` if
/// present, computes `operation`'s id, and checks that the operation has not
/// expired. Returns the operation id.
fn prepare_execute(env: &Env, executor: Option<&Address>, operation: &Operation) -> BytesN<32> {
    renew_instance(env);
    authorize_executor(env, executor);
    let operation_id = hash_operation(env, operation);
    require_operation_not_expired(env, &operation_id);
    operation_id
```

**File:** interfaces/controller/src/lib.rs (L74-86)
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
    ) -> u64;
```

**File:** contracts/controller/src/positions/debt.rs (L260-307)
```rust
pub(crate) fn borrow_into_controller(
    env: &Env,
    account: &mut Account,
    hub_debt: &HubAssetKey,
    amount: i128,
    charge_fee: bool,
    action: events::PositionAction,
    cache: &mut Context,
) -> i128 {
    require_positive_amount(env, amount);
    let aggregated = vec![env, (hub_debt.clone(), amount)];
    validate_position_entry_gates(
        env,
        account,
        &aggregated,
        cache,
        AccountPositionType::Borrow,
    );

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

**File:** interfaces/governance/src/lib.rs (L41-46)
```rust
#[contracttype]
#[derive(Clone, Debug)]
pub struct UpgradePoolParamsArgs {
    pub hub_asset: HubAssetKey,
    pub params: InterestRateModel,
}
```

**File:** interfaces/governance/src/lib.rs (L113-116)
```rust
    RevokeBlendPool(Address),
    CreateLiquidityPool(CreatePoolArgs),
    UpgradeLiquidityPoolParams(UpgradePoolParamsArgs),
    DeployPool(BytesN<32>),
```

**File:** contracts/controller/src/lib.rs (L759-766)
```rust
    /// Accrues market indexes before replacing the interest-rate model.
    /// Owner-only.
    #[only_owner]
    fn upgrade_liquidity_pool_params(env: Env, hub_asset: HubAssetKey, params: InterestRateModel) {
        renew_then!(
            env,
            markets::upgrade_liquidity_pool_params(&env, &hub_asset, &params)
        )
```

**File:** contracts/controller/src/markets.rs (L87-103)
```rust
/// Accrues indexes under the current model before replacing rate and flash-loan
/// parameters, then emits the new configuration.
pub(crate) fn upgrade_liquidity_pool_params(
    env: &Env,
    hub_asset: &HubAssetKey,
    params: &InterestRateModel,
) {
    let mut cache = Context::new(env);

    let pool_addr = cache.cached_pool_address();

    pool_update_indexes_call(env, &pool_addr, &vec![env, hub_asset.clone()]);

    pool_update_params_call(env, &pool_addr, hub_asset, params);

    UpdateMarketParamsEvent::from_rate_model(hub_asset.hub_id, hub_asset.asset.clone(), params)
        .publish(env);
```

**File:** common/src/constants/shared.rs (L45-47)
```rust
/// Upper bound accepted for a pool's configured flash-loan fee, in basis points.
pub const MAX_FLASHLOAN_FEE_BPS: i128 = 500;

```

**File:** common/src/types/pool.rs (L220-224)
```rust
        assert_with_error!(
            env,
            i128::from(self.flashloan_fee) <= MAX_FLASHLOAN_FEE_BPS,
            CollateralError::InvalidBorrowParams
        );
```

**File:** contracts/governance/src/timelock/lifecycle.rs (L81-108)
```rust
/// Executes a scheduled operation against `target` once its delay has elapsed and
/// it has not expired, and returns the invocation's result. Rejects operations
/// that target this contract itself (use `execute_self` for those). Clears the
/// operation's scheduled state on completion.
pub(crate) fn execute(
    env: &Env,
    executor: Option<Address>,
    target: Address,
    function: Symbol,
    args: Vec<Val>,
    predecessor: BytesN<32>,
    salt: BytesN<32>,
) -> Val {
    assert_with_error!(
        env,
        target != env.current_contract_address(),
        GenericError::InternalError
    );
    let operation = Operation {
        target,
        function,
        args,
        predecessor,
        salt,
    };
    let operation_id = prepare_execute(env, executor.as_ref(), &operation);
    let result = execute_operation(env, &operation);
    finish_execute(env, &operation_id);
```
