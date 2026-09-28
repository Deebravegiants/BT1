### Title
RAY-valued accrual overflows before the borrow-index cap, permanently freezing a market - (`common/src/rates/simulate.rs`)

### Summary
Interest accrual can reach an `i128` valuation ceiling before the configured index ceiling, causing every subsequent market operation to revert. Any authenticated user can trigger the failure through `Controller::update_indexes`, after which suppliers cannot withdraw and borrowers cannot repay without a privileged contract upgrade.

### Finding Description
Each accrual step converts scaled debt and supply into RAY-denominated values before calculating utilization and rates. [1](#0-0)  The conversion is `scaled * index / RAY` and panics when the result does not fit in `i128`. [2](#0-1) [3](#0-2) [4](#0-3) 

The borrow index is nominally capped at `MAX_BORROW_INDEX_RAY`, but that cap is approximately `1e9x`. [5](#0-4) [6](#0-5)  A much lower index can already make `borrowed * new_index / RAY` unrepresentable, and `calculate_supplier_rewards` evaluates both the old and new debt values before the step can complete. [7](#0-6) 

Every pool leg loads the market through `synced_market`, which unconditionally calls `global_sync` before withdrawal, repayment, or borrowing logic runs. [8](#0-7) [9](#0-8)  `repay` calls this loader before resolving debt, and `withdraw` calls it before resolving supply. [10](#0-9) [11](#0-10) 

The public controller exposes `update_indexes` to any authenticated caller and forwards the chosen assets to the pool. [12](#0-11) [13](#0-12)  The pool then runs the same accrual path for each requested market. [14](#0-13) 

### Impact Explanation
Once the next accrual step would produce an unrepresentable RAY value, the transaction reverts and the failed step is never committed. Because the stored state remains at the boundary, every later operation retries the same overflowing calculation.

This permanently freezes supplier principal and yield in the affected market and prevents borrowers or liquidators from reducing its debt. It also blocks normal repayment, withdrawal, borrowing, forced index updates, and recapitalization paths that sync the market first. [8](#0-7) [15](#0-14) 

### Likelihood Explanation
The trigger requires an extremely large market and enough high-utilization accrual for the index to approach the representable-value boundary. For example, scaled debt near `9.8e35` becomes unsafe when the evaluated borrow index exceeds roughly `173x`, far below the configured `1e9x` cap.

That is an extreme market condition rather than an arbitrary low-cost attack, so Medium severity is appropriate. It is nevertheless reachable by an unprivileged participant supplying the debt asset, borrowing a large share against adequate collateral, and later calling the permissionless `update_indexes` path.

### Recommendation
Bound each index by both its configured ceiling and the largest index that keeps the market's scaled obligations representable:

```rust
let safe_borrow_index = i128::MAX * RAY / borrowed.raw();
let capped_index = min(MAX_BORROW_INDEX_RAY, safe_borrow_index);
```

Apply the same dynamic bound to `supply_index`, including revenue shares added to `supplied`. Alternatively, perform utilization and interest valuation in `I256`, explicitly saturate utilization at `RAY`, and cap stored indexes before converting values back to `i128`.

The boundary should be enforced before `calculate_supplier_rewards`, `update_supply_index`, and `supply_index_reward_shortfall`, not only inside `update_borrow_index`, because those later calculations also multiply scaled balances by the new indexes. [16](#0-15) 

### Proof of Concept
1. An attacker opens a normal account and supplies a large listed collateral plus one billion whole units of an 18-decimal debt asset:
   ```rust
   controller.supply(
       attacker,
       0,
       spoke_id,
       vec![
           (collateral_hub_asset, sufficient_collateral),
           (debt_hub_asset, 1_000_000_000_000_000_000_000_000_000),
       ],
   );
   ```

2. The attacker borrows 98% of that market:
   ```rust
   controller.borrow(
       attacker,
       account_id,
       vec![(debt_hub_asset, 980_000_000_000_000_000_000_000_000)],
       Some(attacker),
   );
   ```

3. After sustained high-utilization accrual, any authenticated caller invokes:
   ```rust
   controller.update_indexes(attacker, vec![debt_hub_asset]);
   ```

4. The next `accrue_step` evaluates an old or new debt value above `i128::MAX`, causing `Ray::mul` to raise `MathOverflow` before a bounded index can be committed.

5. Subsequent calls revert through the same first-stage accrual:
   ```rust
   controller.withdraw(supplier, supplier_account, vec![(debt_hub_asset, 0)], None);
   controller.repay(payer, borrower_account, vec![(debt_hub_asset, amount)]);
   ```

Both calls reach `ops::load_leg`, `synced_market`, and `global_sync` before any withdrawal or repayment accounting can execute. [8](#0-7)

### Citations

**File:** common/src/rates/simulate.rs (L51-64)
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
```

**File:** common/src/rates/simulate.rs (L66-87)
```rust
    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
    let supplier_shortfall = supply_index_reward_shortfall(
        env,
        supplied,
        supply_index,
        new_supply_index,
        supplier_rewards,
    );

    let protocol_reward = protocol_fee.checked_add(env, supplier_shortfall);
    // Shares are valued at the new supply index, which the caller stores for
    // this step.
    let revenue_shares = if protocol_reward == Ray::ZERO {
        Ray::ZERO
    } else {
        protocol_fee_shares(env, protocol_reward, new_supply_index, supplied)
    };
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/math/fp_core.rs (L120-143)
```rust
/// Computes `x * y / d` rounded half up. Returns `None` if `x < 0`, `y < 0`, `d <= 0`, or the
/// result does not fit in `i128`.
pub fn try_mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> Option<i128> {
    if x < 0 || y < 0 || d <= 0 {
        return None;
    }
    let half = d / 2;

    // Fast path: the biased product fits `i128`, so the whole computation is
    // native. `x * y + half` is non-negative here, so `/` is the floor the
    // widened path would produce.
    if let Some(biased) = x
        .checked_mul(y)
        .and_then(|product| product.checked_add(half))
    {
        return Some(biased / d);
    }

    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
}
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** common/src/rates/index.rs (L11-19)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
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

**File:** contracts/pool/src/ops/mod.rs (L29-47)
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
}
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

**File:** contracts/pool/src/ops/repay.rs (L36-57)
```rust
/// Accrues interest, resolves the repay amount into burned debt shares and
/// overpayment, burns the shares, and credits the net repay to cash without
/// transferring the overpayment refund. Panics if a positive net repay would
/// burn zero scaled shares.
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);

    cache.credit_cash(net_repay);
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-80)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

```

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```

**File:** contracts/controller/src/markets.rs (L118-125)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
}
```

**File:** contracts/pool/src/ops/market.rs (L60-72)
```rust
/// Accrues interest for each market in `hub_assets` and emits one state event
/// per market.
///
/// Always commits state so same-ledger simulation records the write footprint
/// needed if time advances before transaction inclusion.
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
```

**File:** contracts/pool/src/ops/recapitalize.rs (L44-58)
```rust
pub(crate) fn accounting(
    env: &Env,
    hub_asset: HubAssetKey,
    amount: i128,
) -> RecapitalizationOutcome {
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```
