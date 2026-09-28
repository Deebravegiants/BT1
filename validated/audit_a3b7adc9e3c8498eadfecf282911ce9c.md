### Title
Unbounded accrued-debt valuation overflows `i128` and permanently freezes a market - (File: `common/src/rates/simulate.rs`)

### Summary
`accrue_step` converts total scaled debt back into its RAY-denominated principal before checking or applying the borrow-index ceiling. Once `borrowed * borrow_index / RAY` exceeds `i128::MAX`, the conversion panics with `MathOverflow`; because every pool mutation synchronizes the market first, repayment, withdrawal, liquidation, bad-debt cleanup, recapitalization, and further `update_indexes` calls all become unavailable for that market. [1](#0-0) [2](#0-1) 

### Finding Description
The permissionless controller entrypoint `update_indexes(caller, assets)` delegates each supplied `HubAssetKey` to the pool’s index-accrual path. [3](#0-2) [4](#0-3)  The pool implementation loads each market and runs `interest::global_sync` before committing it. [5](#0-4) 

Inside `accrue_step`, the market’s aggregate `borrowed` shares are unscaled by `scaled_to_original(env, borrowed, borrow_index)` before the new borrow index is computed. [6](#0-5)  `scaled_to_original` returns `scaled.mul(env, index)`, which computes `scaled * index / RAY`. [7](#0-6)  Although the multiplication widens to `I256`, converting a result larger than `i128::MAX` back to `i128` returns `None`; `mul_div_half_up` then raises `GenericError::MathOverflow`. [8](#0-7) 

The same synchronization is performed by `synced_market`, the common loader used by pool mutations. [9](#0-8)  Consequently, once the threshold is crossed, the transaction reverts before it can reduce debt, burn supply shares, seize collateral, or write down bad debt.

### Impact Explanation
This is permanent freezing of funds and a market that cannot operate: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, `clean_bad_debt` cannot socialize the position, and `recapitalize` cannot reach its cash-accounting logic. [2](#0-1)  Since the panic occurs during pre-operation accrual, the stored `last_timestamp` is not advanced and every subsequent call encounters the same overflowing valuation. [10](#0-9) 

The failure can happen while the borrow index remains below its protocol ceiling because the checked output is the aggregate debt value, not merely the index itself. [1](#0-0)  Therefore, the index bound does not protect a sufficiently large market.

### Likelihood Explanation
An unprivileged user can reach the state through ordinary `supply`, `borrow`, and `update_indexes` calls; no administrative role, leaked key, upgrade, oracle manipulation, or third-party behavior is required. [11](#0-10) [3](#0-2)  The attacker needs enough collateral to borrow a very large position, or an existing market can grow into the condition through sustained utilization; the economic prerequisite limits practical exploitability, so this is best rated Medium despite the permanent impact.

### Recommendation
Make aggregate valuation overflow impossible or non-fatal during accrual.

- Before calling `scaled_to_original`, derive a market-specific borrow-index ceiling such as `floor(i128::MAX * RAY / borrowed)` and clamp `borrow_index` before valuation.
- Alternatively use the non-panicking `try_mul_div_half_up` result to detect the representability limit and clamp accrual for that market instead of reverting.
- Apply the equivalent bound to supplied valuation and revenue-share accounting.
- Enforce tighter supply/borrow caps from the maximum admitted index, or document and enforce a lower effective index ceiling that preserves representable market totals.
- Add an invariant covering every mutation path: if a market has positive `borrowed` or `supplied`, accrual must not make its own synchronization unusable.

The preferred mitigation is to clamp index growth at the largest value that keeps the corresponding market value representable, rather than allowing accrual to enter a state where no operation can reduce the position.

### Proof of Concept
For an 18-decimal asset, create a large pool position and borrow near the maximum admitted utilization:

```text
market        = HubAssetKey { hub_id: H, asset: BIG18 }
principal     = 1_000_000_000 * 10^18        // base units
scaled_debt   ≈ principal * 10^9
             = 10^36                        // RAY-scaled debt shares

borrow_index  > i128::MAX * RAY / scaled_debt
             ≈ 1.7014118e29                 // about 170.14 * RAY
```

At that point:

```text
scaled_to_original(scaled_debt, borrow_index)
= scaled_debt * borrow_index / RAY
> i128::MAX
```

The smallest representative trigger is:

```text
controller.update_indexes(attacker, vec![market])
```

Execution reaches `pool_update_indexes_call`, then `market::accrue`, then `global_sync`, then `accrue_step`; `scaled_to_original` raises `MathOverflow` before the index update can commit. [5](#0-4) [1](#0-0) 

Afterward, the following calls revert for that market because each loads `synced_market` before changing positions:

```text
controller.repay(caller, victim_account, vec![(market, 1)])
controller.withdraw(caller, supplier_account, vec![(market, 1)], None)
controller.liquidate(liquidator, victim_account, vec![(market, 1)], SeizeMode::Transfer)
controller.clean_bad_debt(caller, victim_account)
controller.recapitalize(payer, market, amount)
controller.update_indexes(caller, vec![market])
```

Each call reaches the same pre-operation accrual, so none can reduce `borrowed` or otherwise remove the overflowing state. [9](#0-8)

### Citations

**File:** common/src/rates/simulate.rs (L60-69)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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
