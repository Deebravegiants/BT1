### Title
Accrual `i128` overflow before index cap permanently freezes a market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
The accrual step unscales `borrowed` and `supplied` through `scaled_to_original` before the index caps can stop growth, so an oversized book can make `borrowed * borrow_index` or `supplied * supply_index` exceed `i128` while both indexes remain below `MAX_*_INDEX_RAY`. Because every market mutation first loads a synced cache and runs `global_sync`, the same overflow is hit by `supply`, `borrow`, `withdraw`, `repay`, `update_indexes`, liquidation pool legs, bad-debt cleanup pool legs, flash paths, and revenue claims for that market. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`accrue_step` computes utilization from `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)`, then only caps the newly computed index afterward through `update_borrow_index`/`update_supply_index`. `scaled_to_original` is a plain `Ray::mul` with no saturation or pre-division fallback. The harness test demonstrates the reachable end state: a large `BIG18` book at sustained high utilization eventually makes permissionless/controller `update_indexes` fail with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent `withdraw` and `repay` fail for the same reason before they can reduce the position. [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

### Impact Explanation
The affected `(hub, token)` book becomes unusable: suppliers cannot withdraw, borrowers cannot repay or borrow, liquidators cannot run the pool legs needed for seizure, and `update_indexes` cannot advance the market. That is a permanent freezing of funds for that market unless an upgrade changes the accrual math, matching the availability impact of the external report while remaining inside the accepted unprivileged surface. Other markets remain isolated because the overflow is computed from that market’s stored scaled totals and indexes. [8](#0-7) [9](#0-8) 

### Likelihood Explanation
Medium. It needs an unusually large admitted book and enough elapsed high-rate accrual for scaled value, not merely index, to cross the `i128` boundary; the reproduced case uses roughly a billion whole 18-decimal tokens supplied and 98% borrowed under steep-rate conditions, then advances years until accrual fails. The barrier is economic rather than privileged: once caps and utilization admit the position, any later caller can trigger the freeze through permissionless/controller paths such as `update_indexes`, and no governance call is needed at the moment of failure. [10](#0-9) 

### Recommendation
Make accrual value computations saturation-safe or boundary-aware: cap or early-return index growth before unscaled value can overflow, compare `scaled` against `i128::MAX / index` before multiplying, and/or use checked multiplication that clamps utilization inputs instead of panicking. Enforce caps using post-accrual worst-case scaled value, not only current token amount, and add a regression that repayment/withdrawal still succeeds after the index cap is reached. [11](#0-10) [12](#0-11) 

### Proof of Concept
The existing regression encodes the sequence: create an 18-decimal `BIG18` market plus collateral market, lift caps, supply `principal = BILLION * 10^18` of `BIG18`, collateralize Alice and borrow `principal * 98 / 100`, then repeatedly advance one year and call `update_indexes` for `BIG18` until it returns `MATH_OVERFLOW`. After that point the stored `borrow_index` is still below `MAX_BORROW_INDEX_RAY`, yet `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", 1.0)` both fail with `MATH_OVERFLOW` because they sync first. [7](#0-6)

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

**File:** contracts/pool/src/ops/mod.rs (L30-45)
```rust
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

**File:** common/src/rates/scaling.rs (L12-24)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}

/// Converts an asset-unit `cap` to a scaled `Ray` value, rounding down.
///
/// The division saturates at `i128::MAX` instead of panicking, so the cap check
/// fails open rather than trapping an entry path. The asset-to-RAY
/// rescale still panics on overflow; listings validate caps with
/// [`crate::validation::require_cap_within_asset_domain`]. Position accounting
/// uses [`calculate_scaled_supply`] and [`calculate_scaled_borrow`], which panic
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-356)
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
