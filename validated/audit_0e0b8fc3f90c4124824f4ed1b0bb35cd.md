### Title
RAY multiplication overflow permanently freezes a high-utilization market - ([File: common/src/math/fp.rs](common/src/math/fp.rs))

### Summary
The pool represents balances and indexes as `RAY`-scaled `i128` values. Interest accrual can raise the borrow index far enough that multiplying scaled debt by that index exceeds `i128::MAX`. Because market accrual runs before supply, borrow, repay, withdraw, and liquidation accounting, the resulting `MathOverflow` panic makes the market unusable rather than capping or saturating the index.

### Finding Description
`Controller::supply`, `Controller::borrow`, `Controller::withdraw`, and `Controller::repay` expose the user actions needed to build a very large, highly utilized position [1](#0-0) . The pool accrues interest through `global_sync`, which repeatedly calls `accrue_chunk` and `accrue_step` until the elapsed interval is consumed [2](#0-1) . During utilization and balance calculations, scaled supply/debt is converted back into RAY-denominated principal with `scaled_to_original` [3](#0-2) . That conversion uses `Ray::mul`, which delegates to `mul_div_half_up` and panics with `MathOverflow` when the product does not fit into `i128` [4](#0-3) .

The repository's own adversarial test demonstrates the failure mode: after constructing a billion-token market at sustained high utilization, `update_indexes` eventually returns `MATH_OVERFLOW`; subsequent `withdraw` and `repay` calls fail with the same error [5](#0-4) .

### Impact Explanation
All funds in the affected market can be permanently frozen. Suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot clear or rescue positions because every state-changing path performs the same overflowing scaled-value calculation before completing the operation. This satisfies permanent freezing of user funds and can also leave protocol revenue unclaimable in that market.

### Likelihood Explanation
An unprivileged user can create the prerequisite state through ordinary `supply` and `borrow` calls, and any user can advance the market with `update_indexes`. Exploitation requires a listed market whose caps and collateral permit an extremely large position at high utilization for enough ledger time for index growth to reach the `i128` boundary. It therefore depends on market scale and configuration, but does not require privileged access, malformed authorization, a compromised oracle, or external software.

### Recommendation
Bound the stored debt and supply values together with their indexes, not just the index itself. Before applying an index update, calculate whether `scaled_balance * new_index` fits in the protocol's integer domain; if it does not, fail early with a market-specific recovery path or clamp the index at the largest safe value. Accrual should also avoid recomputing utilization through an overflowing unscale operation—use checked arithmetic and stop or mark the market at a defined safe boundary. Regression tests should cover withdraw, repay, liquidation, `clean_bad_debt`, and `claim_revenue` at the boundary.

### Proof of Concept
The repository already contains a reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);
```

The test then repeatedly advances the ledger and calls `update_indexes` until the call returns `MATH_OVERFLOW` [6](#0-5) . It verifies that the index cap did not prevent the value overflow [7](#0-6)  and that both withdrawal and repayment subsequently fail [8](#0-7) .

### Citations

**File:** contracts/controller/src/lib.rs (L90-133)
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
    }

    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
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

**File:** contracts/pool/src/cache/scale.rs (L19-27)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-356)
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
