### Title
RAY debt valuation overflows `i128` and permanently freezes a market - (File: common/src/rates/simulate.rs)

### Summary
An unprivileged borrower can grow a market’s scaled debt until `borrowed * borrow_index / RAY` no longer fits in `i128`. The next accrual panics in `calculate_supplier_rewards`; because every market mutation accrues before applying its operation, the panic repeatedly blocks withdrawals, repayments, liquidation and cleanup. [1](#0-0) [2](#0-1) 

### Finding Description
Pool positions and market totals are stored as scaled RAY shares, while `scaled_to_original` converts them to asset values by multiplying by the relevant index. [3](#0-2) 

Each mutation loads the market through `synced_market`, which invokes `interest::global_sync` before the operation-specific logic runs. [2](#0-1) 

`global_sync` divides elapsed time into bounded chunks and calls `accrue_step` for every chunk. [4](#0-3) 

Inside `accrue_step`, the current debt and supply values are calculated first, after which `calculate_supplier_rewards` computes both the old and new total debt. [1](#0-0) 

`calculate_supplier_rewards` multiplies the scaled debt by `new_borrow_index` and subtracts the old value. [5](#0-4) 

The fixed-point multiplication widens intermediate arithmetic to `I256`, but still requires the final quotient to fit `i128`; an unrepresentable quotient raises `MathOverflow`. [6](#0-5) 

`update_borrow_index` only caps the index itself at `MAX_BORROW_INDEX_RAY`; it does not bound the resulting debt value to the `i128` domain. [7](#0-6) 

Consequently, once scaled debt is sufficiently large, ordinary interest growth can make `new_total_debt` unrepresentable even though both the scaled debt and capped index are individually valid `i128` values. [8](#0-7) 

### Impact Explanation
The transaction reverts during accrual, so neither index nor market state is committed; every subsequent accrual attempts the same overflowing calculation with an equal-or-larger elapsed interval. [9](#0-8) 

Because `supply`, `borrow`, `withdraw`, `repay`, seizure and strategy legs all load an interest-synced market, the overflow freezes the entire market rather than only the oversized position. [10](#0-9) [11](#0-10) 

Suppliers cannot withdraw their cash, borrowers cannot repay or be liquidated, bad-debt seizure cannot socialize the position, and revenue cannot be safely claimed from that market. [12](#0-11) 

Parameter replacement also accrues under the old model before writing the replacement, so changing the rate curve does not provide an in-contract recovery path once the arithmetic boundary has been crossed. [13](#0-12) 

Absent a contract upgrade or another privileged code-level intervention, user funds in the affected market are permanently frozen.

### Likelihood Explanation
The attacker does not need privileged access after a market has been listed: they can use the normal `supply`, `borrow` and `update_indexes` paths to create the scaled-debt boundary and trigger accrual. [12](#0-11) 

For an 18-decimal asset, a deposit near `i128::MAX / 10^9` native units produces scaled supply near `i128::MAX`; borrowing 98% of it produces scaled debt where the first borrow-index multiplier above approximately `1.0204 * RAY` overflows the debt valuation. [1](#0-0) [14](#0-13) 

Lower initial utilization only raises the index threshold required for the same failure: at utilization fraction `u`, the market freezes once `borrow_index > RAY / u`. [15](#0-14) 

The attack therefore requires a listing whose caps, available token supply and collateral markets admit a sufficiently large borrow; smaller configured caps can delay or prevent the condition in a particular deployment, but caps do not remove the vulnerable arithmetic.

### Recommendation
Bound the product domain, not just the index domain. Before committing a new index, calculate the maximum index for which both `borrowed * borrow_index / RAY` and `supplied * supply_index / RAY` remain representable, using `I256` for the bound calculation, and clamp or otherwise safely terminate accrual at that boundary. [16](#0-15) 

Alternatively, keep market valuation in `I256` through accrual and explicitly handle values that cannot be represented as transferable `i128` amounts; returning to `i128` must occur only at a boundary with a defined settlement policy. [17](#0-16) 

Add boundary tests proving that a market at the largest admitted scaled debt can still execute `update_indexes`, `repay`, `withdraw`, `seize_positions` and `recapitalize` instead of trapping during accrual. [10](#0-9) 

### Proof of Concept
1. Select an existing 18-decimal market `T` under hub `H` whose supply and borrow caps admit the domain maximum.

2. Let `U = 10^9` be the 18-decimal token-to-RAY upscale factor and choose:

   ```text
   S = floor(i128::MAX / U)
   B = floor(98 * S / 100)
   ```

   `S * U` fits `i128`, while `B * U` is approximately `0.98 * i128::MAX`. [3](#0-2) 

3. Through the normal controller paths, submit `supply` for `T` with amount `S`, supply sufficient collateral in another listed market, and submit `borrow` for `T` with amount `B`. The pool entrypoints accept the corresponding `PoolSupplyEntry` and `PoolBorrowEntry` batches. [18](#0-17) [19](#0-18) 

4. At the initial index, the scaled debt is approximately `D = 0.98 * i128::MAX`. Any new borrow index satisfying

   ```text
   new_borrow_index > (i128::MAX * RAY) / D
                    ≈ 1.0204 * RAY
   ```

   makes `D * new_borrow_index / RAY` exceed `i128::MAX`. [5](#0-4) 

5. Invoke `update_indexes` for `hub_assets = [HubAssetKey { hub_id: H, asset: T }]` after a positive interest interval. [20](#0-19) 

6. `global_sync` reaches `accrue_step`, and `calculate_supplier_rewards` panics while computing `new_total_debt`; the transaction rolls back before `mark_accrued` can commit progress. [9](#0-8) [21](#0-20) 

7. Repeat `update_indexes`, `withdraw`, `repay` or liquidation. Each path first calls `synced_market`, reaches the same overflowing accrual and reverts again, leaving the market’s funds inaccessible. [10](#0-9)

### Citations

**File:** common/src/rates/simulate.rs (L60-80)
```rust
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
        env,
        supplied,
        supply_index,
        new_supply_index,
        supplier_rewards,
    );

    let protocol_reward = protocol_fee.checked_add(env, supplier_shortfall);
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

**File:** common/src/rates/scaling.rs (L12-15)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L73-86)
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
```

**File:** common/src/math/fp_core.rs (L14-20)
```rust
/// Widens `x`, `y`, and `d` to `I256` for overflow-safe intermediate arithmetic.
fn to_i256_operands(env: &Env, x: i128, y: i128, d: i128) -> (I256, I256, I256) {
    (
        I256::from_i128(env, x),
        I256::from_i128(env, y),
        I256::from_i128(env, d),
    )
```

**File:** common/src/math/fp_core.rs (L104-118)
```rust
/// Computes `x * y / d` rounded half up. Requires `x >= 0`, `y >= 0`, and `d > 0`; a
/// `debug_assert` checks this in debug builds. Panics with `GenericError::DivisionByZero` if
/// `d == 0`, and with `GenericError::MathOverflow` if any other precondition is violated or if
/// the result does not fit in `i128`.
pub fn mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    // The zero check runs first so debug and release builds agree on a zero
    // divisor: both surface `DivisionByZero` rather than tripping the assert.
    require_nonzero_divisor(env, d);
    debug_assert!(
        x >= 0 && y >= 0 && d > 0,
        "mul_div_half_up: non-negative x, y and positive d"
    );
    try_mul_div_half_up(env, x, y, d)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** contracts/pool/src/ops/seize.rs (L18-27)
```rust
pub(crate) fn apply(env: &Env, entry: &PoolSeizeEntry) -> MarketStateSnapshot {
    require_nonneg_amount(env, entry.position.scaled_amount);
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);

    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
```

**File:** contracts/pool/src/lib.rs (L110-117)
```rust
    /// Replaces the interest-rate model (curve, utilization cap, reserve
    /// factor) and flash-loan settings for a market. Accrues interest first so
    /// the old model applies through the current ledger, then writes the new
    /// model into market params. Restricted to the owner.
    #[only_owner]
    fn update_params(env: Env, hub_asset: HubAssetKey, model: InterestRateModel) {
        ops::market::replace_rate_model(&env, hub_asset, model);
    }
```

**File:** contracts/pool/src/lib.rs (L128-179)
```rust
    /// Accrues, mints scaled supply shares and credits cash per entry. The
    /// controller transfers the tokens in before this call. Owner-only.
    #[only_owner]
    fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, ops::supply::apply)
    }

    /// Batch-borrows assets and transfers them to `receiver`: accrues
    /// interest, mints scaled debt, debits cash, and enforces max
    /// utilization after each mint. Restricted to the owner; returns one
    /// [`PoolPositionMutation`] per entry.
    #[only_owner]
    fn borrow(
        env: Env,
        receiver: Address,
        entries: Vec<PoolBorrowEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::borrow::apply(env, &receiver, entry)
        })
    }

    /// Burns supply shares and transfers the underlying to `receiver`.
    /// `is_liquidation` skips the max-utilization check and may withhold a
    /// protocol fee. Owner-only; `actual_amount` is gross of that fee.
    #[only_owner]
    fn withdraw(
        env: Env,
        receiver: Address,
        is_liquidation: bool,
        entries: Vec<PoolWithdrawEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::withdraw::apply(env, &receiver, is_liquidation, entry)
        })
    }

    /// Burns scaled debt up to the repay amount, credits cash with the net
    /// repay and refunds overpayment to `payer`. Owner-only.
    #[only_owner]
    fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, actions, |env, action| {
            ops::repay::apply(env, &payer, action)
        })
    }

    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
```

**File:** contracts/pool/src/ops/borrow.rs (L63-78)
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
```
