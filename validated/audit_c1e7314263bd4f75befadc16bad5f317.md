### Title
Unbounded RAY value multiplication can permanently freeze a market - ([File: common/src/rates/scaling.rs])

### Summary
A sufficiently large market can grow its scaled borrow value past the `i128` domain before `MAX_BORROW_INDEX_RAY` is reached. Once that happens, `accrue_step` panics with `MathOverflow`, and every subsequent pool mutation that synchronizes the market fails permanently. An unprivileged caller can trigger the condition through `controller.update_indexes`; afterwards repayments, withdrawals, and liquidations touching the same market cannot complete. [1](#0-0) [2](#0-1) 

### Finding Description
`global_sync` runs `accrue_step` for each elapsed interval before a market mutation proceeds. [2](#0-1) 

`accrue_step` first converts both scaled totals into unscaled RAY values:

```rust
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
let supplied_original = scaled_to_original(env, supplied, supply_index);
```

`scaled_to_original` performs `scaled.mul(env, index)`, which panics when the result does not fit `i128`. [3](#0-2) [1](#0-0) 

The only index ceiling is the fixed `MAX_BORROW_INDEX_RAY`; it does not account for the size of `borrowed`. Therefore a book whose scaled debt is large enough can cross `i128::MAX / borrowed` while still below the nominal index cap. [4](#0-3) 

The failing state cannot be repaired through ordinary pool operations because `synced_market` loads the cache and calls `interest::global_sync` before the requested operation. [5](#0-4)  `repay`, `withdraw`, and `update_indexes` all route into that synchronized batch path. [6](#0-5)  A controller liquidation also reaches the same owner-only pool repayment and withdrawal/seizure operations. [6](#0-5) [7](#0-6) 

The repository's stress test reproduces the issue with a supported 18-decimal market, a one-billion-token supply, 98% utilization, and a steep permitted rate curve: `update_indexes`, withdrawal, and repayment all fail with `MathOverflow` before `MAX_BORROW_INDEX_RAY` is reached. [8](#0-7) 

### Impact Explanation
This is a permanent freezing-of-funds condition for the affected market. Suppliers cannot withdraw, borrowers cannot reduce their debt, liquidators cannot unwind an unhealthy account through the pool, and the permissionless index-maintenance path cannot advance the market because each of those paths performs accrual first. [5](#0-4) [6](#0-5)  The failure is not confined to the triggering transaction: once the stored book and elapsed-time requirement produce the overflowing multiplication, every later mutation hits the same panic. [2](#0-1) [9](#0-8) 

### Likelihood Explanation
Likelihood is economically constrained but technically reachable without privileged access. An attacker needs an admitted high-decimal market whose supply cap permits roughly `1e36` RAY-scaled exposure, enough collateral to hold approximately 98% utilization, and a steep configured rate profile or equivalent long-running high utilization. [10](#0-9) [11](#0-10)  After establishing that state, any later `update_indexes` call—including one submitted by the attacker—can push the market over the representable boundary and leave it permanently stuck. [12](#0-11) [13](#0-12) 

### Recommendation
Do not let index growth depend only on `MAX_BORROW_INDEX_RAY`. Before applying an accrual step, derive a per-market maximum index that also satisfies `scaled_amount * index <= i128::MAX`, and clamp the new borrow and supply indexes to that representable bound. At minimum, `update_borrow_index` should cap `new_index` at `min(MAX_BORROW_INDEX_RAY, i128::MAX / borrowed.raw())` when `borrowed` is nonzero, with equivalent protection for the supply index and the later `new_total_debt` calculation. This preserves a terminal accrued state instead of poisoning every future synchronized operation. [4](#0-3) [14](#0-13) 

### Proof of Concept
1. Configure an 18-decimal market with a cap at the supported domain maximum and a steep permitted interest-rate curve.
2. Supply approximately `1_000_000_000` whole tokens, so its scaled supply is approximately `1e36` RAY.
3. Using other collateral, borrow approximately 98% of that market.
4. Allow interest to compound until the borrow index approaches a growth factor greater than `i128::MAX / 1e36`—approximately 170x, still below `MAX_BORROW_INDEX_RAY`.
5. Call `controller.update_indexes` for that market.
6. The call enters pool `update_indexes`, runs `interest::global_sync`, and panics inside `scaled_to_original` with `MathOverflow`. Subsequent `repay` and `withdraw` calls hit `synced_market` first and fail identically. [13](#0-12) [2](#0-1) [9](#0-8) [5](#0-4)

### Citations

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** contracts/pool/src/interest.rs (L20-33)
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
}
```

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

**File:** contracts/pool/src/ops/mod.rs (L29-34)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}
```

**File:** contracts/pool/src/lib.rs (L153-180)
```rust
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
    }
```

**File:** contracts/pool/src/lib.rs (L224-231)
```rust
    /// Seizes positions during liquidation or bad-debt cleanup. Borrow-side
    /// entries socialize bad debt onto the supply index and burn the debt;
    /// deposit-side entries reclassify supply shares as protocol revenue.
    /// Restricted to the owner.
    #[only_owner]
    fn seize_positions(env: Env, entries: Vec<PoolSeizeEntry>) {
        ops::run_batch(&env, entries, |e, entry| ((), ops::seize::apply(e, entry)));
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L26-39)
```rust
/// Steep XLM stress curve: 175 percent max borrow rate, optimal at 75 percent.
fn xlm_curve() -> MarketParamsPreset {
    MarketParamsPreset {
        max_borrow_rate: RAY * 175 / 100,
        base_borrow_rate: RAY / 100,
        slope1: RAY * 4 / 100,
        slope2: RAY * 10 / 100,
        slope3: RAY * 150 / 100,
        mid_utilization: RAY * 50 / 100,
        optimal_utilization: RAY * 75 / 100,
        max_utilization: RAY,
        reserve_factor: 2000,
    }
}
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-356)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
fn a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap() {
    let mut t = LendingTest::new()
        .with_market(big("BIG18", 18, xlm_curve()))
        .with_market(col())
        .with_max_utilization_disabled_all_markets()
        .build();
    lift_caps(&t, "BIG18", 18);
    lift_caps(&t, "COL", 7);
    let principal = BILLION * 10i128.pow(18);
    t.supply_raw(BOB, "BIG18", principal);
    let debt = principal / 100 * 98;
    t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
    t.borrow_raw(ALICE, "BIG18", debt);

    let mut years = 0u32;
    let failure = loop {
        years += 1;
        assert!(
            years <= 40,
            "no cliff within 40 years; the bound in docs/reference/formulas.md is wrong"
        );
        t.advance_time(YEAR_SECS);
        if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
            break e;
        }
    };
    let failed: Result<(), soroban_sdk::Error> = Err(failure);
    assert_contract_error(failed, errors::MATH_OVERFLOW);
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
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
