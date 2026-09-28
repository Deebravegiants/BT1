### Title
Interest accrual overflows the RAY value domain and permanently freezes a market - (File: `common/src/rates/simulate.rs`)

### Summary
A sufficiently large market can reach a state where `scaled * index / RAY` exceeds `i128::MAX` before the configured index ceiling is reached. Because every mutation synchronizes interest before changing state, the resulting `MathOverflow` permanently blocks repayment, withdrawal, liquidation, and further index updates.

### Finding Description
`accrue_step` converts total scaled debt and supply into RAY-denominated values before calculating utilization and updating the indexes. [1](#0-0)  Both conversions eventually use exact `x * index / RAY` arithmetic, which returns `MathOverflow` when the result cannot fit in `i128`; the configured `MAX_BORROW_INDEX_RAY` is only applied to the index, not to the resulting total debt or supply value. [2](#0-1)  `update_borrow_index` can therefore produce a representable index while `borrowed * new_borrow_index / RAY` or `supplied * supply_index / RAY` is unrepresentable. [3](#0-2) 

The pool’s shared `load_leg` path calls `synced_market`, and `synced_market` calls `interest::global_sync` before any operation-specific state changes. [4](#0-3)  The explicit `update_indexes` operation follows the same sequence and commits only after accrual succeeds. [5](#0-4)  A failed accrual rolls back `last_timestamp`, so every later transaction starts from the same unsafe interval and hits the same overflow.

### Impact Explanation
Once the market crosses this boundary, users cannot repay debt, withdraw supplied assets, liquidate unsafe accounts, claim revenue, or recapitalize through paths that first synchronize the market. The attacker can already have withdrawn the borrowed assets, while supplier principal and yield remain trapped in the pool; absent an upgrade or a non-accrueing rescue path, this is a permanent freeze of user funds. The repository’s own long-horizon test demonstrates that `withdraw`, `repay`, and `update_indexes` all fail with `MATH_OVERFLOW` while the stored borrow index remains below its configured cap. [6](#0-5) 

### Likelihood Explanation
A single unprivileged address can create both a supply account and a separately collateralized borrower account, supply a large amount of an 18-decimal asset, borrow most of that liquidity, and later call the permissionless `update_indexes(caller, assets)` entrypoint. [7](#0-6)  The same public `supply` and `borrow` entrypoints create and manipulate those positions. [8](#0-7)  The attack does not require oracle manipulation or privileged access, but it does require very large token balances, caps that admit those balances, and sustained high utilization until the index approaches the value-overflow boundary.

### Recommendation
Clamp each new index against the maximum value representable for the market’s current scaled totals before calculating rewards or utilization, for example by deriving a per-market ceiling such as `floor(i128::MAX * RAY / scaled_total)` and applying it in addition to `MAX_BORROW_INDEX_RAY` and `MAX_SUPPLY_INDEX_RAY`. Alternatively, perform utilization, debt valuation, supply valuation, and reward splitting with widened `I256` arithmetic while preserving the existing rounding policy. Add a regression test that attempts `update_indexes`, `repay`, `withdraw`, and `liquidate` at the boundary and verifies that accrual commits instead of trapping.

### Proof of Concept
1. As one unprivileged caller, create a supplier account with `supply(caller, 0, spoke_id, [(BIG18, 1_000_000_000 * 10^18)])`.
2. Create a second account, supply sufficient accepted collateral, and call `borrow(caller, borrower_account, [(BIG18, 980_000_000 * 10^18)], None)`.
3. Leave utilization near 98% while interest compounds; the repository test uses one billion units at 18 decimals and a 98% borrow against it. [9](#0-8) 
4. Once index growth would make `borrowed * borrow_index / RAY` exceed `i128::MAX`, call `update_indexes(caller, [(hub_id, BIG18)])`; `accrue_step` panics before committing a new timestamp. [10](#0-9) 
5. Retry `update_indexes`, `repay`, or `withdraw`; each reloads the unchanged `last_timestamp` and repeats the overflowing calculation, matching the existing test’s observed permanent `MATH_OVERFLOW`. [11](#0-10)

### Citations

**File:** common/src/rates/simulate.rs (L60-69)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);
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

**File:** common/src/rates/index.rs (L80-84)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

```

**File:** contracts/pool/src/ops/mod.rs (L29-46)
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
}

/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```

**File:** contracts/pool/src/ops/market.rs (L65-72)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
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

**File:** contracts/controller/src/lib.rs (L90-115)
```rust
    /// Supplies `assets` as collateral and returns the account id; `account_id = 0`
    /// creates an account in `spoke_id`. Third parties may only top up existing
    /// supply positions; owners and delegates may add assets.
    #[when_not_paused]
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
    }

    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
    }
```

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```
