### Title

Permanent market freeze from overflowing RAY-valued debt before the index cap - (File: common/src/rates/simulate.rs)

### Summary

**Medium.** Accrual multiplies the market’s scaled debt by the borrow index as an `i128`-represented RAY value before applying the borrow-index ceiling, so a sufficiently large market can reach a state where every subsequent accrual panics with `MathOverflow`. [1](#0-0) [2](#0-1) 

### Finding Description

`accrue_step` computes `borrowed * borrow_index` through `scaled_to_original`, then computes both old and new total debt inside `calculate_supplier_rewards`. [1](#0-0)  Each multiplication is narrowed back to `i128`, so a mathematically valid debt value above `i128::MAX` reverts instead of being represented or bounded. [3](#0-2) [4](#0-3) 

`update_borrow_index` caps only the index at `MAX_BORROW_INDEX_RAY`; it does not bound the separate `borrowed * index` debt-value result. [2](#0-1)  Every pool position leg calls `load_leg`, which synchronizes the market through `global_sync` before executing the requested operation. [5](#0-4) [6](#0-5) 

An unprivileged borrower can create the oversized debt through `borrow` on its own account after supplying sufficient collateral, while any caller can later trigger the overflowing accrual through `update_indexes`. [7](#0-6) [8](#0-7) 

### Impact Explanation

Once `scaled_borrowed * borrow_index / RAY` exceeds `i128::MAX`, `update_indexes` fails and the market becomes permanently unusable because repayment and withdrawal also run the same accrual before their own logic. [9](#0-8) [10](#0-9)  Liquidation is also blocked because its debt-repayment leg reaches the same synchronized pool repay path. [11](#0-10) 

The result is permanent freezing of all supplier claims in that market, absent a contract upgrade, because no user or permissionless cleanup path can skip the failing accrual. [12](#0-11) 

### Likelihood Explanation

The attack requires a high-decimal market with configured caps and liquidity large enough for scaled debt to approach `i128::MAX / borrow_index`, plus sufficient attacker collateral to open the borrow legally. [13](#0-12) [14](#0-13)  For an 18-decimal market, a 980-million-token borrow creates approximately `9.8e35` scaled debt at index `RAY`; the debt valuation overflows once the borrow index exceeds roughly `173.6 * RAY`, well below the `1e9 * RAY` index ceiling. [15](#0-14) [2](#0-1) 

### Recommendation

Do not form absolute `borrowed * index` totals in an `i128` RAY domain during accrual; compute utilization and incremental interest with widened `I256` intermediates or as `borrowed * (new_index - old_index) / RAY`, then bound the incremental result before narrowing. [1](#0-0)  Additionally enforce a debt-share bound derived from the maximum representable RAY-valued debt, or make accrual transition to a bounded terminal state instead of panicking when the debt value becomes unrepresentable. [16](#0-15) 

### Proof of Concept

1. Victim suppliers deposit `1_000_000_000 * 10^18` base units of an 18-decimal asset into a listed market.
2. The attacker supplies enough separate collateral to satisfy LTV and calls `borrow(caller, account_id, [(hub_asset, 980_000_000 * 10^18)], Some(caller))`.
3. The resulting scaled debt is approximately `980_000_000 * 10^18 * 10^9 = 9.8e35`.
4. After accrual raises `borrow_index` above approximately `173.6 * RAY`, any address calls `update_indexes(caller, [hub_asset])`.
5. `accrue_step` panics while computing the debt value, and subsequent `repay`, `withdraw`, `liquidate`, or further `update_indexes` calls hit the same `MathOverflow` before performing their operation. [17](#0-16) [5](#0-4)

### Citations

**File:** common/src/rates/simulate.rs (L51-69)
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

**File:** common/src/math/fp_core.rs (L138-143)
```rust
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
}
```

**File:** common/src/math/fp_core.rs (L298-303)
```rust
/// Converts an `I256` to `i128`, panicking with `GenericError::MathOverflow` if it does not
/// fit.
fn to_i128(env: &Env, val: &I256) -> i128 {
    val.to_i128()
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
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

**File:** contracts/controller/src/positions/debt.rs (L40-59)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);

    let restamped = enforce_post_pool_solvency(env, &mut cache, &mut account);
```

**File:** contracts/controller/src/markets.rs (L119-124)
```rust
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
```

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-64)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L75-85)
```rust
        let position: DebtPosition =
            (&expect_invariant(env, account.borrow_positions.get(entry.hub_asset.clone()))).into();
        actions.push_back(make_pool_action(&position, received, entry.hub_asset));
    }
    apply_repay_batch(
        env,
        account,
        liquidator,
        events::PositionAction::LiqRepay,
        &actions,
        cache,
```

**File:** contracts/controller/src/spoke_usage.rs (L142-156)
```rust
/// Adds scaled usage and enforces the asset-unit cap converted to RAY
/// with `index` and `decimals`.
fn enforce_spoke_cap(
    env: &Env,
    side: UsageSide,
    usage: &SpokeUsageRaw,
    delta_scaled: Ray,
    cap: i128,
    index: Ray,
    decimals: u32,
) -> Ray {
    let cap_scaled = calculate_scaled_cap(env, cap, decimals, index);
    let next_scaled = Ray::from(side.scaled(usage)).checked_add(env, delta_scaled);
    assert_with_error!(env, next_scaled <= cap_scaled, side.cap_error());
    next_scaled
```

**File:** common/src/rates/scaling.rs (L52-56)
```rust
/// Converts an asset-unit `amount` to a scaled borrow `Ray` using ceiling
/// rounding relative to `borrow_index`.
pub fn calculate_scaled_borrow(env: &Env, amount: i128, decimals: u32, borrow_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, borrow_index)
}
```
