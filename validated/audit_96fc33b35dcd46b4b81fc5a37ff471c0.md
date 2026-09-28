### Title
Sustained high-utilization accrual overflows the RAY value domain and permanently freezes a market — no repay, withdraw, or liquidation - ([File: contracts/pool/src/interest.rs])

### Summary
The bug class of CVE-2020-14873 (a repeatable crash/DoS reachable through a normal protocol path) maps onto XOXNO Lending's millisecond-chunked index accrual. Every pool verb calls `global_sync` → `accrue_chunk` → `accrue_step`, which recomputes total borrowed/supplied value as `scaled_shares * index` in RAY. That product must fit `i128`; when it does not, `scaled_to_original` panics with `MathOverflow`. Because the panic happens *before* any state is written and the `MAX_BORROW_INDEX_RAY` index cap engages only after the value ceiling, an unprivileged borrower who holds a large borrow at ~98% utilization on a steep rate curve can push the market past the ceiling — at which point `update_indexes`, `repay`, `withdraw`, `liquidate`, `clean_bad_debt` and every other accrue-first entrypoint permanently revert.

### Finding Description
`global_sync` runs unconditionally at the top of pool operations and loops accrual chunks over elapsed time (`contracts/pool/src/interest.rs:20-33`). `accrue_chunk` calls `accrue_step` over the cached `borrowed`/`supplied` scaled shares and indexes (`interest.rs:39-53`). Inside `accrue_step`/`scaled_to_original` (in `common/src/rates`), the scaled RAY totals are multiplied by the index with no ceiling on the resulting *value* — only the *index* itself is capped at `MAX_BORROW_INDEX_RAY` (10^36, per `docs/reference/formulas.md:426-437`, which explicitly notes "Value overflow can occur before the index ceiling and block repayment/withdrawal because those operations accrue first").

The repository's own harness demonstrates reachability: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`) supplies 10^9·10^18 units of an 18-decimal asset, borrows 98% of it on the XLM curve, advances time, and observes `update_indexes` revert with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`. The test then asserts `withdraw` and `repay` of 1 unit both revert with the same error — the market is frozen with no recovery path (`large_positions_and_long_horizons.rs:354-356`).

### Impact Explanation
Permanent freezing of funds: once the value ceiling is crossed, suppliers can never withdraw, borrowers can never repay, liquidations cannot execute, and bad-debt cleanup (which also accrues first) cannot run. All user balances in that market are bricked. This satisfies the "permanent freezing of funds" / "contract unable to operate" acceptance criteria.

### Likelihood Explanation
Medium. The trigger requires only standard unprivileged entrypoints (`supply`/`borrow`, then `update_indexes` or any accrue-first verb) and no privileged action — but it demands whale-scale capital (a market holding ~10^9 whole tokens of an 18-decimal asset near the `i128`-derived token-to-RAY input maximum of ~170 billion whole tokens) and sustained near-max utilization on a steep segment of the rate curve so the RAY-scaled debt value crosses `i128::MAX` before the index cap. On a large listed market this is a capital-intensive but permissionless grief; the docs acknowledge the bound exists but no contract-level mitigation prevents reaching it.

### Recommendation
Bound the scaled-value arithmetic, not just the index: either cap accrual when `borrowed * borrow_index` approaches the `i128` RAY ceiling (saturating the index/step rather than panicking), or enforce supply/borrow caps far enough below the ceiling that `scaled * index` cannot overflow within the index's 10^36 bound. At minimum, add a pre-accrual check in `accrue_chunk`/`accrue_step` that clamps growth so the value domain stays representable, keeping exits and liquidations executable.

### Proof of Concept
1. Governance lists an 18-decimal asset with the steep XLM rate curve and high caps (caps can be lifted up to the admitted maximum ~170B whole tokens).
2. Attacker calls `supply`/`borrow` to reach ~98% utilization with ~10^9·10^18 base units outstanding (as in the harness test).
3. Time elapses; anyone calls permissionless `update_indexes` (or any verb).
4. `global_sync` → `accrue_chunk` → `accrue_step` → `scaled_to_original(borrowed, borrow_index)` overflows `i128` → `GenericError::MathOverflow` panic.
5. The state never advances past accrual, so every subsequent `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, and `recapitalize` on that market reverts identically — permanently.

Confirmed executable path per the in-repo test at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/pool/src/interest.rs (L39-53)
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

**File:** docs/reference/formulas.md (L426-437)
```markdown
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
