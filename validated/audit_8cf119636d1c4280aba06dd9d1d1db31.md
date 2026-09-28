### Title
Permanent market freeze: `accrue_step` overflows `i128` in `scaled_to_original` once `borrowed × borrow_index` exceeds the RAY-value ceiling, long before `MAX_BORROW_INDEX_RAY` engages - (File: `common/src/rates/simulate.rs`)

### Summary
Like CVE-2025-32405 (out-of-bounds write → crash), the analog is an unchecked arithmetic bound in the accrual path that turns a reachable state into a permanent panic. Every mutating pool entrypoint runs `interest::global_sync` first, which calls `accrue_step`, whose first line is `scaled_to_original(borrowed, borrow_index)` — a `Ray::mul` → `mul_div_half_up` that panics `MathOverflow` when the half-up product leaves `i128`. Once a market's scaled-debt value crosses that ceiling, the panic is not transient: it re-fires on every subsequent call, permanently freezing the market.

### Finding Description
`accrue_step` computes `borrowed_original = scaled_to_original(env, borrowed, borrow_index)` — i.e. `half_up(borrowed_raw * borrow_index_raw / RAY)` — and `scaled_to_original` delegates to `Ray::mul`, which panics via `mul_div_half_up` on overflow ( [1](#0-0) , [2](#0-1) ). The pool's mutating `global_sync` runs this on every entrypoint before any state change ( [3](#0-2) , [4](#0-3) ).

The index-side protection exists — `update_borrow_index` clamps at `MAX_BORROW_INDEX_RAY` ( [5](#0-4) ) — but it clamps the *index*, not the *product*. For a book whose scaled debt is large enough, `borrowed * borrow_index / RAY` exceeds `i128::MAX` while `borrow_index` is still far below the cap. The protocol's own test demonstrates exactly this: on a billion-token 18-decimal market at ~98% utilization, `update_indexes`, `withdraw`, and `repay` all revert with `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY` — "the market is frozen: no repay, no withdraw, no liquidation" ( [6](#0-5) ). The state is unrecoverable: accrual is the first step of `supply`/`borrow`/`withdraw`/`repay`/`net_settle`/`seize_positions`/`recapitalize`/`claim_revenue`, so no verb can roll the book back under the cliff; even `recapitalize` accrues first.

Attacker path (unprivileged): on a sufficiently large pool market, an attacker supplies collateral via `controller.supply`, borrows up to the utilization ceiling via `controller.borrow`, and holds utilization in the steep segment of the rate curve. `simulate_update_indexes_body` chunks arbitrary elapsed time into ≤1-year accrual steps ( [7](#0-6) ), so ordinary ledger progression compounds the index until the next `update_indexes`/mutation panics and the market is frozen for good.

### Impact Explanation
Permanent freezing of funds and permanent loss of a market. Every supplier's deposit, every borrower's collateral routed through the same pool balance, and the market's accrued revenue are unreachable: withdraw, repay, liquidate (`seize_positions`), `clean_bad_debt`, `recapitalize`, and `claim_revenue` all hit `global_sync` → `accrue_step` → `MathOverflow`. Since the panic lives in a pure function of committed state (`borrowed`, `borrow_index` both monotonically grow until the cliff), no caller-supplied argument can avoid it. This is the smart-contract analogue of the CVE's crash: an attacker-driven input domain (large debt × elapsed compounding) reaches an unchecked arithmetic bound and permanently disables the device/market.

### Likelihood Explanation
Medium-Low. Preconditions: (a) a market whose scaled debt is large enough that `borrowed * index / RAY > i128::MAX` before the index hits `MAX_BORROW_INDEX_RAY` — feasible for high-decimal assets at whale scale (the repo's own test reaches it), but possibly blocked by configured supply/borrow caps (`require_cap_within_asset_domain`), which is market-config dependent and was not fully verified; (b) sustained high utilization, which a single well-capitalized attacker can enforce by borrowing the pool up, at the cost of interest on their own debt; (c) real wall-clock time for the index to grow — years at moderate rates, faster on steep curves. No privileged access, no oracle manipulation, and no third-party cooperation is needed; the cost is the attacker's own interest payments, which are moot once repayment is impossible anyway (a griefing/self-lock tradeoff).

### Recommendation
Make the accrual overflow non-fatal. Options:
- Compute `borrowed_original`/`supplied_original` with `I256` widening (as other paths already do) or a saturating variant, and treat the saturation as "index/value at ceiling" — clamp `borrow_index` to `MAX_BORROW_INDEX_RAY` once the value product would overflow, so accrual halts gracefully instead of panicking.
- Alternatively, bound `borrowed` (scaled) at market creation and in `borrow` so that `max_scaled_debt * MAX_BORROW_INDEX_RAY` provably fits `i128` — i.e. enforce a per-decimals cap at the same place `require_cap_within_asset_domain` validates caps, closing the gap the test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` exposes.

### Proof of Concept
The repo ships a working reproduction: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` ( [8](#0-7) ). Outline:

```rust
// 18-decimal market, steep rate curve (max_borrow_rate = 175% APR)
t.supply_raw(BOB, "BIG18", 1_000_000_000 * 10i128.pow(18));   // whale supply
t.supply_raw(ALICE, "COL", collateral);                        // attacker collateral
t.borrow_raw(ALICE, "BIG18", principal * 98 / 100);            // ~98% utilization
// advance ledger time; each update_indexes re-accrues
loop { t.advance_time(YEAR_SECS); t.try_update_indexes_for(&["BIG18"])?; }
// eventually: Err(MathOverflow) — borrowed * borrow_index / RAY > i128::MAX
// and every subsequent call fails identically:
try_withdraw_raw(BOB, "BIG18", 1)   // Err(MathOverflow)
try_repay(ALICE, "BIG18", 1.0)      // Err(MathOverflow)
// borrow_index still < MAX_BORROW_INDEX_RAY — the cap never protected the product
```

The panic site is `scaled_to_original(env, borrowed, borrow_index)` on the first line of `accrue_step` ( [9](#0-8) ), reached unconditionally by `global_sync` ( [3](#0-2) ) at the top of every mutating market call.

### Citations

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp.rs (L50-52)
```rust
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
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

**File:** common/src/rates/simulate.rs (L60-66)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);
```

**File:** common/src/rates/simulate.rs (L157-175)
```rust
    let mut remaining = total_delta_ms;
    while remaining > 0 {
        let chunk = remaining.min(MAX_COMPOUND_DELTA_MS);
        let step = accrue_step(
            env,
            &params,
            state.borrowed,
            supplied,
            borrow_index,
            supply_index,
            chunk,
        );

        borrow_index = step.borrow_index;
        supply_index = step.supply_index;
        supplied = supplied.checked_add(env, step.revenue_shares);

        remaining -= chunk;
    }
```

**File:** common/src/rates/index.rs (L13-19)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
}
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-360)
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
    std::println!(
        "ray-value cliff reached after {years} years at 98 percent utilization on the XLM curve; last index x{:.1}",
        last.borrow_index as f64 / RAY as f64
    );
```
