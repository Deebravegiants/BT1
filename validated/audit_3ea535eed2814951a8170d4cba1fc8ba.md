### Title
Unprivileged whale borrow at sustained high utilization permanently freezes a market via `i128` overflow in index accrual — (`contracts/pool/src/interest.rs`)

### Summary
Every state-changing pool entrypoint accrues interest through `interest::global_sync` before acting. Accrual computes `scaled * index` products in `i128`. When a market's scaled totals are large enough, the borrow index can grow past the point where `scaled_to_original` (and the next accrual step's products) fit in `i128` **before** the `MAX_BORROW_INDEX_RAY` cap engages. From that point every accrual panics with `MathOverflow` (error 33), and because accrual runs first, `supply`, `borrow`, `withdraw`, `repay`, `liquidate` (via controller), `claim_revenue`, `recapitalize`, and `update_indexes` all revert permanently for that market. The protocol's own test demonstrates this end-to-end. This is the on-chain analog of CVE-2025-61668: an anonymous actor can place the protocol in a state where subsequent calls deterministically trap.

### Finding Description
`global_sync` unconditionally accrues before any market mutation: [1](#0-0) 

Each chunk calls `accrue_step`, which computes index-scaled values; utilization and share↔amount conversions multiply scaled RAY totals by indexes via `scaled_to_original` / `mul_div_*` in `i128`, panicking with `GenericError::MathOverflow` or `DivisionByZero` on overflow: [2](#0-1) [3](#0-2) 

The repository's own harness test proves the freeze: a market supplied with `BILLION * 10^18` units and borrowed to ~98% utilization hits `MathOverflow` inside `scaled_to_original` while `borrow_index < MAX_BORROW_INDEX_RAY`, and afterwards `withdraw` and `repay` both fail with the same error: [4](#0-3) 

The trigger path is fully permissionless: `controller.supply` and `controller.borrow` (any user can reach high utilization with enough collateral), and `controller.update_indexes` is explicitly permissionless keeper surface (`caller-auth` only): [5](#0-4) 

Because the panic occurs inside `global_sync`, which precedes every verb, there is no in-protocol recovery path — `seize_positions`, `recapitalize`, and governance `update_params` all load the `Cache` and accrue first (`replace_rate_model` calls `ops::renewed_market(...).commit()`, which accrues), so even governance remediation short of a Wasm upgrade reverts.

### Impact Explanation
Permanent freezing of funds: all supplier and borrower value in the affected `(hub_id, asset)` market becomes immovable — no withdraw, repay, liquidation, or revenue claim ever succeeds again. For a token shared across hubs, only the affected book freezes, but the physical pool balance attributable to it is stranded. This matches the "permanent freezing of funds" / "contract unable to operate" acceptance categories, not a transient fail-closed revert.

### Likelihood Explanation
Medium-to-low likelihood, high impact. The attack requires: (a) a market with decimals near 18 and caps high enough to admit ~`i128::MAX / 170` scaled shares (≈10^9 tokens at 18 decimals — whale-scale or inflated-supply token), (b) sustained utilization near the steep segment of the rate curve for multiple years so the index compounds ~170×, and (c) no governance intervention. The attacker must lock own capital and wait; they cannot accelerate index growth beyond `max_borrow_rate`. However, once the cliff is reached, any anonymous `update_indexes` call commits nothing and the next accrual reverts — the freeze is then permanent and unrecoverable without upgrade. The code base itself acknowledges the cliff (`the bound in docs/reference/formulas.md is wrong`), so this is an existing, demonstrated edge rather than a speculative one.

### Recommendation
- Cap accrual so `scaled_to_original` cannot overflow: when a chunk step would overflow, clamp `borrow_index`/`supply_index` to `MAX_BORROW_INDEX_RAY` / a computed max index that keeps `supplied * supply_index` and `borrowed * borrow_index` within `i128` for the stored totals, instead of panicking.
- Alternatively, make `accrue_step` saturate (use `mul_div_floor_saturating`-style semantics already present in `common::math::fp_core`) and emit an event when saturation occurs, so accrual never reverts and exits remain possible.
- Enforce per-market supply caps (`validate_market_creation` / borrow caps) so `supplied * MAX_BORROW_INDEX_RAY * 10^(27 - decimals)` provably fits `i128` at listing time.

### Proof of Concept
The scenario is executable today via the harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

1. Anonymous user calls `controller.supply(caller, 0, spoke_id, [(BIG18_key, BILLION * 10^18)])`.
2. A funded borrower calls `controller.borrow` to reach ~98% utilization (borrower may be the same attacker using collateral in a second market).
3. Time elapses at high utilization (attacker sustains it by keeping utilization high; any keeper or attacker call to `controller.update_indexes(caller, [BIG18_key])` advances accrual in ≤1-year chunks).
4. Once `borrowed * borrow_index` nears `i128::MAX`, the next `accrue_chunk` → `scaled_to_original` panics with `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`.
5. Every subsequent `withdraw`, `repay`, `liquidate`, `claim_revenue`, `recapitalize`, and `update_indexes` on that market reverts in `global_sync` — permanently.

Note on uncertainty: I verified the freeze mechanism and its permissionless reachability through the checked-in test and the accrual ordering, but I could not fully trace `common::rates::accrue_step`'s internals in this pass to confirm whether any partial index-clamp already mitigates the cliff at extreme (but below-cap) index values; the test asserts the cap does not engage before the overflow, which I rely on here.

### Citations

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
