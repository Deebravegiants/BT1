### Title
A large high-utilization market can permanently overflow interest accrual and freeze repayment, withdrawal, and liquidation - ([File: contracts/pool/src/interest.rs](contracts/pool/src/interest.rs))

### Summary
Every pool mutation calls `interest::global_sync` before performing the operation, and each accrual chunk multiplies total scaled debt or supply by the current index using checked RAY arithmetic. If the scaled market balance is sufficiently large, interest growth causes that multiplication to exceed `i128::MAX` before either index reaches its configured `1e36` ceiling, producing `MathOverflow` on every subsequent accrual. Because repayment, withdrawal, liquidation, and index updates all sync the market first, the market becomes permanently unusable rather than merely reverting one oversized user call.

### Finding Description
`ops::synced_market` loads market state and invokes `interest::global_sync`, and the same helper is used by pool operations such as `repay`, `withdraw`, borrow, supply, and liquidation execution. [1](#0-0)  `global_sync` iterates elapsed time in chunks and calls `accrue_chunk`, which delegates valuation and index growth to `accrue_step`. [2](#0-1) [3](#0-2) 

`accrue_step` converts total scaled debt and supply into RAY-denominated values and later multiplies `borrowed` by both the old and newly compounded borrow index. [4](#0-3)  Those conversions use `Ray::mul`, which performs checked multiplication and panics with `MathOverflow` when the RAY value cannot fit `i128`. [5](#0-4) [6](#0-5) 

The public path is `Controller::update_indexes(caller, assets)`, which authorizes the unprivileged caller and forwards the market list to the pool's owner-only `update_indexes`. [7](#0-6) [8](#0-7)  Once an accrual multiplication overflows, the transaction aborts before `last_timestamp` is committed, so every later attempt starts from the same elapsed interval and hits the same overflow.

### Impact Explanation
This is a permanent market-level denial of service: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot seize, flash loans cannot settle, and `update_indexes` cannot recover the market because all of those paths run accrual before state changes. A user can intentionally create or use a very large high-utilization market and then let it remain inactive until the debt or supply valuation crosses the `i128` boundary.

The production documentation acknowledges that accrued market totals must fit the RAY domain and that value overflow can occur before index ceilings, blocking repayment and withdrawal; the regression test demonstrates that this is not merely theoretical. [9](#0-8) [10](#0-9) 

### Likelihood Explanation
Exploitation requires an unusually large market book and sustained high utilization long enough for index growth to push `scaled_amount * index / RAY` above `i128::MAX`. The demonstrated test uses a billion whole tokens at 18 decimals and approximately 98% utilization; it reaches the cliff through repeated yearly time advancement while the borrow index remains below `MAX_BORROW_INDEX_RAY`. [11](#0-10) 

The caller does not need privileges once such state exists: `update_indexes` only requires caller authorization and the controller forwards the call to the pool. [7](#0-6)  The required liquidity scale and time dependence make this less likely than an immediate attacker-controlled revert, but the consequence is permanent freezing of market funds.

### Recommendation
Accrual must not rely on total RAY value fitting `i128` after index growth. Concretely:

- Detect the representable-value boundary before compounding and clamp the borrow and supply indexes to values for which both `borrowed * borrow_index` and `supplied * supply_index` remain representable.
- Perform utilization and accrual using widened `I256` arithmetic or saturation-compatible helpers, then return checked in-range indexes.
- Ensure index ceilings are enforced before calculating `new_total_debt`; otherwise `MAX_BORROW_INDEX_RAY` alone cannot prevent this overflow.
- Add an emergency-safe accrual path so repayment and bad-debt cleanup can still execute at the saturation boundary instead of being blocked by the pre-operation sync.
- Add a regression test equivalent to `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`, asserting that `update_indexes`, `repay`, and `withdraw` remain callable at the numeric ceiling rather than panicking with `MathOverflow`.

### Proof of Concept
The existing harness reproduces the freeze by creating a billion-token market, borrowing approximately 98% of it, advancing time until `update_indexes` returns `MathOverflow`, and then showing that withdrawal and repayment fail for the same reason:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.borrow_raw(ALICE, "BIG18", debt);

// Advance time until accrual fails.
assert_contract_error(
    t.try_update_indexes_for(&["BIG18"]),
    errors::MATH_OVERFLOW
);

assert!(last.borrow_index < MAX_BORROW_INDEX_RAY);
assert_contract_error(
    t.try_withdraw_raw(BOB, "BIG18", 1),
    errors::MATH_OVERFLOW
);
assert_contract_error(
    t.try_repay(ALICE, "BIG18", 1.0),
    errors::MATH_OVERFLOW
);
```

The test's assertion that `borrow_index < MAX_BORROW_INDEX_RAY` proves the index ceiling does not prevent the underlying multiplication overflow. [12](#0-11)

### Citations

**File:** contracts/pool/src/ops/mod.rs (L29-34)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
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

**File:** contracts/pool/src/interest.rs (L39-52)
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

    cache.set_borrow_index(step.borrow_index);
    cache.set_supply_index(step.supply_index);
    cache.accrue_revenue(step.revenue_shares);
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

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
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

**File:** contracts/pool/src/lib.rs (L174-180)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
    }
```

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
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
