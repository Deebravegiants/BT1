### Title
Unbounded RAY-denominated market totals overflow `i128` and permanently freeze accrual - (File: common/src/rates/scaling.rs)

### Summary
Large scaled supply or debt balances can make `scaled * index` exceed the `i128` accounting domain before the configured index ceiling is reached. Once that happens, permissionless `update_indexes`, repayments, withdrawals, and liquidations all revert during mandatory accrual, permanently freezing the affected market.

### Finding Description
`Controller.update_indexes` reaches `pool::ops::market::accrue`, which loads each market and calls `interest::global_sync` before committing state. [1](#0-0) [2](#0-1) 

`global_sync` runs `accrue_chunk` for every elapsed interval, and `accrue_step` first converts both aggregate scaled debt and scaled supply back to RAY-denominated values. [3](#0-2) [4](#0-3) 

`scaled_to_original` performs `scaled.mul(index)`, and `Ray::mul` evaluates `scaled * index / RAY` as an `i128` result. [5](#0-4) [6](#0-5) 

The borrow-index ceiling only bounds the index itself; it does not guarantee that the index remains representable when multiplied by an already-large scaled balance. [7](#0-6) 

The subsequent reward calculation also multiplies aggregate scaled debt by both the old and newly grown borrow indexes, so interest distribution can hit the same representational ceiling even when the index is still below `MAX_BORROW_INDEX_RAY`. [8](#0-7) 

### Impact Explanation
This is a permanent freezing-of-funds condition for the affected hub/asset market. The in-tree reproduction shows the market entering an `i128` overflow before `MAX_BORROW_INDEX_RAY`, after which repay and withdraw both return `MathOverflow`; because every mutating path accrues first, borrowers cannot close debt, suppliers cannot exit, and liquidators cannot unwind the position. [9](#0-8) [10](#0-9) 

### Likelihood Explanation
The trigger requires an unusually large market and sustained interest accrual: the reproduction uses a billion whole units of an 18-decimal asset and roughly 98% utilization, then advances time until accrual fails. [11](#0-10) 

No privileged runtime action is needed after such a market exists: an unprivileged caller can invoke `update_indexes`, while ordinary `repay`, `withdraw`, or `liquidate` calls hit the same mandatory accrual path. The capital requirement and elapsed-time precondition reduce likelihood, but the failure is deterministic once the market reaches the unsafe index/share product.

### Recommendation
Do not materialize aggregate RAY-denominated debt or supply as an `i128` during accrual. Use widened `I256` totals for utilization, accrued-value, and reward calculations, or compare/index-cap against `i128::MAX / scaled_balance` so accrual clamps at the largest safe index instead of reverting. Market-level share limits should also account for future index growth rather than only initial deposit conversion.

### Proof of Concept
On a listed 18-decimal market with sufficiently high caps and sustained high utilization:

```rust
// One unprivileged account can provide both the debt-asset liquidity
// and separate collateral.
supply(caller, account_id, spoke, vec![
    (big18_hub_asset, 1_000_000_000 * 10^18),
    (collateral_hub_asset, sufficient_collateral),
]);

borrow(
    caller,
    account_id,
    vec![(big18_hub_asset, 980_000_000 * 10^18)],
    None,
);

// Advance ledger time through repeated yearly intervals.
update_indexes(vec![big18_hub_asset]); // eventually reverts MathOverflow

repay(any_caller, borrower_account, vec![(big18_hub_asset, 1)]);
withdraw(owner, supplier_account, vec![(big18_hub_asset, 1)], None);
// Both revert during accrual, leaving funds frozen.
```

The repository’s regression test uses this same structure: one billion 18-decimal units supplied, 98% borrowed, repeated yearly accruals, then `MathOverflow` from `update_indexes`, `withdraw`, and `repay`. [12](#0-11)

### Citations

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

**File:** contracts/pool/src/ops/market.rs (L68-71)
```rust
    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
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

**File:** common/src/rates/simulate.rs (L60-64)
```rust
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/rates/index.rs (L11-18)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
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
