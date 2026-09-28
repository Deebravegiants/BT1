### Title
Permanent market freeze via i128 RAY-value overflow in accrual — every pool verb panics before the borrow-index cap engages - (File: contracts/pool/src/interest.rs)

### Summary
CVE-2026-60188 is a difficult-to-trigger availability-only bug (repeatable crash → complete DoS). The XOXNO analog is a permanent, repeatable panic inside the pool's accrual step: once `scaled borrowed × borrow_index` can no longer be represented after division, `scaled_to_original` overflows i128 and `accrue_step` aborts with `MathOverflow`. Because `global_sync` runs at the head of every mutating entrypoint, the market then rejects `supply`, `withdraw`, `repay`, `net_settle`, `seize_positions`, `claim_revenue` — and through the controller's `cached_market_index` reads, every liquidation and `update_indexes` call touching the market — forever. The documented borrow-index ceiling at `MAX_BORROW_INDEX_RAY` (10^36 raw RAY) does not save the market: the value overflow fires before the cap engages.

### Finding Description
`global_sync` chunks elapsed time and calls `accrue_step`, which converts scaled debt to original units to compute utilization and supplier rewards [1](#0-0) . `scaled_to_original` multiplies `scaled_amount * index / RAY`; the result must fit i128. The input-side bound is much looser: token-to-RAY upscaling admits scaled amounts up to roughly `i128::MAX / 10^(27-d)`, i.e. scaled supply/debt can sit near i128::MAX [2](#0-1) . For a scaled debt `S`, accrual panics as soon as `borrow_index / RAY > i128::MAX / S` — with a near-maximal book, an index barely above one RAY already overflows. `update_borrow_index` multiplies before clamping to the ceiling and has headroom there, but the value conversion in utilization/rewards has none [3](#0-2) . The repository's own harness test demonstrates the end state: a whale market at sustained high utilization reaches the RAY-value cliff, `update_indexes` fails with `MATH_OVERFLOW`, and the same panic then blocks `withdraw` and `repay` permanently — "no repay, no withdraw, no liquidation" [4](#0-3) . Since Soroban rolls back a panicking call, no transaction can ever advance `last_timestamp` past the cliff; the freeze is terminal, not transient.

### Impact Explanation
Permanent freezing of funds for every supplier of the affected market, plus protocol insolvency exposure: the borrower cannot repay, suppliers cannot exit, liquidators cannot touch positions collateralized through this market, and `claim_revenue`/`recapitalize` (which also accrue first) cannot rescue it. No privileged action is required to create the condition — `supply` and `borrow` are the only entrypoints needed, and `update_indexes` is permissionless, so any address can push the market over the cliff once the book is large.

### Likelihood Explanation
Difficult, matching the CVSS 4.4 profile (AC:H). The attacker must build a scaled position near the token-to-RAY input maximum (≈170 billion whole tokens at 18 decimals, or proportionally less at fewer decimals since the scaled bound tightens), hold utilization high enough for the borrow index to grow the small multiple needed for `S × index / RAY` to exceed i128::MAX, and let ledger time elapse — the attacker cannot force time, so the trigger is capital-heavy and slow, but it is fully deterministic once the position exists. No oracle manipulation, leaked key, or privileged call is involved.

### Recommendation
Make accrual value conversions saturating or fallible-tolerant rather than panicking: e.g., have `scaled_to_original` (or a dedicated accrual variant used inside `accrue_step`/`utilization`) clamp to `i128::MAX` so utilization saturates at 100%+ and the borrow index proceeds to its `MAX_BORROW_INDEX_RAY` cap instead of reverting; or add an explicit guard in `global_sync`/`accrue_step` that detects the pre-overflow condition and pins the index at the ceiling, allowing repay/withdraw to proceed. A coarse mitigation is capping admitted scaled market size well below `i128::MAX / 10^(27-d)` so that `S × MAX_BORROW_INDEX_RAY / RAY` always fits i128.

### Proof of Concept
Mirrors the existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` [5](#0-4) :

1. Governance lists a high-decimals market (e.g., 18 decimals) with a steep rate curve (XLM-style curve, `max_borrow_rate` up to 2 RAY annual) and caps lifted to the admitted maximum.
2. Attacker (unprivileged) calls `supply` with ~`10^27`-scale scaled units of the asset, then `borrow` ~98% of it from a second collateralized account, driving utilization near max.
3. Time passes at high utilization; the borrow index compounds toward `i128::MAX × RAY / scaled_borrowed`.
4. Any address calls `update_indexes` (or any user calls `withdraw`/`repay`/`liquidate`): `global_sync → accrue_step → scaled_to_original` overflows i128 and the call reverts with `MathOverflow` (error 33) [6](#0-5) .
5. Every subsequent call on the market accrues first and hits the identical panic; the index stays below `MAX_BORROW_INDEX_RAY` (the cap never engages), and all supplier cash in the market is permanently frozen.

### Citations

**File:** contracts/pool/src/interest.rs (L20-53)
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
}
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

**File:** common/tests/rates/index.rs (L497-517)
```rust
fn test_borrow_index_at_the_ceiling_multiplies_without_overflow() {
    let env = Env::default();

    // `update_borrow_index` multiplies before it clamps, so the pre-clamp
    // product at the ceiling times the largest reachable chunk factor is the
    // real overflow site. It must stay inside i128 with room to spare.
    let factor = max_chunk_growth_factor(&env, MAX_BORROW_RATE_RAY);
    let at_ceiling = Ray::from(MAX_BORROW_INDEX_RAY);

    let product = at_ceiling.mul(&env, factor);
    assert!(product.raw() > MAX_BORROW_INDEX_RAY);
    assert!(
        product.raw() < i128::MAX / 20,
        "pre-clamp headroom above the ceiling fell below 20x: {}",
        product.raw()
    );

    assert_eq!(
        update_borrow_index(&env, at_ceiling, factor).raw(),
        MAX_BORROW_INDEX_RAY,
    );
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
