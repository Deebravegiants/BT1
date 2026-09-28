### Title
Unchecked index accrual overflow permanently freezes an oversized market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
A market whose scaled debt or supply value grows beyond `i128::MAX` makes every subsequent accrual panic with `MathOverflow`. Because `update_indexes` and state-changing market operations accrue before mutating, suppliers can neither withdraw nor repayments clear the frozen debt.

### Finding Description
`Controller::update_indexes` is callable by an authorized unprivileged caller and forwards the selected `HubAssetKey`s to the pool. [1](#0-0)  The pool loads each market and invokes `interest::global_sync` before committing state. [2](#0-1)  `global_sync` calls `accrue_step` for every elapsed interval. [3](#0-2)  That step first unscales both stored positions with `scaled_to_original`, then computes utilization, rate, and the next borrow index. [4](#0-3)  `scaled_to_original` delegates to `Ray::mul`, whose fixed-point multiplication panics when the scaled value times the index exceeds `i128`. [5](#0-4) [6](#0-5) 

The borrow-index cap does not prevent this condition: `update_borrow_index` caps the index at `10^36` raw RAY, but a sufficiently large scaled borrow balance can overflow when multiplied by an index far below that cap. [7](#0-6)  The repository's integration test demonstrates this exact state transition: a 1-billion-whole-token, 18-decimal market at 98% utilization eventually fails inside `scaled_to_original`, after which both a 1-unit withdrawal and a repayment revert with `MATH_OVERFLOW`. [8](#0-7) 

### Impact Explanation
Once the overflow threshold is crossed, the market's stored scaled balances cannot be converted under the new index, so accrual-dependent operations consistently revert. Supplier funds, borrower collateral economically tied to the account, and unclaimed yield in that market become permanently frozen unless a contract upgrade changes the arithmetic.

### Likelihood Explanation
An unprivileged attacker cannot trigger this with an ordinary-sized position; they must first create an extremely large admitted position and sustain utilization long enough for index growth to make `scaled * index` exceed `i128::MAX`. Where an asset's configured cap and real token liquidity permit that scale, the sequence uses only `supply`, `borrow`, and permissionless `update_indexes`; no privileged action, oracle manipulation, leaked key, or malformed parameter is required.

### Recommendation
Constrain admitted scaled supply and debt so `scaled * MAX_*_INDEX` cannot overflow before the configured index ceiling is reached, or implement saturating/wider-value accrual that clamps interest while still allowing withdrawals and repayments. Add a pre-accrual representability guard that safely freezes further interest rather than reverting all market operations.

### Proof of Concept
1. A caller creates an account and supplies a very large 18-decimal listed asset, for example the test fixture's `principal = 1_000_000_000 * 10^18` native units.
2. The same caller supplies sufficient listed collateral to the same account and calls `borrow(caller, account_id, [(BIG18, principal * 98 / 100)], Some(caller))`.
3. The caller lets ledger time advance until the market's projected borrow value approaches `i128::MAX`, then calls `update_indexes(caller, [BIG18])`.
4. `accrue_step` evaluates `scaled_to_original(borrowed, borrow_index)` and panics with `GenericError::MathOverflow`.
5. Subsequent `repay`, `withdraw`, liquidation, cleanup, and governance rate-model updates touching `BIG18` run accrual first and hit the same panic, leaving the market frozen.

### Citations

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

**File:** common/src/rates/simulate.rs (L51-67)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
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
