### Title
Stale oracle prices survive an external flash-position callback - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`flash_position` caches all relevant oracle prices before invoking an attacker-controlled receiver, then performs collateral measurement and final solvency checks with that same cached `Context`. Because the callback may execute a ready governance operation that changes the collateral or debt price source, the account is evaluated using a pre-callback price even though the oracle configuration changed during the transaction. [1](#0-0) [2](#0-1) 

### Finding Description
`process_flash_position` loads or creates the attacker's account, validates the declared collateral, and calls `prefetch_strategy_prices` before debt is forwarded or the receiver callback runs. [3](#0-2)  `prefetch_strategy_prices` fills the operation `Context` with the account and strategy asset prices. [4](#0-3) 

The function then mints the requested debt, transfers the measured receipt to the caller-selected receiver, and invokes `execute_flash_position`. [5](#0-4) [6](#0-5)  The strategy borrow itself mints debt shares and sends the net borrowed assets to the controller before forwarding them to the receiver. [7](#0-6) [8](#0-7) 

After the callback, the controller deposits the measured collateral delta and calls `strategy_finalize`, which evaluates post-pool solvency through the same `Context` rather than a refreshed one. [2](#0-1) [9](#0-8)  The context stores token prices and market data for the invocation, and its market-loading API explicitly retains values already cached. [10](#0-9) [11](#0-10)  Consequently, an oracle change performed by the callback does not affect the final collateral valuation.

Governance's ready-operation execution path is callable without privileged executor identity when no executor is supplied. [12](#0-11)  Governance is also the owner/configurer of the price aggregator, including `ConfigureAssetOracle` operations, so a ready repricing operation can be executed from the receiver without re-entering the controller. [13](#0-12) [14](#0-13) 

### Impact Explanation
An attacker can open a leveraged account whose collateral satisfies LTV and health-factor checks only under the stale pre-callback oracle price. The attacker keeps the borrowed assets, while the protocol retains collateral worth materially less under the oracle configuration committed during the same transaction. [2](#0-1) 

This can create immediately undercollateralized debt and, after liquidation and bad-debt cleanup, socialized losses or protocol insolvency. The same pattern applies when a ready operation raises the protocol price of a debt asset after the price has been cached. [15](#0-14) 

### Likelihood Explanation
The attack requires a governance operation that reprices the collateral downward—or the debt upward—to already be ready for execution. No privileged action, leaked key, malicious token, or controller re-entry is required: the attacker supplies only `flash_position`, a deployed receiver, declared collateral, and a public ready-operation execution inside the callback. [16](#0-15) [12](#0-11) 

The borrow amount is bounded by the stale cached price and available pool liquidity, but any positive gap between the stale and committed valuation creates bad debt.

### Recommendation
Do not reuse pre-callback pricing or configuration for post-callback solvency checks. After `invoke_receiver` returns, refresh the relevant oracle prices and spoke/market configuration and require the position to pass under the refreshed values; alternatively, record the relevant oracle/listing/configuration epochs before the callback and revert if any changed before finalization. Preserve pending position events, spoke-usage deltas, and pool-returned market indexes while rebuilding or selectively invalidating the security-sensitive cached fields in `Context`. [17](#0-16) [9](#0-8) 

### Proof of Concept
Assume collateral `C` is currently priced at 100 USD, its LTV is 50%, and ready governance operation `OP` reconfigures `C` to an oracle source reporting 1 USD. Debt asset `D` is priced at 1 USD and is flash-loanable.

1. Attacker deploys receiver `R` holding 10 `C`.
2. Attacker calls:

```rust
flash_position(
    caller = attacker,
    account_id = 0,
    spoke_id = S,
    mode = PositionMode::Multiply,
    debt = D,
    amount = 400 * unit_D,
    receiver = R,
    data = encode(OP),
    collaterals = [(C, 10 * unit_C)],
    refund_assets = [],
)
```

3. `flash_position` caches `C = 100 USD` and `D = 1 USD` before the callback. [18](#0-17) 
4. The controller mints 400 `D` against the new account and forwards it to `R`. [19](#0-18) 
5. Inside `execute_flash_position`, `R` transfers 10 `C` to the controller and executes ready operation `OP`, changing `C`'s protocol valuation to 1 USD. [6](#0-5) 
6. The controller measures and deposits 10 `C`, but `strategy_finalize` still sees the cached 100 USD price. The deposited collateral is treated as 1,000 USD and supports the 400 USD debt. [2](#0-1) 
7. The transaction commits with the attacker holding 400 `D`; under the committed oracle the collateral is worth 10 USD, leaving approximately 390 USD of undercollateralized debt.

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L69-90)
```rust
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L93-123)
```rust
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L131-141)
```rust
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

**File:** contracts/controller/src/strategies/flash_position.rs (L271-294)
```rust
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

**File:** contracts/controller/src/strategies/mod.rs (L35-43)
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

**File:** contracts/pool/src/ops/strategy.rs (L69-80)
```rust
    let mut position = Ray::from(position.scaled_amount);
    borrow::mint_debt(env, &mut cache, &mut position, amount);

    let protocol_fee = Ray::from_asset(env, fee, cache.params().asset_decimals);
    interest::add_protocol_revenue(&mut cache, protocol_fee);

    let amount_to_send = amount
        .checked_sub(fee)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.debit_cash(amount_to_send);

```

**File:** contracts/controller/src/context.rs (L48-60)
```rust
        Context {
            env: env.clone(),
            token_prices: Map::new(env),
            market_indexes: Map::new(env),
            pool_address: None,
            pool_sync_data: Map::new(env),
            spoke_usage: None,
            spoke_config: None,
            spoke_assets: Map::new(env),
            verified_hubs: Map::new(env),
            supply_updates: Vec::new(env),
            debt_updates: Vec::new(env),
        }
```

**File:** contracts/controller/src/context.rs (L68-74)
```rust
    /// Loads missing prices by token address and missing indexes by hub-asset key.
    /// Already cached values are retained.
    pub(crate) fn load_markets(&mut self, hub_assets: &Vec<HubAssetKey>) {
        let assets = unique_hub_tokens(&self.env, hub_assets);
        self.fetch_prices(&assets);
        self.fetch_market_indexes(hub_assets);
    }
```

**File:** docs/explanation/threat-model.md (L67-70)
```markdown
Typed proposals perform proposal-time checks; targets retain execution-time
validation. Ready operations must also be within the grace window. Anyone may
execute with no executor identity; supplying one requires its authorization
and EXECUTOR role. Executor/canceller separation exempts the governance owner.
```

**File:** docs/explanation/threat-model.md (L107-115)
```markdown
and `symbol()` on every `CreateLiquidityPool` proposal and on every
`ConfigureAssetOracle` proposal for a `PriceKey::Token` key, and a failing call
rejects the proposal with `InvalidAsset` (6). Governance uses the live decimals
only while the price aggregator holds no oracle for the token. Otherwise
`resolve_oracle` uses the stored oracle's `asset_decimals`, and
`CreateLiquidityPool` checks `asset_decimals` against the same value. The price
aggregator rejects a replacement oracle that changes the stored
`asset_decimals` with `InvalidOracleDecimals` (221). Thus oracle maintenance
keeps the listed decimals after a relabel, and a listing in a second hub must
```

**File:** docs/reference/architecture.md (L38-46)
```markdown
| Position NFT | Account ownership, holder/approved transfers, and controller-authorized mint, burn, and upgrade |
| Price aggregator | Source configuration, validated price reads, and owner-authorized upgrades |
| XOXNO oracle | Authenticated signer submissions and threshold-based aggregation |
| Swap aggregator | Route execution, fees, and venue calls |
| DeFindex adapter | Supply-only controller accounts keyed by authenticated vault address |

Governance's deployment helpers make governance the owner of the controller
and price aggregator. The controller deploys one pool and one position NFT
with itself as their authority. The pool has no separate ownership-transfer
```

**File:** contracts/controller/src/risk/totals.rs (L171-207)
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
        let gate_value = position_value_floor(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

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
