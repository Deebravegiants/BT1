### Title
Repeated permissionless accrual overflows `borrowed × borrow_index` in `scaled_to_original`, permanently freezing every market verb before the index cap engages - (File: common/src/rates/index.rs via contracts/pool/src/interest.rs)

### Summary
CVE-2020-13974 is a counter that overflows because a function can be invoked repeatedly with no reset. The analog here is the pool's `borrow_index`/`supplied` accrual: `update_indexes` is permissionless and every market verb accrues first, so repeated compounding pushes `borrow_index` upward monotonically until the unscaling product `borrowed_scaled × borrow_index` overflows `i128` inside `scaled_to_original` — at which point `MathOverflow` panics on every subsequent call and the market is frozen forever.

### Finding Description
`interest::global_sync` runs on every market mutation and chunks elapsed time into `MAX_COMPOUND_DELTA_MS` steps, each step multiplying `borrow_index` by a compounding factor in `accrue_step` [1](#0-0) . `borrow_index` is monotone non-decreasing; its sole writer is `update_borrow_index`, capped only at `10^36` (`MAX_BORROW_INDEX_RAY`) [2](#0-1) . The index cap is therefore the only guard, but the debt-value computation `borrowed × borrow_index / RAY` in `scaled_to_original` overflows `i128` long before the index reaches `10^36` when `borrowed` is large — the product's ceiling is `i128::MAX`, ~170× `10^36` ray-units, so any book with scaled debt above ~1.7e35 ray panics first [3](#0-2) .

The protocol's own harness test proves this: a 1-billion-unit, 18-decimal market at 98% utilization on the XLM curve reaches the overflow cliff within a bounded number of years, `update_indexes` fails with `MATH_OVERFLOW`, and because accrual precedes every verb, `withdraw` and `repay` panic identically — the index cap never engages [4](#0-3) .

Attack path for a single unprivileged address: `supply` a large position into a high-decimals market, `borrow` up to the utilization cap, then drive accrual with the permissionless `update_indexes` entrypoint over time. No admin key, leaked key, or governance action is required; the cadence itself is attacker-controlled since `update_indexes` accepts any caller [5](#0-4) .

### Impact Explanation
Once the product overflows, every state-changing entrypoint on that market (`supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `recapitalize`, `claim_revenue`) reverts at the accrual step, which runs before any mutation in the standard flow [6](#0-5) . Because `borrow_index` only grows, there is no future timestamp at which the panic clears: all supplied and collateral funds in the market are permanently frozen — protocol insolvency-grade impact for that book, satisfying the "permanent freezing of funds" criterion.

### Likelihood Explanation
Requires a very large (whale-scale, or high-decimals) market at sustained high utilization and an extended accrual horizon; the checked-in test bounds the cliff to under ~40 years on the real XLM curve, and shorter at steeper rate regimes or larger books [7](#0-6) . Any single unprivileged caller can trigger it with `update_indexes`; there is no cost beyond ledger fees and no way for anyone to prevent it once the book size and utilization exist. Medium likelihood, High impact → High severity.

### Recommendation
- Enforce the economic bound earlier: reject `supply`/`borrow` that would push `borrowed_scaled` above `i128::MAX / MAX_BORROW_INDEX_RAY`, so the index cap (`10^36`) always engages before the value multiplication can overflow.
- Alternatively, clamp inside `accrue_step`/`update_borrow_index` so that when the computed debt value would exceed `i128::MAX`, the index is pinned at `MAX_BORROW_INDEX_RAY` and accrual halts gracefully (charge no further interest) instead of panicking — a frozen-interest market is recoverable, a panicking one is not.
- In `scaled_to_original` on the accrual path, use a saturating or cap-aware multiplication rather than a raw checked multiply whose panic propagates into every verb.

### Proof of Concept
The repo contains a working PoC: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` seeds a 1e9-unit 18-decimal market, borrows 98%, advances time year-by-year calling the permissionless `try_update_indexes_for`, observes `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, then confirms `withdraw` and `repay` panic with the same error [8](#0-7) .

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

**File:** contracts/pool/README.md (L159-168)
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
```

**File:** contracts/pool/README.md (L180-190)
```markdown
```text
supplied, borrowed, revenue : Ray, scaled shares
borrow_index                : Ray, monotone non-decreasing
supply_index                : Ray, grows on interest, falls on bad debt
cash                        : i128, token-native, bookkeeping
```

`borrow_index` only ever grows — `update_borrow_index` is its sole writer.
`supply_index` is **not** monotone: `apply_bad_debt_to_supply_index` scales it
down to socialize a loss across suppliers, floored at `SUPPLY_INDEX_FLOOR_RAW`
(`RAY/1000`). Anything caching an index must tolerate a decrease.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-320)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
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

**File:** contracts/pool/tests/interest.rs (L852-856)
```rust
// Failure shape: frequent accrual floors the protocol fee to zero before the
// reserve factor applies. `update_indexes` is permissionless, so an attacker
// picks the cadence. These tests run the same elapsed span three ways (one
// accrual at the end, one per ~5s ledger, one per second) and measure where
// the value lands.
```
