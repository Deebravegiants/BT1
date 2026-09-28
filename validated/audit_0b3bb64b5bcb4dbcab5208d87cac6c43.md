### Title
RAY-denominated interest accrual can overflow and permanently freeze a heavily utilized market - (File: common/src/rates/simulate.rs)

### Summary
High. A sufficiently large, heavily borrowed market can grow until a `scaled_amount * index` product no longer fits in `i128`. Because every pool mutation performs accrual before acting, the resulting `MathOverflow` blocks repayment, withdrawal, liquidation, bad-debt cleanup, index updates, and recapitalization for that market.

### Finding Description
Every mutating pool path loads its market through `synced_market`, which invokes `interest::global_sync` before processing the requested operation. `global_sync` calls `accrue_step`, which reconstructs the market’s RAY-denominated borrowed and supplied values by calling `scaled_to_original` for `borrowed * borrow_index` and `supplied * supply_index`. That conversion uses `Ray::mul`, which ultimately returns `None` when the exact half-up quotient cannot fit `i128`, and the caller converts that into a contract `MathOverflow` panic. Once either aggregate value crosses the `i128` ceiling, subsequent accrual fails before the operation’s business logic can execute. The public controller path is `update_indexes(caller, assets)`, which is permissionless and calls `markets::update_indexes`; the same accrual also precedes controller-routed `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, and `recapitalize`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Impact Explanation
The overflow is not a temporary rejection of one malformed input: accrual is mandatory before all market mutations, so after the state reaches the overflow domain every later mutation that touches the market fails at the same arithmetic step. The in-tree test demonstrates that repayment and withdrawal revert with `MATH_OVERFLOW` after `update_indexes` reaches the condition, permanently trapping supplier balances and preventing borrowers or liquidators from settling the debt. This is a permanent freezing of user funds and can leave the affected market economically insolvent because neither voluntary repayment nor liquidation can proceed. [6](#0-5) [7](#0-6) 

### Likelihood Explanation
An unprivileged attacker can initiate the condition by supplying and borrowing very large positions, maintaining high utilization, and then repeatedly calling `update_indexes` as time elapses. The tested scenario uses one billion whole 18-decimal tokens supplied and 98% borrowed under the XLM rate curve, then advances time until `update_indexes` panics before `MAX_BORROW_INDEX_RAY` is reached. The exploit requires a market whose admitted caps and available liquidity permit exposure near the documented RAY domain ceiling, but it does not require privileged access, malformed protocol parameters, oracle manipulation, or control of another user’s account. [8](#0-7) [9](#0-8) 

### Recommendation
Do not allow accrued aggregate values to become unrepresentable while the borrow index remains below its intended cap. Before updating an index, compute the post-update aggregate in a saturating or widened representation and clamp the index to the largest value that keeps both `borrowed * borrow_index` and `supplied * supply_index` within the RAY/`i128` domain. Apply the same bound inside `update_borrow_index`, `update_supply_index`, and each `scaled_to_original` call used by accrual. Prefer deterministic clamping and market-level borrowing disablement over a panic; additionally enforce a market-size invariant that keeps the maximum possible accrued aggregate below `i128::MAX` rather than relying only on token-unit caps. [10](#0-9) [11](#0-10) 

### Proof of Concept
The repository already contains an executable reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

1. Create a listed 18-decimal market and disable its utilization ceiling in the test fixture.
2. Supply `1_000_000_000 * 10^18` base units as `BOB`.
3. Supply sufficient collateral as `ALICE` and borrow 98% of the supplied `BIG18`.
4. Advance ledger time in yearly increments and call controller `update_indexes` for `BIG18`.
5. Observe `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`.
6. Subsequent `withdraw` and `repay` calls also revert with `MATH_OVERFLOW` because both paths accrue first. [12](#0-11)

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

**File:** common/src/rates/simulate.rs (L51-64)
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
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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

**File:** common/src/rates/index.rs (L29-44)
```rust
pub fn update_supply_index(env: &Env, supplied: Ray, old_index: Ray, rewards_increase: Ray) -> Ray {
    if supplied == Ray::ZERO || rewards_increase == Ray::ZERO {
        return old_index;
    }

    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
```
