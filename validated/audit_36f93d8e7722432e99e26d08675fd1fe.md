### Title
Accrued debt overflows `i128` before the borrow-index cap, permanently freezing a market - (File: common/src/rates/scaling.rs)

### Summary
A sufficiently large market at sustained high utilization can make `scaled_to_original(borrowed, borrow_index)` overflow `i128` before `MAX_BORROW_INDEX_RAY` engages. Because every pool mutation accrues interest before changing state, the market then rejects `update_indexes`, withdrawals, repayments, and liquidations indefinitely. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::update_indexes(caller, assets)` is permissionless and forwards the requested `HubAssetKey` list to the pool. [3](#0-2)  The pool loads each market and calls `interest::global_sync`, which invokes `accrue_step` using the stored scaled debt and previous borrow index. [4](#0-3) [5](#0-4) 

At large scaled-debt values, converting the accrued debt back to asset/RAY value can overflow `i128` even though the stored index remains below `MAX_BORROW_INDEX_RAY`; the existing regression test demonstrates that the index cap never engages. [6](#0-5)  All ordinary mutation legs enter through `ops::load_leg`, which calls `synced_market` and therefore attempts the same failing accrual before any repay, withdraw, seize, or other state change. [7](#0-6) [8](#0-7) 

An unprivileged caller can create the condition through the public `supply` and `borrow` entrypoints on markets whose configured caps admit the position, then call `update_indexes` after enough ledger time has passed. [9](#0-8) [10](#0-9)  Once the overflow occurs, the failing accrual prevents the market timestamp from being committed, so retrying the operation later still encounters the overflow.

### Impact Explanation
All user funds and debt positions in the affected `(hub_id, asset)` market become permanently frozen under the deployed code. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot reduce risk, and permissionless index synchronization cannot recover the market without a code upgrade. The harness explicitly demonstrates failed `withdraw` and `repay` calls after the accrual overflow. [11](#0-10) 

### Likelihood Explanation
This is a Medium likelihood, high-impact condition: it requires very large supply/debt totals, high utilization, and configured caps that permit those totals. The relevant operations themselves are unprivileged, and the included test constructs the state using a billion-scale 18-decimal market with 98% of it borrowed. [12](#0-11) 

### Recommendation
Perform index accrual and debt-value reconstruction in widened arithmetic, or return a checked/saturated result before narrowing to `i128`. Clamp or cap the projected borrow index before unscaling accumulated debt, and commit a recoverable accrual state rather than leaving `last_timestamp` behind a permanently failing calculation. Add regression coverage at maximum permitted caps and asset decimals for supply, borrow, withdraw, repay, liquidation, and `update_indexes`.

### Proof of Concept
The existing harness test constructs a large 18-decimal market, supplies `BILLION * 10^18`, borrows 98%, repeatedly advances ledger time, and calls `update_indexes` until accrual returns `MathOverflow`. [13](#0-12) 

```rust
let principal = BILLION * 10i128.pow(18);
let debt = principal / 100 * 98;

t.supply_raw(BOB, "BIG18", principal);
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() {
        break;
    }
}

assert_contract_error(
    t.try_withdraw_raw(BOB, "BIG18", 1),
    errors::MATH_OVERFLOW,
);
assert_contract_error(
    t.try_repay(ALICE, "BIG18", 1.0),
    errors::MATH_OVERFLOW,
);
```

The test observes `borrow_index < MAX_BORROW_INDEX_RAY`, proving that the value conversion overflows before the intended index ceiling can protect the market. [14](#0-13)

### Citations

**File:** contracts/pool/src/interest.rs (L25-32)
```rust
    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
```

**File:** contracts/pool/src/interest.rs (L40-48)
```rust
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-319)
```rust
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

**File:** contracts/controller/src/lib.rs (L94-101)
```rust
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
```

**File:** contracts/controller/src/lib.rs (L107-115)
```rust
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

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/pool/src/ops/market.rs (L68-71)
```rust
    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
```

**File:** contracts/pool/src/ops/mod.rs (L30-33)
```rust
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
```

**File:** contracts/pool/src/ops/mod.rs (L43-46)
```rust
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```
