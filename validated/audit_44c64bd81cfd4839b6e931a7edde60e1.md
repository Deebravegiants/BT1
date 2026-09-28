### Title
Permanent market freeze from unchecked RAY value overflow during interest accrual - (`common/src/rates/scaling.rs`)

### Summary
`update_indexes` can permanently freeze a heavily borrowed market once the product of stored scaled debt and the growing borrow index exceeds the `i128` range. The failure occurs inside `scaled_to_original` before `update_borrow_index` can apply `MAX_BORROW_INDEX_RAY`, so the index cap does not prevent the overflow. Because every pool mutation syncs interest before acting, later repayments, withdrawals, liquidations, bad-debt cleanup, and recapitalization fail with `MathOverflow`.

### Finding Description
The attacker first uses `supply` to place a very large amount of a high-decimal asset into a listed market, then uses `borrow` to maintain high utilization with sufficient collateral. The pool represents supply and debt as RAY-scaled shares, while asset values are recovered by multiplying those shares by their market index in `scaled_to_original`. [1](#0-0) 

Each accrual step calls `scaled_to_original` for both total debt and total supply before calculating utilization, the borrow rate, and the next index. [2](#0-1)  Although `update_borrow_index` clamps a successfully calculated index to `MAX_BORROW_INDEX_RAY`, that clamp runs only after the preceding total-value multiplication has already succeeded. [3](#0-2) 

The intended cap is `1e36` raw RAY, but the underlying `i128` value ceiling is only about 170 times a `1e36` scaled position at index `RAY`; therefore, sufficiently large scaled debt can overflow the debt-value multiplication before the index reaches its configured ceiling. [4](#0-3)  The checked multiplication then panics with `MathOverflow`, making every subsequent accrual attempt fail at the same point.

`update_indexes` reaches this path directly because `accrue` loads each selected market and invokes `global_sync`. [5](#0-4)  More importantly, all ordinary market operations load an interest-synced cache through `synced_market`, which unconditionally calls `global_sync` before applying the operation. [6](#0-5)  Consequently, the overflow becomes a persistent state-level failure rather than a rejection caused by one malformed transaction.

### Impact Explanation
This permanently freezes all funds and obligations in the affected `(hub_id, asset)` market under the deployed implementation. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, keepers cannot accrue or clean up the market, and recapitalization cannot restore the path because all these operations first perform accrual.

The repository’s own long-horizon test demonstrates this exact cliff: once `scaled_to_original` overflows, `update_indexes`, `withdraw`, and `repay` all fail with `MathOverflow`, while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`. [7](#0-6) 

A governance-controlled contract upgrade could potentially recover the market, but no in-scope unprivileged or ordinary administrative market operation can bypass the shared accrual prelude. The frozen state therefore persists absent a code upgrade.

### Likelihood Explanation
An unprivileged account can create the required state through ordinary `supply` and `borrow` calls, including by supplying the target asset and separate collateral itself. The attacker must maintain sufficiently high utilization until index growth pushes `borrowed_scaled * borrow_index` beyond `i128::MAX`; a billion-unit, 18-decimal market at sustained 98% utilization reaches the cliff in the repository’s harness. [8](#0-7) 

The attack requires substantial capital and a market whose configured caps and utilization policy admit the required exposure, so it is not an immediate low-cost crash. Nevertheless, it requires no privileged key, malformed external service, leaked secret, or dishonest oracle, and the resulting failure is permanent rather than limited to the attacking transaction.

### Recommendation
Bound scaled balances and index products before accrual, or make the accrual path saturate safely when the next unscaled debt value exceeds `i128::MAX`. In particular:

- check `borrowed_scaled * new_borrow_index` and `supplied_scaled * new_supply_index` before calling `scaled_to_original`;
- clamp `borrow_index` to `MAX_BORROW_INDEX_RAY` without requiring the overflowed total-debt multiplication;
- consider saturating utilization and accrued-value calculations at a documented safe bound instead of panicking;
- add a production regression that advances the market past the boundary and verifies that repayments and withdrawals remain executable;
- enforce protocol-level scaled-balance caps below the largest value that can remain representable at `MAX_BORROW_INDEX_RAY`.

### Proof of Concept
The existing regression test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates the exploit path:

1. Create a valid 18-decimal market and a collateral market.
2. As one unprivileged actor, call `supply(caller, account_id, spoke_id, [(target_hub_asset, 1_000_000_000 * 10^18)])` and separately supply enough collateral to authorize the borrow.
3. Call `borrow(caller, account_id, [(target_hub_asset, 980_000_000 * 10^18)], None)` and maintain approximately 98% utilization.
4. Periodically call `update_indexes(caller, [target_hub_asset])`.
5. Once index growth makes `borrowed_scaled * borrow_index` exceed the `i128` value ceiling, `update_indexes` panics with `MathOverflow`.
6. Subsequent `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, or `recapitalize` transactions involving that market all load the same accrual path and fail before their operation-specific logic executes.

The regression explicitly observes that `update_indexes` fails, the borrow index remains below the intended cap, and both withdrawal and repayment remain frozen. [9](#0-8)

### Citations

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/simulate.rs (L51-67)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

```

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** contracts/pool/src/ops/market.rs (L60-72)
```rust
/// Accrues interest for each market in `hub_assets` and emits one state event
/// per market.
///
/// Always commits state so same-ledger simulation records the write footprint
/// needed if time advances before transaction inclusion.
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
```

**File:** contracts/pool/src/ops/mod.rs (L29-39)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}

/// Renews instance TTL, then loads and accrues the market.
pub(crate) fn renewed_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    renew_instance(env);
    synced_market(env, hub_asset)
```

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
