### Title
Index accrual can overflow aggregate debt value and permanently freeze a market - (File: common/src/rates/simulate.rs)

### Summary
A market whose scaled borrow or supply total is large enough can reach an `i128` overflow during ordinary interest accrual before the configured index ceiling is reached. Once this occurs, `update_indexes`, `withdraw`, `repay`, liquidation, and other state-changing calls repeatedly fail because each path must accrue before mutating the market. This permanently freezes all supplier funds in the affected market unless an upgrade or other privileged recovery path is available.

### Finding Description
The controller exposes permissionless `update_indexes`, which forwards a caller-selected list of hub assets to the pool. [1](#0-0) [2](#0-1)  The pool processes each market by loading its cache, running `interest::global_sync`, and committing the result. [3](#0-2)  `global_sync` applies elapsed time in bounded chunks, but every chunk invokes `accrue_step`. [4](#0-3) [5](#0-4) 

`accrue_step` first computes aggregate debt and supply values through `scaled_to_original`. [6](#0-5)  `scaled_to_original` multiplies the stored scaled amount by the current index using checked RAY arithmetic. [7](#0-6) [8](#0-7)  If the resulting aggregate value exceeds `i128::MAX`, the helper panics with `MathOverflow`. [9](#0-8) 

The borrow index is nominally capped at `MAX_BORROW_INDEX_RAY`, but that bound is only checked after the already-overflowing aggregate value calculations. [10](#0-9) [11](#0-10)  For sufficiently large scaled totals, `scaled * index / RAY` overflows at an index far below the nominal `1000x` index ceiling. [12](#0-11) 

### Impact Explanation
The failed accrual runs before the pool commits a new timestamp, so retrying the same market includes at least as much elapsed time and reaches the same overflowing multiplication. [13](#0-12)  Since every market mutation follows the load-accrue-mutate sequence, suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot recover the market through ordinary entrypoints. [14](#0-13) 

The repository’s own long-horizon test demonstrates the end state: an 18-decimal market holding one billion whole tokens at 98% utilization eventually fails `update_indexes` with `MathOverflow`, after which even a one-unit withdrawal and a small repayment fail with the same error. [15](#0-14)  This is a market-wide permanent freezing of user funds absent a privileged upgrade.

### Likelihood Explanation
Likelihood is low because the trigger requires an exceptionally large market—on the order of one billion whole 18-decimal tokens—high utilization, and enough elapsed time for the effective index to exceed the aggregate value ceiling. [16](#0-15)  The quantities are nevertheless within the protocol’s arithmetic domain: the documented maximum admitted token amount is approximately 170.14 billion whole tokens, while the documented value-overflow condition explicitly warns that accrual can block repayment and withdrawal before the index ceiling engages. [17](#0-16) 

No privileged call is needed to trigger the failure once a validly configured market permits the position size: `supply`, `borrow`, and `update_indexes` are callable through the controller, with `update_indexes` explicitly permissionless. [18](#0-17) [1](#0-0) 

### Recommendation
Bound aggregate scaled supply and debt by their respective value ceilings, not merely by token caps and a fixed index ceiling. In particular:

- Enforce a per-market invariant such as `scaled_total * MAX_*_INDEX / RAY <= i128::MAX` before minting additional supply or debt shares.
- Alternatively, cap each accrual at `min(MAX_*_INDEX, i128::MAX * RAY / scaled_total)` before evaluating `scaled_to_original`.
- Ensure the same bound covers both `borrowed * borrow_index` and `supplied * supply_index`, including protocol-revenue shares added between compounding chunks.
- Add a regression test proving that an extreme market reaches the aggregate cap through a controlled saturation path rather than entering an unrecoverable `MathOverflow` state.

### Proof of Concept
The repository already contains an executable reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [19](#0-18) 

Conceptually:

```text
1. Configure an 18-decimal market with caps large enough for the position.
2. Call Controller::supply(
       caller,
       account_id = 0,
       spoke_id,
       assets = [(HubAssetKey { hub_id, asset = BIG18 },
                  1_000_000_000 * 10^18)]
   ).
3. Supply sufficient collateral in another market.
4. Call Controller::borrow(
       caller,
       account_id,
       borrows = [(BIG18_key, supplied_principal * 98 / 100)],
       to = caller
   ).
5. Leave utilization high while ledger time advances.
6. Call Controller::update_indexes(caller, [BIG18_key]).
```

The call reaches `pool_update_indexes_call`, `ops::market::accrue`, `global_sync`, and `accrue_step`, where `borrowed * borrow_index` exceeds `i128::MAX` before the nominal borrow-index cap is reached. [20](#0-19) [21](#0-20)  The test then shows `update_indexes`, a one-unit withdrawal, and a small repayment all failing with `MathOverflow`. [22](#0-21)

### Citations

**File:** contracts/controller/src/lib.rs (L90-114)
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
```

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/controller/src/external/pool.rs (L109-116)
```rust
/// Accrues and persists market indexes through the current ledger time.
pub(crate) fn pool_update_indexes_call(
    env: &Env,
    pool_addr: &Address,
    hub_assets: &Vec<HubAssetKey>,
) {
    LiquidityPoolClient::new(env, pool_addr).update_indexes(hub_assets)
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

**File:** common/src/rates/simulate.rs (L60-67)
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

**File:** docs/reference/formulas.md (L421-437)
```markdown
fee; see [its settlement invariant](invariants.md#inv-strat-04).

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

**File:** contracts/pool/README.md (L161-167)
```markdown
```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
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
