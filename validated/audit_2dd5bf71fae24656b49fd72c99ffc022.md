### Title
Interest accrual overflows `i128` on near-max scaled totals and permanently freezes a market - (File: common/src/rates/index.rs)

### Summary
The integer-overflow class maps to the pool's RAY-scaled market totals: `accrue_step` and `update_supply_index` calculate `scaled * index` and add rewards in `i128`, even though individually valid supply, debt, and index values can make those products unrepresentable. Because every pool mutation performs accrual before executing the requested action, the first overflow prevents all later repayment, withdrawal, liquidation, and index updates for that market. [1](#0-0) [2](#0-1) 

### Finding Description
`global_sync` calls `accrue_step` before marking the market accrued, and `accrue_step` computes both `borrowed * borrow_index` and `supplied * supply_index`. [3](#0-2) [4](#0-3)  `Ray::mul` delegates to exact multiply-divide arithmetic and panics when the resulting value cannot fit in `i128`; the intermediate product can be widened to `I256`, but the final market value cannot exceed `i128::MAX`. [5](#0-4) [6](#0-5) 

The overflow can also occur directly in `update_supply_index`: it calculates `total_supplied_value = supplied * old_index`, then calls `checked_add(total_supplied_value, rewards_increase)`, while `Ray::checked_add` panics on `i128` overflow. [7](#0-6) [8](#0-7)  The index ceilings bound the indexes themselves, but do not constrain `scaled * index`; `borrow_index` is capped at `MAX_BORROW_INDEX_RAY`, and `supply_index` is capped at `MAX_SUPPLY_INDEX_RAY`. [9](#0-8) [10](#0-9) 

All ordinary pool legs call `ops::load_leg`, which calls `synced_market` and therefore `global_sync` before supply, borrow, withdrawal, repayment, net settlement, or strategy accounting. [2](#0-1)  The explicit `update_indexes` path also loads the market and runs `global_sync` before committing, so once accrual overflows, `last_timestamp` is not advanced and every later attempt repeats the same panic. [11](#0-10) 

### Impact Explanation
Once a market reaches an overflowing scaled-value state, suppliers cannot withdraw, borrowers cannot repay, liquidators cannot progress the market, keepers cannot update its indexes, and governance cannot replace its rate model because `update_params` also accrues under the old model first. [12](#0-11) [13](#0-12) [14](#0-13)  This causes market-wide, permanent freezing of deposited funds and unclaimed yield under the deployed code. [3](#0-2) [11](#0-10) 

### Likelihood Explanation
The condition requires a market book near the admitted RAY-domain limit and enough accrued value to push either `supplied * supply_index` or `borrowed * borrow_index` over `i128::MAX`. [1](#0-0) [15](#0-14)  The protocol permits token inputs up to approximately `i128::MAX / 10^(27-decimals)` and index growth up to `10^36`, so configured caps can admit states whose scaled totals are valid at index `RAY` but become unrepresentable after accrual. [16](#0-15) [9](#0-8)  An unprivileged attacker can establish the large position through ordinary `supply` and `borrow`, then trigger accrual with `Controller::update_indexes(caller, hub_assets)`; the controller forwards the supplied `Vec<HubAssetKey>` to the pool's owner-authenticated `update_indexes` call. [17](#0-16) [18](#0-17) 

### Recommendation
Constrain scaled market totals against the maximum index ratio, not merely `i128::MAX` shares: for example, require `supplied <= i128::MAX * RAY / MAX_SUPPLY_INDEX_RAY` and `borrowed <= i128::MAX * RAY / MAX_BORROW_INDEX_RAY` before minting additional shares. [9](#0-8) [19](#0-18)  Alternatively, represent cumulative supplied and borrowed values with a wider fixed-point type throughout accrual and add boundary tests that place scaled totals just below the admissible cap, accrue positive rewards, then execute repay, withdraw, liquidation, and `update_indexes`. [20](#0-19) [2](#0-1) 

### Proof of Concept
Consider a listed asset with `asset_decimals = 3`, a normal positive reserve rate, and `reserve_factor < BPS`. [21](#0-20) [22](#0-21)  At three decimals, an attacker deposits approximately `1.70e14` base units through `Controller::supply(caller, account_id, spoke_id, [(hub_asset, amount)])`; `Ray::from_asset` multiplies by `10^24`, producing `supplied` close to `1.70e38`, near `i128::MAX`. [23](#0-22) [24](#0-23) 

The attacker then creates positive utilization with `Controller::borrow(caller, account_id, [(hub_asset, borrow_amount)], to)`; borrowing mints debt shares and records them in `borrowed` after normal liquidity and utilization checks. [25](#0-24)  After ledger time advances, the attacker calls `Controller::update_indexes(caller, [hub_asset])`. [18](#0-17)  `global_sync` computes positive supplier rewards, while `update_supply_index` evaluates `supplied * supply_index` and adds `rewards_increase`; with `supplied` near the representable ceiling, either that multiplication or the subsequent `checked_add` panics with `MathOverflow`. [1](#0-0) [15](#0-14) 

Because `commit` and `mark_accrued` occur only after all chunks complete, the failed transaction leaves `last_timestamp` unchanged. [3](#0-2) [26](#0-25)  Subsequent `withdraw`, `repay`, `supply`, `borrow`, or `update_indexes` calls load the same stale timestamp and re-run the overflowing accrual before performing their own logic, permanently denying the operation. [2](#0-1) [11](#0-10)

### Citations

**File:** common/src/rates/simulate.rs (L51-72)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
    let supplier_shortfall = supply_index_reward_shortfall(
```

**File:** contracts/pool/src/ops/mod.rs (L29-46)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}

/// Renews instance TTL, then loads and accrues the market.
pub(crate) fn renewed_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    renew_instance(env);
    synced_market(env, hub_asset)
}

/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```

**File:** contracts/pool/src/interest.rs (L20-32)
```rust
pub(crate) fn global_sync(env: &Env, cache: &mut Cache) {
    if !cache.needs_accrual() {
        return;
    }

    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
```

**File:** common/src/math/fp.rs (L49-57)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }

    /// Divides this value by `other`, rounding the result half up.
    pub fn div(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, RAY, other.0))
    }
```

**File:** common/src/math/fp.rs (L139-147)
```rust
    /// Builds a `Ray` from a token amount at `asset_decimals`, rescaling half up to 27 decimals.
    pub fn from_asset(env: &Env, amount: i128, asset_decimals: u32) -> Ray {
        Ray(fp_core::rescale_half_up(
            env,
            amount,
            asset_decimals,
            RAY_DECIMALS,
        ))
    }
```

**File:** common/src/math/fp.rs (L155-158)
```rust
    /// Adds `rhs` to this value. Panics on overflow.
    pub fn checked_add(self, env: &Env, rhs: Ray) -> Ray {
        Ray(checked_add_raw(env, self.0, rhs.0))
    }
```

**File:** common/src/math/fp_core.rs (L5-8)
```rust
//! Every multiply-divide first attempts the whole computation in `i128` and
//! only widens the operands to `I256` when the intermediate product does not
//! fit. The widened path is exact, so both paths return the same value.
//! `I256` operations are host calls, so the `i128` path costs less.
```

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L29-45)
```rust
pub fn update_supply_index(env: &Env, supplied: Ray, old_index: Ray, rewards_increase: Ray) -> Ray {
    if supplied == Ray::ZERO || rewards_increase == Ray::ZERO {
        return old_index;
    }

    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
}
```

**File:** common/src/rates/index.rs (L73-88)
```rust
pub fn calculate_supplier_rewards(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    new_borrow_index: Ray,
    old_borrow_index: Ray,
) -> (Ray, Ray) {
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);

    (supplier_rewards, protocol_fee)
```

**File:** common/src/rates/index.rs (L91-99)
```rust
/// Converts a Ray-denominated `fee` into scaled supply-index shares
/// (`fee / supply_index`), floor-rounded and saturating on overflow. Caps the
/// result so that adding it to `supplied` cannot overflow `i128::MAX`.
pub fn protocol_fee_shares(env: &Env, fee: Ray, supply_index: Ray, supplied: Ray) -> Ray {
    let raw = fp_core::mul_div_floor_saturating(env, fee.raw(), RAY, supply_index.raw());

    let headroom = i128::MAX.saturating_sub(supplied.raw());
    Ray::from(raw.min(headroom))
}
```

**File:** contracts/pool/src/ops/market.rs (L50-57)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
```

**File:** contracts/pool/src/ops/market.rs (L65-72)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-65)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
```

**File:** contracts/pool/src/ops/repay.rs (L40-47)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
```

**File:** docs/reference/formulas.md (L423-437)
```markdown
| Bound | Consequence |
|---|---|
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```

**File:** contracts/controller/src/lib.rs (L90-115)
```rust
    /// Supplies `assets` as collateral and returns the account id; `account_id = 0`
    /// creates an account in `spoke_id`. Third parties may only top up existing
    /// supply positions; owners and delegates may add assets.
    #[when_not_paused]
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
    }

    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
    }
```

**File:** contracts/controller/src/external/pool.rs (L109-116)
```rust
/// Accrues and persists market indexes through the current ledger time.
pub(crate) fn pool_update_indexes_call(
    env: &Env,
    pool_addr: &Address,
    hub_assets: &Vec<HubAssetKey>,
) {
    LiquidityPoolClient::new(env, pool_addr).update_indexes(hub_assets)
}
```

**File:** contracts/pool/src/ops/supply.rs (L23-40)
```rust
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);

    cache.credit_cash(amount);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/borrow.rs (L42-79)
```rust
pub(crate) fn accounting(env: &Env, entry: &PoolBorrowEntry) -> BorrowOutcome {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    mint_debt(env, &mut cache, &mut position, amount);
    cache.debit_cash(amount);

    let snapshot = cache.commit();
    let mutation = cache.position_mutation(position, amount);
    BorrowOutcome {
        cache,
        mutation,
        snapshot,
    }
}

/// Mints scaled debt for `amount` of underlying and enforces max utilization.
///
/// Requires positive amount, sufficient cash reserves, and that the draw
/// leaves the liquidation buffer intact. Panics if the scaled mint rounds to
/// zero shares.
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

**File:** contracts/pool/src/cache/mod.rs (L73-85)
```rust
    /// Persists the full market state and returns a snapshot for events.
    pub(crate) fn commit(&self) -> MarketStateSnapshot {
        let state = PoolStateRaw {
            supplied: self.supplied.raw(),
            borrowed: self.borrowed.raw(),
            revenue: self.revenue.raw(),
            borrow_index: self.borrow_index.raw(),
            supply_index: self.supply_index.raw(),
            last_timestamp: self.last_timestamp,
            cash: self.cash,
        };
        storage::write_state(&self.env, &self.hub_asset, &state);
        self.snapshot()
```
