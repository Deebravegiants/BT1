### Title
Accrual integer overflow permanently freezes a large market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
The accrual engine multiplies total scaled supply or debt by its RAY index before checking whether that value still fits in `i128`, causing `MathOverflow` and permanently blocking every operation that first synchronizes the market. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`accrue_step` unconditionally evaluates `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` to calculate utilization. [1](#0-0) 

`scaled_to_original` calls `Ray::mul`, and the underlying multiplication raises `MathOverflow` when the RAY-denominated result cannot be represented by `i128`; there is no pre-check against the remaining numeric domain. [2](#0-1) [4](#0-3) 

The failure occurs before `update_borrow_index` can clamp the index to `MAX_BORROW_INDEX_RAY`, so the configured index ceiling does not protect the market from overflowing its total-value representation. [5](#0-4) [6](#0-5) 

`global_sync` runs this accrual before the pool mutation and therefore the panic aborts the calling operation before repayment, withdrawal, liquidation, or cleanup can change the market state. [3](#0-2) [7](#0-6) 

An unprivileged caller reaches the path through `controller.update_indexes(caller, assets)`; the controller authenticates the caller and forwards the selected `HubAssetKey` list to the pool. [8](#0-7) [9](#0-8) 

### Impact Explanation
Once `scaled_amount * index / RAY` exceeds `i128::MAX`, all ordinary exits and debt-reducing operations for that market revert during accrual, permanently freezing supplier funds and preventing repayment or liquidation of the associated debt. [10](#0-9) [11](#0-10) 

The included executable test demonstrates that `update_indexes` fails with `MathOverflow`, the borrow index remains below `MAX_BORROW_INDEX_RAY`, and subsequent `withdraw` and `repay` attempts fail with the same error. [11](#0-10) 

### Likelihood Explanation
This requires a market whose stored scaled exposure is large enough that index growth makes its total RAY value exceed `i128::MAX`; the documented admission ceiling is approximately 170.14 billion whole tokens, before index growth. [12](#0-11) 

The trigger transaction is permissionless once that state exists: a caller only needs to submit `update_indexes` for the affected asset, while an attacker can also build the required exposure by supplying collateral and borrowing within configured caps. [8](#0-7) [13](#0-12) 

This is best classified as Medium because the impact is permanent freezing of market funds, but reaching the arithmetic cliff requires an extremely large market state rather than a small malformed amount. [14](#0-13) [15](#0-14) 

### Recommendation
Represent aggregate market values and accrual intermediates in a wider type such as `I256`, or explicitly detect the impending product overflow before `scaled_to_original` and transition the market into a bounded terminal state that still permits repayment and withdrawal. [16](#0-15) [1](#0-0) 

At minimum, compute `borrowed * borrow_index` and `supplied * supply_index` with a non-trapping overflow check, clamp further index growth before the value exceeds the RAY domain, and add a regression test that exits and repayment remain callable at that boundary. [17](#0-16) [11](#0-10) 

### Proof of Concept
1. Configure a high-decimal market and a collateral market with caps sufficiently raised to admit the exposure, matching the existing harness test setup. [18](#0-17) 
2. Supply `BILLION * 10^18` base units of the target asset and use collateral to borrow 98% of it. [19](#0-18) 
3. Advance ledger time and repeatedly call the permissionless `update_indexes` path for the target asset. [8](#0-7) [20](#0-19) 
4. The next accrual returns `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`, proving that value overflow occurs before the index cap can stop it. [21](#0-20) 
5. `withdraw` and `repay` then both revert with `MathOverflow`, demonstrating permanent market freeze. [22](#0-21)

### Citations

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

**File:** common/src/rates/scaling.rs (L12-15)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** common/src/math/fp.rs (L49-57)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }

    /// Divides this value by `other`, rounding the result half up.
    pub fn div(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, RAY, other.0))
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

**File:** contracts/pool/README.md (L159-167)
```markdown
Each mutation of an existing market runs this sequence:

```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
```

**File:** contracts/controller/src/markets.rs (L118-120)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-319)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L322-344)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L348-356)
```rust
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

**File:** common/src/math/fp_core.rs (L177-200)
```rust
/// Computes `floor(x * y / d)`, saturating to `i128::MAX` (or `i128::MIN` for a negative
/// quotient) instead of panicking if the result does not fit in `i128`. Panics with
/// `GenericError::DivisionByZero` if `d == 0`.
pub fn mul_div_floor_saturating(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    require_nonzero_divisor(env, d);
    if let Some(quotient) = x
        .checked_mul(y)
        .and_then(|product| div_floor_i128(product, d))
    {
        return quotient;
    }
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    div_floor_i256(
        env,
        &x256.mul(&y256),
        &d256,
        quotient_is_nonnegative(x, y, d),
    )
    .to_i128()
    .unwrap_or(if quotient_is_negative(x, y, d) {
        i128::MIN
    } else {
        i128::MAX
    })
```
