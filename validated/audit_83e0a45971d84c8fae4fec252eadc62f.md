### Title
RAY-value overflow permanently freezes a large accrued market - ([File: common/src/rates/scaling.rs](common/src/rates/scaling.rs))

### Summary
An attacker who can legitimately create a sufficiently large, highly utilized market position can eventually push the market into a state where every operation that accrues interest reverts with `MathOverflow`. The borrow index remains below `MAX_BORROW_INDEX_RAY`, but converting the scaled debt into its RAY-denominated value exceeds `i128`, causing accrual to panic before repayment, withdrawal, liquidation, bad-debt cleanup, or revenue processing can run.

### Finding Description
`scaled_to_original` computes `scaled.mul(index)`, where `Ray::mul` returns `MathOverflow` when the result cannot fit in `i128`. [1](#0-0)  The underlying multiplication path widens only the intermediate product to `I256`; conversion back to `i128` still fails when the final value exceeds `i128::MAX`. [2](#0-1) 

Every pool mutation first loads the market through `ops::load_leg`, which performs accrual. `global_sync` then evaluates `accrue_step` against the market's scaled borrow and supply totals and indexes. [3](#0-2)  Repayment reaches this path through `ops::repay::accounting`, before any debt can be burned. [4](#0-3)  Withdrawal reaches it through `ops::withdraw::accounting`, before supply can be burned. [5](#0-4) 

The in-repository regression test demonstrates the reachable end state with a one-billion-whole-token, 18-decimal market at 98% utilization: the index remains below `MAX_BORROW_INDEX_RAY`, but the next accrual fails with `MathOverflow`, after which both withdrawal and repayment fail with the same error. [6](#0-5) 

### Impact Explanation
This permanently freezes the affected market rather than merely rejecting one oversized transaction. Once the scaled-debt value crosses the `i128` domain boundary:

- suppliers cannot withdraw;
- borrowers cannot repay;
- liquidators cannot liquidate;
- `clean_bad_debt` cannot socialize the position;
- `update_indexes` cannot advance the market;
- revenue claims and other market mutations that load and accrue the market fail.

The pool retains the corresponding user funds, but no ordinary exit path can reduce either the scaled balances or the index far enough to restore arithmetic. This is permanent freezing of user funds and potentially protocol insolvency for the affected market.

### Likelihood Explanation
The attack requires a very large market: the demonstrated fixture uses one billion whole tokens at 18 decimals and 98% utilization. It also requires enough collateral to support the borrow and a market configuration whose supply and borrow caps admit the required exposure. Those are significant capital and configuration prerequisites, but no privileged call is needed after such a market exists: an attacker can use `controller::supply` for both the debt-market liquidity and collateral, `controller::borrow` to reach high utilization, and permissionless `controller::update_indexes` to advance accrual until the overflow boundary is crossed.

The issue is therefore not an instantly triggerable overflow on arbitrary markets, but it is a reachable protocol-state cliff under admitted `i128` bounds and does not depend on compromised keys, upgrades, oracle manipulation, or external-contract dishonesty.

### Recommendation
Make accrued RAY-value calculations saturating or explicitly cap indexes by each market's remaining value headroom.

In particular:

- During accrual, calculate `borrowed * new_borrow_index` and `supplied * new_supply_index` with a non-panicking primitive.
- If either result exceeds the representable RAY domain, clamp the affected index to the largest value that keeps the market value representable, rather than allowing accrual to panic.
- Emit an explicit index-ceiling event so keepers and governance can detect that the market reached the arithmetic limit.
- Add production tests proving `update_indexes`, `repay`, `withdraw`, `liquidate`, and `clean_bad_debt` remain executable at the dynamic cap.

A simple global index cap is insufficient because the safe index depends on the market's scaled balances.

### Proof of Concept
The repository's harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` is already the direct reproduction:

1. Create an 18-decimal market using the steep XLM interest-rate curve.
2. Supply `1_000_000_000 * 10^18` units of the debt asset.
3. Supply sufficient collateral in a separate market.
4. Borrow 98% of the debt-market liquidity.
5. Repeatedly call permissionless `update_indexes` as ledger time advances.
6. Before `borrow_index` reaches `MAX_BORROW_INDEX_RAY`, accrual panics with `MathOverflow`.
7. Subsequent `withdraw` and `repay` calls also revert with `MathOverflow`, because both load and accrue the market before changing positions.

Relevant implementation:

- `scaled_to_original`: `common/src/rates/scaling.rs:14-16`
- accrual loop: `contracts/pool/src/interest.rs:20-32`
- repayment accrual entry: `contracts/pool/src/ops/repay.rs:40-44`
- withdrawal accrual entry: `contracts/pool/src/ops/withdraw.rs:57-65`

### Citations

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

**File:** contracts/pool/src/interest.rs (L20-48)
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
```

**File:** contracts/pool/src/ops/repay.rs (L40-55)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-80)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

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
