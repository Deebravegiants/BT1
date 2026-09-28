### Title
RAY-domain integer overflow in interest accrual permanently freezes a large high-utilization market - (`common/src/rates/index.rs`)

### Summary
A market with sufficiently large scaled debt can reach a borrow index at which `borrowed * borrow_index / RAY` no longer fits in `i128`, even though the stored index remains below `MAX_BORROW_INDEX_RAY`. Because every pool mutation first accrues interest, the first `MathOverflow` in `calculate_supplier_rewards` permanently blocks repayment, withdrawal, liquidation, bad-debt cleanup, recapitalization, and further index updates for that market. [1](#0-0) 

### Finding Description
`accrue_step` is invoked for every elapsed accrual chunk by `accrue_chunk`, which is called by `global_sync` before market mutations. [2](#0-1)  `calculate_supplier_rewards` separately computes `borrowed.mul(old_borrow_index)` and `borrowed.mul(new_borrow_index)`, then subtracts the values to obtain accrued interest. [3](#0-2)  Each multiplication is a RAY-scaled `i128` multiply-divide; the widened intermediate prevents intermediate overflow, but the final quotient still must fit `i128`. [4](#0-3) [5](#0-4) 

The borrow index ceiling is `1e36` raw RAY, equivalent to an index multiplier of `1e9`, while the debt-value ceiling is `i128::MAX`, approximately `1.70e38`. For example, scaled debt of `9.8e35` raw RAY overflows when the index multiplier is only about `174`, far below the index cap. The cap therefore cannot prevent the value overflow because the panicking value calculation occurs after the capped index has been computed and remains bounded. [6](#0-5) [1](#0-0) 

The permissionless controller entrypoint `update_indexes(caller, assets)` forwards the attacker-selected `HubAssetKey` vector to pool accrual. [7](#0-6) [8](#0-7)  Thereafter, `load_leg` calls `synced_market`, which calls `global_sync`, before supply, borrow, withdraw, or repay accounting. [9](#0-8) 

### Impact Explanation
This permanently freezes all funds in the affected market rather than merely rejecting one oversized call. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot close unhealthy positions, and bad-debt cleanup cannot complete because each operation first recomputes the same overflowing total debt. The repository’s regression test demonstrates that after the cliff, `update_indexes`, `withdraw`, and `repay` all fail with `MathOverflow`, while `borrow_index` remains below `MAX_BORROW_INDEX_RAY`. [10](#0-9) 

The trapped market also leaves protocol revenue and residual collateral associated with that market inaccessible through normal execution paths. Since the panic occurs before mutation or settlement, no smaller amount entered later avoids the failure; the state transition required to reduce the debt is itself unreachable.

### Likelihood Explanation
The trigger is economically expensive but reachable by an unprivileged account. It requires an admitted high-decimal asset market, enough liquidity and collateral to create a debt whose RAY-scaled share amount approaches the `i128` value ceiling divided by a reachable index, and sustained high utilization long enough for interest to raise the index across that threshold. No privileged parameter, oracle manipulation, leaked key, or malformed external object is required.

The repository’s concrete test creates a one-billion-whole-token, 18-decimal market, supplies the principal, and borrows 98% of it under the XLM-style rate curve. Advancing ledger time in yearly increments causes the first accrual that would represent debt above `i128::MAX` to fail, and all subsequent exit and repayment attempts fail in the same place. [11](#0-10) 

### Recommendation
Enforce a market-level debt-value ceiling before debt minting and before accrual commits, rather than relying on `MAX_BORROW_INDEX_RAY` alone. In particular:

- bound `borrowed * new_borrow_index / RAY` and `supplied * new_supply_index / RAY` so every stored accrual state remains representable;
- stop accrual at the last representable index instead of panicking during reward calculation;
- add a separate raw scaled-debt cap derived from `i128::MAX / MAX_BORROW_INDEX_RAY`;
- consider saturated or emergency accrual behavior that still permits repayments, withdrawals, liquidation, and bad-debt cleanup;
- add regression coverage for the exact transition immediately before and after the representable-value boundary.

### Proof of Concept
The repository already contains an end-to-end reproduction in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs`:

```text
1. Configure BIG18 as an 18-decimal market using xlm_curve.
2. Lift its supply and borrow caps.
3. BOB supplies principal = 1_000_000_000 * 10^18 base units.
4. ALICE supplies collateral in COL.
5. ALICE borrows principal * 98 / 100 of BIG18.
6. Advance ledger time one year at a time and call:
   update_indexes(caller, vec![HubAssetKey { hub_id, asset: BIG18 }])
7. Once borrowed * borrow_index / RAY exceeds i128::MAX, the call fails
   with MathOverflow.
8. Subsequent withdraw(BOB, BIG18, 1) and repay(ALICE, BIG18, amount)
   also fail with MathOverflow because both load the market through
   synced_market and execute global_sync first.
```

The test asserts that the failed borrow index is still below `MAX_BORROW_INDEX_RAY`, proving that the index cap does not prevent the RAY-value overflow. [12](#0-11)

### Citations

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

**File:** contracts/pool/src/interest.rs (L20-48)
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

/// Applies one compound step of `delta_ms` to indexes and protocol revenue.
///
/// The arithmetic lives in [`accrue_step`], shared with the read-only
/// `simulate_update_indexes` so the view and the mutator cannot drift.
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/math/fp_core.rs (L108-143)
```rust
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
