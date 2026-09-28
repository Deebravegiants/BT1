### Title
Attacker-seeded whale market at sustained steep-curve utilization overflows the RAY-scaled debt value in `scaled_to_original`, permanently freezing all verbs on that market - (File: common/src/math/fp.rs)

### Summary
CVE-2017-12445 is a crafted-input crash/DoS (invalid memory read). The analog in XOXNO Lending is an unhandled `i128` overflow panic inside the permissionless accrual path: a caller-supplied market shape (supply size, borrow utilization, asset decimals) drives the RAY-scaled debt value past `i128::MAX` before the borrow-index cap can engage, and every subsequent verb on that market panics with `MathOverflow`.

### Finding Description
The pool tracks debt as `scaled_amount × borrow_index` in RAY fixed point (`common/src/math/fp.rs`, `scaled_to_original`), and accrual in `contracts/pool/src/interest.rs` (`accrue_step` / `global_sync`) recomputes that product on every market touch. The product of a large scaled amount and a grown borrow index is `i128`-bounded; the code uses checked math that panics with `GenericError::MathOverflow` instead of clamping.

An unprivileged user creates the precondition using only `controller::supply` and `controller::borrow`:

1. Pick a high-decimals listed asset whose interest-rate curve has a steep high-utilization segment (the harness reproduces it with an 18-decimal asset on `xlm_curve()`).
2. `supply` a whale-sized amount (`BILLION × 10^decimals`) and `borrow` ~98% of it, keeping utilization pinned on the steep segment.
3. Wait while accrual compounds the borrow index at the steep rate (the test bound is under ~40 years; the index cap `MAX_BORROW_INDEX_RAY` never engages first).

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` proves the full chain: `update_indexes` starts returning `MATH_OVERFLOW`, and because every verb accrues first, `withdraw` and `repay` on that market also revert with `MATH_OVERFLOW`, with `last.borrow_index < MAX_BORROW_INDEX_RAY` confirming the cap did not engage [1](#0-0) . Liquidations on debt in that market fail identically, so the panic is permanent — there is no recovery path that skips accrual [2](#0-1) .

### Impact Explanation
Permanent freezing of funds and effective protocol insolvency for that market: suppliers can never withdraw, borrowers can never repay, liquidators can never liquidate, and `clean_bad_debt`/`recapitalize` also accrue first. All tokens physically sitting in the pool book for that (hub, asset) are bricked, and bad debt in the frozen market cannot be written down, so the supply side absorbs an unresolvable shortfall.

### Likelihood Explanation
Medium. It requires a governance-listed high-decimals asset with a steep rate curve, whale-scale capital (or flash-assisted cycling), and sustained ~98% utilization over many years. No privileged action is needed, and the protocol's own test demonstrates the cliff is reachable and that the documented bound in `docs/reference/formulas.md` understates it. Any keeper calling the permissionless `update_indexes` triggers the panic once the state is primed, and from that point the freeze is irreversible.

### Recommendation
Saturate rather than panic: clamp the RAY-scaled value (or the borrow index growth per accrual step) at the `i128`/value ceiling inside `scaled_to_original`/`accrue_step`, or engage `MAX_BORROW_INDEX_RAY` strictly before the value product can overflow. Add a regression bound check in `docs/reference/formulas.md` so the index-cap engages at least one accrual step below the `i128` cliff for the maximum supported supply × decimals combination.

### Proof of Concept
The repository already contains a working end-to-end PoC: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`. It builds a market with an 18-decimal asset on the XLM curve, supplies `BILLION × 10^18`, borrows 98%, advances time in yearly steps until `try_update_indexes_for(&["BIG18"])` fails with `MATH_OVERFLOW`, then asserts `try_withdraw_raw` and `try_repay` also revert with `MATH_OVERFLOW` — demonstrating the permanent freeze reached purely through unprivileged `supply`/`borrow`/time.

### Citations

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

**File:** contracts/controller/src/context.rs (L111-134)
```rust
    pub(crate) fn fetch_market_indexes(&mut self, hub_assets: &Vec<HubAssetKey>) {
        let missing = collect_uncached_keys(&self.env, hub_assets, &self.market_indexes);
        if missing.is_empty() {
            return;
        }
        let pool_addr = self.cached_pool_address();
        let indexes = fetch_pool_bulk_indexes(&self.env, &pool_addr, &missing);
        for (i, hub_asset) in missing.iter().enumerate() {
            self.market_indexes
                .set(hub_asset, indexes.get_unchecked(i as u32));
        }
    }

    /// Returns a cached index or fetches its simulated current value from the pool.
    pub(crate) fn cached_market_index(&mut self, hub_asset: &HubAssetKey) -> MarketIndex {
        if let Some(index) = self.market_indexes.get(hub_asset.clone()) {
            return (&index).into();
        }
        let pool_addr = self.cached_pool_address();
        let request = vec![&self.env, hub_asset.clone()];
        let index = fetch_pool_bulk_indexes(&self.env, &pool_addr, &request).get_unchecked(0);
        self.market_indexes.set(hub_asset.clone(), index.clone());
        (&index).into()
    }
```
