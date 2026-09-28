### Title

Interest accrual can permanently freeze an oversized market before its index cap - ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary

An unprivileged caller can trigger `controller.update_indexes(caller, vec![HubAssetKey { hub_id, asset }])` on a market whose stored scaled balances and accumulated index make `scaled * index` exceed the `i128` RAY-value domain. Accrual panics while unscaled totals are calculated, before the index ceiling can clamp further growth, and because every pool mutation synchronizes the market first, subsequent supply, borrow, withdraw, repay, liquidation, flash-loan, recapitalization, and revenue paths for that market revert.

### Finding Description

`LiquidityPool::update_indexes` calls `ops::market::accrue`, which loads each requested market and invokes `interest::global_sync`. [1](#0-0) [2](#0-1)  `global_sync` repeatedly invokes `accrue_chunk` until the market reaches the current timestamp. [3](#0-2)  During accrual, utilization and reward accounting convert scaled balances back to value with non-saturating `Ray::mul`; `calculate_utilization` computes both `borrowed * borrow_index` and `supplied * supply_index`. [4](#0-3) [5](#0-4)  The index ceiling is applied only after `old_index.mul(interest_factor)` and does not prevent an already oversized scaled balance from overflowing when it is unscaled. [6](#0-5)  All pool mutation batches use `synced_market` or `load_leg`, both of which run `global_sync` before processing the requested action. [7](#0-6) 

### Impact Explanation

Once the market crosses this arithmetic boundary, the failed accrual cannot commit a new `last_timestamp`, so every later accrual repeats the same overflowing calculation. Any operation touching that hub asset therefore reverts, permanently freezing supplier funds, preventing borrower repayment and collateral withdrawal, and blocking liquidation and bad-debt cleanup through the ordinary protocol paths. The repository’s regression test demonstrates exactly this state: `update_indexes` returns `MathOverflow`, the stored borrow index remains below `MAX_BORROW_INDEX_RAY`, and subsequent withdraw and repay calls fail with the same error. [8](#0-7) 

### Likelihood Explanation

The caller only needs authorization as an arbitrary address; `controller.update_indexes` is permissionless and passes caller-selected `HubAssetKey` values to the pool. [9](#0-8) [10](#0-9)  Reaching the boundary requires a very large scaled book and sustained interest accrual under the configured rate model, so it is capital- and market-condition-dependent rather than an immediate single-transaction attack. The tested scenario creates a billion-unit 18-decimal market with 98% borrowed, then advances time until the next public accrual fails; the failure occurs before the configured index ceiling. [11](#0-10) 

### Recommendation

Make accrual fail-safe at the value boundary before recomputing utilization or supplier rewards. In particular:

- Detect `borrowed * borrow_index` or `supplied * supply_index` overflow before multiplication.
- Clamp the relevant index or accrued step in a way that preserves a representable total.
- Prefer saturating total-value calculation for accrual decisions while retaining checked arithmetic for actual balance mutations.
- Add a market-level recovery invariant: after an index cap or value-domain boundary is reached, `update_indexes`, `repay`, `withdraw`, and liquidation must still succeed or return a bounded domain-specific state rather than repeatedly panicking.
- Extend the existing whale-market test to prove recovery actions remain possible after the index reaches its configured cap.

### Proof of Concept

1. Configure a listed hub asset whose decimals and supply/borrow caps permit a very large scaled balance.
2. Supply a large amount through `controller.supply` and create a high-utilization borrow through `controller.borrow`.
3. Advance ledger time until `scaled_balance * index` exceeds `i128::MAX`.
4. Call:

```rust
controller.update_indexes(
    attacker,
    vec![&env, HubAssetKey { hub_id, asset }],
);
```

5. `pool.update_indexes` enters `accrue`, `global_sync`, and `accrue_chunk`; the accrual calculation panics with `MathOverflow`.
6. Call `controller.repay`, `controller.withdraw`, or `controller.liquidate` for the same `HubAssetKey`; each reaches `synced_market`/`load_leg`, retries the same failed accrual, and reverts.
7. The included regression test demonstrates the first three externally observable assertions: accrual returns `MathOverflow`, the stored index remains below the cap, and both a withdrawal and a repayment subsequently return `MathOverflow`. [12](#0-11)

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

**File:** contracts/pool/src/interest.rs (L25-32)
```rust
    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```

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
