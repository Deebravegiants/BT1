### Title
Unbounded accrued-value conversion permanently freezes an oversized market - (File: common/src/rates/simulate.rs)

### Summary
A sufficiently large market can grow `borrowed * borrow_index` beyond the `i128` value domain before `borrow_index` reaches its cap. The next interest accrual panics while reconstructing total debt, and because every market mutation accrues first, withdrawals, repayments, liquidations, and future index updates all fail. [1](#0-0) 

### Finding Description
`accrue_step` unconditionally converts the scaled borrow balance back to its index-scaled value with `scaled_to_original(env, borrowed, borrow_index)`. [2](#0-1)  `scaled_to_original` performs `scaled.mul(env, index)`, which panics with `MathOverflow` when the resulting RAY-scaled value exceeds `i128`. [3](#0-2) [4](#0-3) 

The borrow-index cap is applied only after calculating the new index; it does not bound the separately represented total-debt value used by accrual. [5](#0-4)  `global_sync` calls `accrue_step` for each elapsed chunk, and only stamps the market accrued after all chunks complete. [6](#0-5) 

Every mutating pool leg loads the market through `synced_market`, which invokes `global_sync` before the requested operation. [7](#0-6)  For example, repayment performs this sync before burning debt, while withdrawal performs it before resolving the withdrawal. [8](#0-7) [9](#0-8) 

### Impact Explanation
Once the scaled-debt product crosses the representable-value boundary, the market cannot recover through ordinary protocol actions. The public controller `update_indexes` call reaches `ops::market::accrue`, which loads the market and invokes `global_sync`; it panics before `mark_accrued` or `commit`, leaving `last_timestamp` unchanged. [10](#0-9)  Consequently, the same overflow repeats on every subsequent accrual.

Suppliers cannot withdraw, borrowers or third parties cannot repay, and liquidators cannot progress through paths that touch the frozen market. The repository’s regression test demonstrates that `update_indexes`, `withdraw`, and `repay` all fail with `MATH_OVERFLOW` while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`. [11](#0-10)  This permanently freezes the market’s token funds unless a privileged contract upgrade changes the accounting logic.

### Likelihood Explanation
The trigger is reachable by an unprivileged address, but requires an extremely large admitted market and sustained high utilization. A single attacker can create one account that supplies the debt asset, create another that supplies collateral, draw the debt asset through `borrow`, and wait until accrued value exceeds the numeric boundary. No privileged call is required to trigger the failure: a later permissionless controller `update_indexes` call commits accrual through the pool.

The existing proof uses an 18-decimal asset with `1e27` base units supplied and `9.8e26` borrowed, then advances time until accrual fails. [12](#0-11)  The scale and holding period make exploitation costly and configuration-dependent, so the issue is not an immediate small-transaction griefing vector.

### Recommendation
Bound each market’s scaled share total so the maximum index cannot make `scaled * index` overflow. Enforce this at both `supply` and `borrow` using conservative ceiling arithmetic, or cap `borrow_index`/`supply_index` and market share totals at a common safe value domain. At minimum, make accrual handle an over-domain aggregate gracefully by clamping or socializing the excess rather than panicking before `last_timestamp` can advance. The admitted cap validation should account for worst-case index growth instead of only checking the initial token-to-RAY conversion.

### Proof of Concept
1. Configure or use an admitted 18-decimal debt market whose caps allow at least `1e27` base units, plus a collateral market sufficient to borrow it.
2. As one unprivileged caller:
   - `supply(caller, 0, spoke_id, [(HubAssetKey { hub_id, asset: DEBT }, 1_000_000_000_000_000_000_000_000_000)])`
   - `supply(caller, 0, spoke_id, [(HubAssetKey { hub_id, asset: COLLATERAL }, collateral_amount)])`
   - `borrow(caller, borrow_account_id, [(HubAssetKey { hub_id, asset: DEBT }, 980_000_000_000_000_000_000_000_000)], Some(caller))`
3. Keep utilization near 98% until `borrowed * borrow_index / RAY` exceeds `i128::MAX`; this can occur while `borrow_index < MAX_BORROW_INDEX_RAY`.
4. Submit `update_indexes(caller, [HubAssetKey { hub_id, asset: DEBT }])`. The pool reaches `global_sync → accrue_step → scaled_to_original` and reverts with `MathOverflow`. [13](#0-12) 
5. Subsequent `withdraw` or `repay` calls on that market fail before executing their respective mutations because both paths call `ops::load_leg → synced_market → global_sync`. [14](#0-13)

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-319)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L322-356)
```rust
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

**File:** common/src/rates/simulate.rs (L60-66)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);
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

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
```

**File:** contracts/pool/src/ops/mod.rs (L42-46)
```rust
/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
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

**File:** contracts/pool/src/ops/market.rs (L65-71)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
```
