### Title
Stale pre-callback oracle prices allow undercollateralized flash positions - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`flash_position` caches collateral and debt prices before invoking an attacker-controlled receiver, but performs the post-callback collateral deposit and solvency finalization against that stale `Context` state. A receiver can manipulate a listed collateral’s reachable market price during the callback, return enough nominal collateral to satisfy the stale valuation, and retain value while leaving insolvent debt. This can socialize losses onto suppliers through bad-debt cleanup.

### Finding Description
`process_flash_position` loads strategy prices through `prefetch_strategy_prices` before minting and forwarding debt to `receiver`. [1](#0-0)  The contract then snapshots collateral balances, invokes `execute_flash_position`, and only afterward measures and deposits the returned collateral. [2](#0-1) [3](#0-2) 

`Context` intentionally retains previously fetched prices for the invocation: `fetch_prices` only requests missing assets, while `cached_price` returns the stored feed without checking whether external market state changed. [4](#0-3)  Consequently, a receiver can execute its own Aquarius or Soroswap trade after the pre-fetch and before returning collateral, changing the strict post-trade valuation while the final risk calculation continues to use the earlier price. [5](#0-4) 

This is the XOXNO Lending analogue of the kernel bug’s read/write ordering failure: the price snapshot is read before the callback, external state is mutated during the callback, and the later solvency read incorrectly consumes the pre-mutation snapshot rather than re-reading the changed market state.

### Impact Explanation
An unprivileged caller can use `flash_position` with a caller-controlled receiver, borrow a flashloanable asset, manipulate the selected collateral’s reachable market price downward during the callback, and deposit enough units of that collateral to pass only under the stale higher valuation. [6](#0-5) [7](#0-6) 

The resulting account can be left undercollateralized at the post-manipulation price. Subsequent liquidation and `clean_bad_debt` can convert that shortfall into a supply-index write-down, imposing the loss on suppliers rather than requiring the flash-position initiator to provide sufficient collateral. [8](#0-7) [9](#0-8) 

### Likelihood Explanation
The path is permissionless and requires only an authorized caller, a deployed receiver contract, a flashloanable debt market, and a collateral whose accepted price source can be moved by the receiver’s own trade. [6](#0-5) [10](#0-9)  The host and flash guard prevent re-entering the controller, but they do not prevent the receiver from trading on external venues or otherwise mutating the market inputs represented by the already-cached price. [11](#0-10) 

Feasibility depends on a production market using a price source that the receiver can move within the configured tolerance and on the attacker having sufficient inventory or route liquidity. Those conditions affect magnitude, not the ordering flaw: no post-callback price refresh occurs before collateral measurement and final risk validation. [4](#0-3) [12](#0-11) 

### Recommendation
Do not reuse pre-callback prices for post-callback solvency. After `invoke_receiver` returns, invalidate or reload the debt, collateral, and refund-asset price entries, then perform collateral conversion and the final risk calculation exclusively with the refreshed values. A second strict price read after the callback would preserve existing tolerance and sanity checks while detecting callback-induced price changes.

If intentionally retaining dual prices, bound the position against the less favorable fresh post-callback valuation rather than the earlier cached valuation. Add an adversarial `flash_position` test whose receiver moves a listed collateral’s reachable DEX price after the pre-fetch and before returning the collateral.

### Proof of Concept
1. Configure a market where flash-loanable asset `D` can be minted as flash-position debt and listed collateral `C` has a price source influenced by a reachable Aquarius or Soroswap route.
2. The attacker deploys a receiver implementing `execute_flash_position`.
3. The attacker calls `Controller::flash_position(caller, account_id, spoke_id, mode, D, amount, receiver, data, [(C, min_amount)], refund_assets)`.
4. The controller caches the prices for `D` and `C` before any receiver code executes. [13](#0-12) 
5. The controller mints `D`, verifies receipt, and forwards the measured borrowed amount to the attacker’s receiver. [14](#0-13) 
6. Inside `execute_flash_position`, the receiver sells `C` through the reachable venue, causing the current strict price of `C` to fall relative to the cached pre-callback feed.
7. The receiver returns `min_amount` of `C` to the controller; it may source `C` from pre-funded inventory or from part of the forwarded `D`.
8. The controller measures and deposits `C` after the callback, then finalizes the position using the stale higher `C` price retained in `Context`. [15](#0-14) [4](#0-3) 
9. At the refreshed market price, the deposited `C` no longer covers the outstanding `D` debt. The attacker retains extracted value, while later bad-debt cleanup writes down the market’s supply index and shifts the loss to suppliers.

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L85-111)
```rust
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L113-154)
```rust
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
    require_flash_position_still_open(env, &account, debt);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L260-295)
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L297-323)
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

**File:** contracts/controller/src/context.rs (L141-160)
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
    }
```

**File:** contracts/controller/src/lib.rs (L189-217)
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
        )
    }
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L21-50)
```rust
    let mut entries: Vec<PoolSeizeEntry> = Vec::new(env);
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Supply,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Deposit,
            position: (&position).into(),
        });
    }
    for (hub_asset, position) in iter_debt_positions(&account.borrow_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Borrow,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);

```

**File:** contracts/pool/src/ops/seize.rs (L23-31)
```rust
    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
        AccountPositionType::Deposit => {
            cache.absorb_supply_as_revenue(position);
        }
```
