### Title
Unbounded RAY value arithmetic permanently freezes a high-balance market - (File: common/src/rates/simulate.rs)

### Summary

`accrue_step` multiplies total scaled borrow and supply shares by their respective indexes before the borrow-index ceiling can provide protection. [1](#0-0)  Once either aggregate value exceeds `i128::MAX`, `scaled_to_original` panics with `MathOverflow`. [2](#0-1)  This is analogous to the reported heap overflow: a value derived from attacker-controlled balances crosses the fixed-width arithmetic domain and converts later state transitions into an unconditional trap.

### Finding Description

Every pool accrual calls `accrue_chunk`, which delegates index progression, reward accounting, and revenue-share accounting to `accrue_step`. [3](#0-2)  `accrue_step` first computes `borrowed_original = borrowed * borrow_index` and `supplied_original = supplied * supply_index`; these RAY-scaled totals must fit in `i128`. [4](#0-3)  The borrow index is capped only after multiplying it by the next interest factor, while the already-overflowing total-debt value is computed both before and after that capped update. [5](#0-4) [6](#0-5) 

The permissionless `update_indexes` entrypoint invokes this pool accrual for caller-selected markets. [7](#0-6)  Because ledger time only advances, once the current aggregate scaled value no longer fits, there is no smaller valid accrual state to commit: the same operation is retried at the same or a later timestamp and continues to overflow.

The codebase contains a deterministic regression for this exact failure: a one-billion-token market at 98% utilization eventually makes `try_update_indexes_for` fail with `MathOverflow`, below `MAX_BORROW_INDEX_RAY`; subsequent `withdraw` and `repay` calls fail with the same error. [8](#0-7)  The project documentation also states that valid caps and bounded indexes do not ensure that future accrued values fit, and that value overflow can block repayment and withdrawal. [9](#0-8) 

### Impact Explanation

This permanently freezes every operation on the affected market that performs accrual, including borrower repayment, supplier withdrawal, liquidation, bad-debt cleanup, and index updates. [10](#0-9)  Suppliers cannot recover funds, borrowers cannot close debt, liquidators cannot repair underwater accounts, and protocol revenue tied to the market cannot be claimed.

The freeze is not merely temporary DoS: time cannot be moved backward, so after the aggregate share/index product crosses `i128::MAX`, every future accrual evaluates the same invalid arithmetic. [11](#0-10)  This maps to permanent freezing of user funds and can leave bad debt unresolved, creating protocol insolvency.

### Likelihood Explanation

The attack requires an unusually large market: for an 18-decimal asset, a one-billion-token book reaches the `i128` boundary when the relevant index approaches roughly `170x`; smaller books require proportionally larger index growth. [12](#0-11)  It also requires sustained high utilization and enough time for index growth.

Nevertheless, the state is reached through normal, unprivileged `supply`, `borrow`, and `update_indexes` calls; no privileged operation, leaked key, malformed token, oracle dishonesty, or external service is required once the configured market admits the required volume. [13](#0-12) [7](#0-6)  Given the severe and irreversible impact but substantial capital/time prerequisite, this is best assessed as Medium severity.

### Recommendation

Saturate or chunk aggregate-value calculations before multiplying scaled totals by indexes, rather than allowing `scaled_to_original` to panic inside accrual. [1](#0-0)  In particular:

- Compute utilization without materializing `borrowed * borrow_index` or `supplied * supply_index`, such as a widened-ratio comparison or capped quotient.
- Compute `calculate_supplier_rewards` as `borrowed * (new_index - old_index)` where safe, or use a saturating total-debt delta.
- Ensure the borrow-index cap engages before any market-total product can trap.
- Add a governance-facing index/value ceiling alarm, but do not rely on the alarm as the only safety mechanism.
- Extend the regression test so the market reaches the index cap cleanly instead of trapping on aggregate value.

### Proof of Concept

1. In a listed flash-compatible 18-decimal market with a supply cap admitting the position, call `supply` with `account_id = 0`, `caller = whale`, `spoke_id = S`, and `assets = [(HubAssetKey { hub_id: H, asset: TOKEN }, 1_000_000_000 * 10^18)]`. [14](#0-13) 
2. From a second account with sufficient collateral, call `borrow` for approximately 98% of that market's liquidity, for example `borrows = [(HubAssetKey { hub_id: H, asset: TOKEN }, 980_000_000 * 10^18)]`. [15](#0-14) 
3. Let time advance and repeatedly call `update_indexes(caller, [(H, TOKEN)])`; each call is permissionless apart from caller authorization. [7](#0-6) 
4. When `borrowed * borrow_index` exceeds `i128::MAX`, `scaled_to_original` in `accrue_step` panics before the borrow-index cap can complete the update. [1](#0-0) [2](#0-1) 
5. Thereafter `update_indexes`, `repay`, `withdraw`, and liquidation paths for that market all attempt accrual first and revert with `MathOverflow`; the existing harness proves both repayment and one-unit withdrawal fail after the index-update cliff. [16](#0-15)

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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** contracts/pool/src/interest.rs (L20-52)
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

    cache.set_borrow_index(step.borrow_index);
    cache.set_supply_index(step.supply_index);
    cache.accrue_revenue(step.revenue_shares);
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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-356)
```rust
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

**File:** docs/reference/formulas.md (L429-437)
```markdown
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```

**File:** contracts/controller/src/lib.rs (L93-115)
```rust
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
    }
```
