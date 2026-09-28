### Title
Debt-value overflow during accrual permanently freezes a market - ([File: common/src/rates/scaling.rs])

### Summary
An unprivileged user can push a sufficiently large, highly utilized market past the representable RAY debt-value range, after which `accrue_step` panics before committing state. Because every pool operation accrues before mutating the market, subsequent `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, and `update_indexes` calls for that market revert indefinitely. [1](#0-0) 

### Finding Description
`accrue_step` computes the market’s unscaled debt as `scaled_to_original(borrowed, borrow_index)` before deriving utilization, the borrow rate, the next index, and accrued rewards. [2](#0-1)  `scaled_to_original` delegates to `Ray::mul`, which evaluates `scaled * index / RAY` through `mul_div_half_up`. [3](#0-2)  When the resulting RAY-denominated debt value exceeds `i128::MAX`, `mul_div_half_up` panics with `GenericError::MathOverflow`. [4](#0-3) 

The pool runs `global_sync` whenever `elapsed_ms() > 0`, splitting the interval into bounded chunks but applying the same panicking valuation to each chunk. [5](#0-4)  `ops::load_leg` calls `synced_market` before returning the position, so repayments, withdrawals, supplies, borrows, and other position legs cannot bypass accrual. [6](#0-5)  The controller’s `update_indexes` entrypoint is permissionless and calls the pool accrual path, so any caller can trigger the state transition attempt once the market has crossed the arithmetic boundary. [7](#0-6) 

The borrow-index cap does not prevent this condition because the cap applies to the index value itself, not to `borrowed * index / RAY`; a large `borrowed` can make the debt value exceed `i128::MAX` while the index remains below `MAX_BORROW_INDEX_RAY`. [8](#0-7)  The repository’s regression test explicitly observes `MATH_OVERFLOW` before the index cap and then confirms that both withdrawal and repayment fail with the same error. [9](#0-8) 

### Impact Explanation
This is a permanent freezing of all funds and debt operations in the affected market. Suppliers cannot withdraw collateral, borrowers cannot repay, liquidators cannot clear the account, and index updates cannot advance past the overflowing step. The failed accrual occurs before `Cache::commit`, leaving `last_timestamp` unchanged and causing every subsequent operation to retry the same overflowing computation. [10](#0-9) 

The impact is market-wide rather than limited to the attacker’s own position because `borrowed`, `supplied`, and the indexes are global market totals used by every leg touching that `(hub, asset)` book. [11](#0-10) 

### Likelihood Explanation
Exploitation requires a market whose admitted cap and liquidity allow debt-share value to approach the representable RAY bound, together with enough elapsed high-interest accrual for the debt valuation to overflow. A single funded caller can supply the borrowed asset, supply separate collateral, borrow at high utilization, and repeatedly call `update_indexes`; no privileged role or leaked key is needed. [7](#0-6) 

The likelihood is constrained by the need for whale-scale balances and an accrual period sufficient to grow the index. Once the boundary is crossed, however, the freeze is deterministic and cannot be undone by an ordinary protocol action because all state-changing exits accrue first. [1](#0-0) 

### Recommendation
Bound the next borrow index by both `MAX_BORROW_INDEX_RAY` and the largest index for which `borrowed * new_index / RAY` remains representable, using `I256` or checked arithmetic for the bound calculation. When that market-specific bound is reached, stop borrower interest growth deterministically instead of panicking inside `scaled_to_original`, and apply the same representability analysis to supplied-value growth. [12](#0-11) 

Alternatively, separate market valuation needed for rate calculation from user exit accounting and provide a checked accrual path that permits repayment, withdrawal, liquidation, and bad-debt cleanup even when aggregate displayed value is unrepresentable. Add a regression test based on the existing large-market scenario asserting that `update_indexes`, `repay`, `withdraw`, and `liquidate` remain executable at the bound. [9](#0-8) 

### Proof of Concept
1. An attacker calls `Controller::supply(caller, 0, spoke_id, [(BIG18, 1_000_000_000 * 10^18)])`, creating very large BIG18 liquidity. [13](#0-12) 
2. The attacker supplies enough collateral in another listed asset and calls `Controller::borrow(caller, account_id, [(BIG18, debt)], None)` until BIG18 utilization is near its maximum. [14](#0-13) 
3. After ledger time advances, the attacker calls `Controller::update_indexes(caller, [BIG18])`. [7](#0-6) 
4. The pool accrual reaches `scaled_to_original(borrowed, borrow_index)` while `borrowed * borrow_index / RAY > i128::MAX`, so `mul_div_half_up` returns no representable result and raises `MathOverflow`. [15](#0-14) 
5. The failed call leaves `last_timestamp` in the past because it occurs before `mark_accrued` and `commit`, so later `repay`, `withdraw`, `liquidate`, or `update_indexes` calls repeat the same overflowing accrual and revert. [16](#0-15) 
6. The existing test demonstrates this exact sequence and asserts `MATH_OVERFLOW` for index update, withdrawal, and repayment after the market crosses the bound. [17](#0-16)

### Citations

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

**File:** common/src/rates/simulate.rs (L60-71)
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
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp_core.rs (L108-118)
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

**File:** contracts/controller/src/lib.rs (L90-102)
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
```

**File:** contracts/controller/src/lib.rs (L104-115)
```rust
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

**File:** contracts/pool/src/cache/mod.rs (L30-41)
```rust
pub(crate) struct Cache {
    env: Env,
    hub_asset: HubAssetKey,
    params: MarketParams,
    last_timestamp: u64,
    current_timestamp: u64,
    supplied: Ray,
    borrowed: Ray,
    revenue: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    cash: i128,
```

**File:** contracts/pool/src/cache/mod.rs (L73-85)
```rust
    /// Persists the full market state and returns a snapshot for events.
    pub(crate) fn commit(&self) -> MarketStateSnapshot {
        let state = PoolStateRaw {
            supplied: self.supplied.raw(),
            borrowed: self.borrowed.raw(),
            revenue: self.revenue.raw(),
            borrow_index: self.borrow_index.raw(),
            supply_index: self.supply_index.raw(),
            last_timestamp: self.last_timestamp,
            cash: self.cash,
        };
        storage::write_state(&self.env, &self.hub_asset, &state);
        self.snapshot()
```
