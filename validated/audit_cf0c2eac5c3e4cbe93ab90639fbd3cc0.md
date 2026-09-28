### Title
Interest accrual overflows before index caps and permanently freezes a large utilized market - (File: common/src/rates/simulate.rs)

### Summary
A sufficiently large supplied or borrowed RAY-scaled balance can make `accrue_step` panic while converting shares back to value, before the borrow-index ceiling can engage. Once the market reaches that state, the permissionless `update_indexes` call and every controller operation touching the market accrue first and therefore revert indefinitely, freezing supplier funds, blocking repayment, and preventing liquidation. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`Controller::update_indexes(caller, assets)` is callable by any authorized caller and forwards `assets` to the pool's `update_indexes`. [4](#0-3) [5](#0-4) 

The pool loads each market and calls `interest::global_sync`, which invokes `accrue_step` for every elapsed chunk before committing state. [6](#0-5) [7](#0-6) 

`accrue_step` first calls `scaled_to_original` for both `borrowed * borrow_index` and `supplied * supply_index`; `scaled_to_original` uses `Ray::mul`, which panics on `i128` overflow. [1](#0-0) [8](#0-7) 

The configured cap domain permits approximately 170.14 billion whole-token equivalents, while index growth can push an already admitted book past the separate `i128` value ceiling before the `MAX_BORROW_INDEX_RAY` clamp is reached. [9](#0-8) [10](#0-9) 

The existing harness reproduces the condition with a one-billion-token, 18-decimal market at 98% utilization on a steep rate curve: a later `update_indexes` fails with `MATH_OVERFLOW`, after which both withdrawal and repayment also fail because they accrue first. [11](#0-10) 

### Impact Explanation
This is permanent freezing of market funds rather than a single failed transaction. Once `supplied * supply_index` or `borrowed * borrow_index` exceeds `i128::MAX`, `last_timestamp` remains stale and every subsequent accrual retries the same overflowing multiplication. [1](#0-0) [2](#0-1) 

Consequently, suppliers cannot withdraw pool cash, borrowers cannot repay, liquidators cannot rescue underwater accounts, and bad-debt cleanup cannot progress for that market. The regression test explicitly demonstrates failed `update_indexes`, `withdraw`, and `repay` calls after the overflow boundary is reached. [12](#0-11) 

### Likelihood Explanation
The trigger requires a very large market and enough elapsed high-utilization accrual for a stored scaled balance times its index to exceed the `i128` value domain. Those prerequisites are economically significant, but they can arise from ordinary permissionless `supply`, `borrow`, and time passage; once the state exists, any unprivileged caller can trigger the panic through `update_indexes(caller, [hub_asset])`. [4](#0-3) [13](#0-12) 

The issue is also not safely bounded by the configured index ceiling: `update_borrow_index` clamps only after computing the product, while debt and supply value calculations independently multiply balances by indexes. [14](#0-13) [15](#0-14) 

### Recommendation
Replace the vulnerable `i128` intermediate products with wider arithmetic or decomposition-based `mul_div` calculations throughout accrual and unscaling. At minimum, utilization and accrued-interest calculations should saturate or use a wider intermediate instead of allowing `scaled * index` to panic, and index/value-cap checks must run before the overflowing product is formed. [16](#0-15) [14](#0-13) 

Additionally, enforce market-level scaled-supply and scaled-debt limits that guarantee `scaled * max_index <= i128::MAX` for every admitted cap and position. Without such an invariant, caps on token input amounts alone do not bound later accrued values. [13](#0-12) 

### Proof of Concept
The repository already contains a deterministic reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

1. Create an 18-decimal market using the steep `xlm_curve`.
2. Raise its caps to the permitted domain ceiling.
3. Supply `1_000_000_000 * 10^18` base units.
4. Borrow 98% of that supply against separate collateral.
5. Advance ledger time by one-year intervals and call `update_indexes` after each interval.
6. Observe `MATH_OVERFLOW`; subsequent `withdraw` and `repay` calls also return `MATH_OVERFLOW`. [11](#0-10)

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

**File:** contracts/pool/src/interest.rs (L25-29)
```rust
    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
```

**File:** contracts/pool/src/interest.rs (L39-48)
```rust
fn accrue_chunk(env: &Env, cache: &mut Cache, delta_ms: u64) {
    let step = accrue_step(
        env,
        cache.params(),
        cache.borrowed(),
        cache.supplied(),
        cache.borrow_index(),
        cache.supply_index(),
        delta_ms,
    );
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

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/controller/src/markets.rs (L118-124)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
```

**File:** contracts/pool/src/ops/market.rs (L65-71)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/validation.rs (L48-55)
```rust
pub fn max_cap_for_decimals(asset_decimals: u32) -> i128 {
    let Some(exp) = RAY_DECIMALS.checked_sub(asset_decimals) else {
        return 0;
    };
    let upscale = 10i128
        .checked_pow(exp)
        .expect("10^(RAY_DECIMALS - asset_decimals) fits i128 for asset_decimals <= RAY_DECIMALS");
    i128::MAX / upscale
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
```
