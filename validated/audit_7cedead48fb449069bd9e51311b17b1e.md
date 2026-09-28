### Title
Permanent market freeze from unscaled RAY value overflow during interest accrual - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
A market can reach a state in which every subsequent interest accrual panics with `MathOverflow` while converting scaled balances to their unscaled RAY values. Because `scaled_to_original` multiplies scaled balances by an index before the borrow index is capped, a sufficiently large market can overflow `i128` even while `borrow_index` remains below `MAX_BORROW_INDEX_RAY`. Once that state exists, permissionless `update_indexes`, as well as repay, withdraw, liquidation, and other controller paths that load the same market, revert before they can mutate state.

### Finding Description
Pool accrual runs through `interest::global_sync`, which calls `accrue_step` for each elapsed interval. [1](#0-0)  `accrue_step` first computes `borrowed_original` and `supplied_original` using `scaled_to_original`. [2](#0-1)  `scaled_to_original` is a non-saturating `Ray::mul`, so an unscaled value exceeding `i128::MAX` panics instead of being capped. [3](#0-2) [4](#0-3) 

The borrow index ceiling only applies after `update_borrow_index` has already multiplied the current index by the interest factor. [5](#0-4)  More importantly, it does not bound the absolute market value. A market storing 1 billion whole 18-decimal tokens has a scaled balance of `1e36`; once either index exceeds roughly 170, the intermediate unscaled value exceeds `i128::MAX` even though the index itself is still far below `MAX_BORROW_INDEX_RAY = 1e36`. [6](#0-5)  The repository's regression test documents exactly this cliff: at 98% utilization on the steep XLM curve, later accrual overflows inside `scaled_to_original` before the index cap engages. [7](#0-6) 

### Impact Explanation
Once the market's scaled balance and index product crosses `i128::MAX`, the next accrual panics permanently. Every ordinary market mutation first calls `global_sync`, so `borrow`, `repay`, `withdraw`, `liquidate`, `recapitalize`, `claim_revenue`, and `update_indexes` all fail before their business logic runs. [8](#0-7)  The pool's direct `update_indexes` path also calls the same `accrue` implementation and therefore cannot recover the market. [9](#0-8) 

The result is permanent freezing of all funds and debt positions in that market: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and bad-debt cleanup cannot execute. The existing harness test confirms that both withdrawal and repayment fail with `MATH_OVERFLOW` after the cliff is reached. [10](#0-9) 

### Likelihood Explanation
This is not a one-call instant freeze. It requires a very large asset balance, a high enough index, and enough elapsed accrual time or a sufficiently steep configured interest-rate curve. An unprivileged user can reach the state through ordinary `supply`, `borrow`, and later `update_indexes`, provided the listed market's configured caps and token supply allow the required position size. [11](#0-10) [12](#0-11)  The regression test demonstrates the condition with 1 billion whole 18-decimal tokens at 98% utilization, so exploitability depends on market scale and configuration rather than privileged access. [13](#0-12) 

### Recommendation
Bound the total unscaled RAY value, not only the indexes. At minimum, add a checked pre-accrual guard that rejects or safely caps state transitions before `scaled_to_original` can overflow. Prefer saturating or widened `I256` arithmetic for utilization, debt growth, and supplied-value calculations, followed by explicit market-level accounting limits. Separately, enforce a maximum accepted market value based on `i128::MAX / maximum_index_growth` during supply and borrow so a valid listed market cannot enter the unrecoverable region.

### Proof of Concept
The repository contains a direct executable proof in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. It creates an 18-decimal market on the steep XLM curve, supplies `1_000_000_000 * 10^18` raw units, borrows 98% of it, advances ledger time one year per iteration, and then calls `update_indexes`. [14](#0-13) 

The first failing `update_indexes` returns contract error `MATH_OVERFLOW`, while the stored borrow index is still below `MAX_BORROW_INDEX_RAY`. [15](#0-14)  A subsequent one-unit withdrawal and a one-token repayment both return the same error, proving that the market is frozen rather than merely rejecting the accrual entrypoint. [16](#0-15)

### Citations

**File:** contracts/pool/src/interest.rs (L20-29)
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
```

**File:** common/src/rates/simulate.rs (L60-64)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-319)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-345)
```rust
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L347-356)
```rust
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

**File:** contracts/pool/src/ops/mod.rs (L29-40)
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

**File:** contracts/controller/src/lib.rs (L94-115)
```rust
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
