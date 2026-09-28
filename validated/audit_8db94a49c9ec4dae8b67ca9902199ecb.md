### Title
Market accrual arithmetic overflow permanently freezes repayment, withdrawal, and liquidation - ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary
The market interest path calculates total debt by multiplying total scaled debt by the borrow index before enforcing the borrow-index ceiling. If a sufficiently large market remains highly utilized long enough for the product to exceed the `i128`/RAY arithmetic domain, `accrue_step` reverts before the index cap can clamp growth. Because every state-changing pool operation synchronizes interest first, the affected market then permanently rejects `withdraw`, `repay`, `borrow`, liquidation settlement, and `update_indexes`, freezing supplier and borrower funds.

### Finding Description
`Controller::update_indexes(caller, assets)` is permissionless after caller authorization and forwards the selected hub assets to the pool. [1](#0-0)  On the pool side, `global_sync` accrues every elapsed chunk through `accrue_step` and only marks the market accrued after all chunks succeed. [2](#0-1)  Debt valuation then multiplies `borrowed * borrow_index` for both the old and new index; an unrepresentable product panics rather than clamping or preserving a recoverable partial state. [3](#0-2) 

The codebase documents that valid market caps and the index ceiling do not guarantee future accrued values remain representable. [4](#0-3)  The regression test reaches this condition through ordinary `supply` and `borrow` state, advances time until `update_indexes` returns `MathOverflow`, and confirms that withdrawal and repayment fail through the same accrual precondition. [5](#0-4) 

### Impact Explanation
This is permanent freezing of user funds and a protocol availability failure for the affected market. Once `borrowed * borrow_index` crosses the representable bound, no operation can reduce the debt because repayment itself must first accrue, and suppliers cannot exit because withdrawal accrues first. Liquidation also cannot settle the debt because liquidation repayment and collateral seizure use the same pool mutation path. The failed accrual does not advance `last_timestamp`, so waiting cannot push the index to its ceiling or make a later call succeed; recovery would require a code fix or privileged intervention rather than an ordinary protocol operation.

### Likelihood Explanation
Likelihood is medium-low but the impact is high. A single unprivileged actor can trigger it only where governance-configured caps, token supply, and available collateral admit the required market scale, and where high utilization persists until the scaled debt value approaches `i128::MAX`. No privileged call is needed once such a market exists: the actor can fund supply and borrow positions through `supply` and `borrow`, then call `update_indexes(caller, [hub_asset])` after enough elapsed time. The in-repository test demonstrates the cliff below the borrow-index cap, although it uses a deliberately large fixture rather than proving that a specific deployed market currently admits that scale. [6](#0-5) 

### Recommendation
Bound total market scaled debt and supply shares so that the largest admissible value times `MAX_BORROW_INDEX_RAY` and `MAX_SUPPLY_INDEX_RAY` cannot overflow, rather than relying on token-unit caps alone. Additionally, make accrual saturate safely at the index ceiling before evaluating debt totals when the projected index reaches the cap, and add a checked emergency path that can reduce debt or supply without requiring the failing accrual step. Tests should cover `update_indexes`, `repay`, `withdraw`, and liquidation at the first market size/index pair that reaches the RAY-value boundary.

### Proof of Concept
Assuming an existing listed market whose caps admit the tested scale, an unprivileged caller can execute the ordinary production sequence:

```rust
// Account A: creates the target market's large supplier book.
controller.supply(
    attacker,
    0,                         // create a Normal account
    spoke_id,
    vec![(market, principal)], // e.g. 1 billion 18-decimal tokens
);

// Account B: supplies collateral in another market, then draws almost all
// target-market liquidity.
controller.supply(attacker, 0, spoke_id, vec![(collateral_market, collateral)]);
controller.borrow(attacker, account_b, vec![(market, debt)], None);
```

After sustained high utilization, any caller can force the terminal state through the permissionless keeper entrypoint:

```rust
controller.update_indexes(
    attacker,
    vec![market],
);
```

The call reverts with `MathOverflow` before the index ceiling engages. Subsequent `withdraw`, `repay`, `borrow`, `liquidate`, or further `update_indexes` calls touching that market repeat the same accrual and revert before reducing the unsafe debt value. [7](#0-6)

### Citations

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

**File:** common/src/rates/index.rs (L73-84)
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

```

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
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
