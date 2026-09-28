### Title
Missing representability bound before scaled debt valuation permanently freezes an oversized market - (File: contracts/pool/src/cache/scale.rs)

### Summary
An unprivileged borrower/supplier can create a market state in which the RAY-scaled debt total remains valid, but multiplying it by the borrow index exceeds `i128`. Because every market operation accrues interest before executing the requested action, the resulting `MathOverflow` panic blocks repayment, withdrawal, liquidation, index updates, and recovery for the entire market. [1](#0-0) 

### Finding Description
`Cache::calculate_utilization` converts total scaled debt and supply back to RAY-denominated asset values through `scaled_to_original`, which multiplies `scaled_amount * index / RAY`. [2](#0-1)  There is no check that the scaled total and index product still fits in `i128`; `calculate_supplier_rewards` similarly multiplies the scaled debt by both the old and new borrow indexes. [3](#0-2) 

`update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY`, but that cap only bounds the index value itself and does not guarantee that `borrowed_scaled_ray * borrow_index` remains representable. [4](#0-3)  The repository’s own stress test demonstrates the resulting cliff: a billion-token, 18-decimal market at 98% utilization reaches `MathOverflow` before the borrow-index cap, after which `withdraw` and `repay` fail with the same error. [5](#0-4) 

A single unprivileged address can reach the prerequisite state through `supply`, `borrow`, and later `update_indexes` on a market whose caps admit sufficient size; no privileged call is needed once those market parameters exist. [6](#0-5) 

### Impact Explanation
This permanently freezes all funds tracked by the affected market. Borrowers cannot repay, suppliers cannot withdraw, liquidators cannot clear positions, and ordinary index updates cannot advance the market because each path performs the overflowing valuation before its mutation. [7](#0-6)  The pool’s documented flow performs `global_sync` before every market mutation, so the panic is not limited to one user-facing entrypoint. [8](#0-7)  Since the borrow index is monotone and the panic occurs before a capped state can be committed, ordinary parameter changes or user transactions do not provide an in-contract recovery path. [9](#0-8) 

### Likelihood Explanation
Triggering the condition requires an unusually large market balance and enough time for the index to multiply the scaled debt past `i128::MAX`, so it is not reachable in a small or tightly capped market. [10](#0-9)  However, admitted caps extend to the representable asset ceiling, and the regression test reaches the failure using ordinary protocol operations rather than corrupted storage or privileged mutations. [11](#0-10)  Once reached, the outcome is deterministic and market-wide.

### Recommendation
Before unscaled valuation or rewards calculation, check whether `scaled_amount * index` exceeds the representable range and handle that case deliberately rather than panicking. Options include performing the intermediate valuation in `U256`, saturating accrued value at a protocol-defined ceiling before converting back to `i128`, or forcing the market into an explicit bad-debt/recapitalization state that still permits repayments, liquidations, and withdrawals. If a hard numerical ceiling is intentional, enforce it at entry with supply/borrow caps derived from `MAX_BORROW_INDEX_RAY`, so user-facing operations cannot transition the market into an unrecoverable state.

### Proof of Concept
The existing harness test is a concrete end-to-end reproduction:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs
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

loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() {
        break;
    }
}

assert_contract_error(
    t.try_withdraw_raw(BOB, "BIG18", 1),
    errors::MATH_OVERFLOW,
);
assert_contract_error(
    t.try_repay(ALICE, "BIG18", 1.0),
    errors::MATH_OVERFLOW,
);
```

The test observes the overflow while the stored borrow index is still below `MAX_BORROW_INDEX_RAY`, proving that the index cap does not prevent the unrepresentable debt-value calculation. [12](#0-11)

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-356)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
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

**File:** contracts/pool/src/cache/scale.rs (L19-26)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
```

**File:** common/src/rates/index.rs (L11-19)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
}
```

**File:** common/src/rates/index.rs (L73-88)
```rust
pub fn calculate_supplier_rewards(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    new_borrow_index: Ray,
    old_borrow_index: Ray,
) -> (Ray, Ray) {
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);

    (supplier_rewards, protocol_fee)
```

**File:** contracts/pool/README.md (L161-167)
```markdown
```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
```

**File:** docs/reference/invariants.md (L229-236)
```markdown
### INV-IDX-01 — Borrow index is monotone and bounded

Both indexes start at one RAY. Successful accrual with validated rate parameters
cannot lower the borrow index and caps it at the protocol constant 10^36 raw
RAY. At the ceiling, further accrual produces no borrower interest.

Debt-value overflow can still revert accrual before that ceiling is reached.
Bounded indexes do not guarantee representable position or market values.
```

**File:** common/tests/validation.rs (L346-376)
```rust
/// The cap ceiling and the balance ceiling are the same number: both are the
/// largest amount `Ray::from_asset` can upscale without overflowing `i128`.
/// See `docs/reference/formulas.md#numeric-limits`
#[test]
fn cap_ceiling_is_exactly_the_largest_representable_balance() {
    let env = Env::default();
    use crate::math::fp::Ray;

    for decimals in crate::constants::MIN_ASSET_DECIMALS..=crate::constants::MAX_ASSET_DECIMALS {
        let ceiling = max_cap_for_decimals(decimals);

        assert_eq!(
            Ray::from_asset(&env, ceiling, decimals).to_asset(&env, decimals),
            ceiling
        );

        let unit_in_ray = 10i128.pow(RAY_DECIMALS - decimals);
        assert!(
            ceiling.checked_mul(unit_in_ray).is_some(),
            "ceiling must not overflow at {decimals} decimals",
        );
        assert!(
            (ceiling + 1).checked_mul(unit_in_ray).is_none(),
            "ceiling is not tight at {decimals} decimals",
        );
    }
}

/// Expressed in whole tokens the ceiling does not depend on decimals at all:
/// i128::MAX / RAY = 170_141_183_460.469…
#[test]
```
