### Title
Unchecked scaled-debt growth permanently freezes a high-utilization market - (File: common/src/rates/simulate.rs)

### Summary
A sufficiently large debt position can make the fixed-point multiplication `borrowed * borrow_index` overflow during interest accrual before the borrow-index ceiling can protect the market. [1](#0-0) [2](#0-1)  Because every market mutation synchronizes interest before accounting, the resulting `MathOverflow` permanently blocks withdrawals, repayments, borrows, liquidations, and index updates for that market. [3](#0-2) 

### Finding Description
`accrue_step` first converts scaled debt and supply back to their original values with `scaled_to_original`, which is a checked `Ray::mul`. [4](#0-3) [5](#0-4)  At very high utilization, repeated compounding raises `borrow_index` until `borrowed * borrow_index` exceeds `i128::MAX`. [6](#0-5) 

The configured `MAX_BORROW_INDEX_RAY` is applied only to the index after `old_index * interest_factor`; it does not bound the much larger debt-value product. [2](#0-1)  `calculate_supplier_rewards` additionally multiplies the same scaled debt by both the old and new indexes, providing another overflow point during the same accrual. [7](#0-6) 

`global_sync` advances `last_timestamp` only after every elapsed-time chunk succeeds, so reverting on an overflowing chunk leaves the market at the same fatal timestamp on the next call. [8](#0-7)  All normal pool legs load through `synced_market` or `load_leg`, so there is no user-facing bypass that skips the failing accrual. [3](#0-2) 

### Impact Explanation
Once the condition is reached, suppliers cannot withdraw and borrowers cannot repay because both controller calls eventually execute pool paths that first call `global_sync`. [9](#0-8) [10](#0-9)  Liquidation is also blocked because its pool repay/withdraw legs use the same synchronized leg loader. [11](#0-10) [12](#0-11) 

This permanently freezes all user funds and unclaimed yield in the affected `(hub_id, asset)` market and prevents debt cleanup even after collateral prices change. [8](#0-7) 

### Likelihood Explanation
A single unprivileged account can set up the condition by supplying collateral in one asset, supplying or using existing liquidity in a high-decimal debt asset, and borrowing nearly all cash through `borrow(caller, account_id, borrows, to)`. [13](#0-12)  The attack needs an unusually large market and sustained high utilization, but the relevant entrypoints are permissionless after normal authentication and do not require privileged state changes. [13](#0-12) 

The bundled regression demonstrates that an 18-decimal market holding `10^27` asset units at 98% utilization reaches `MathOverflow` while the stored borrow index is still below `MAX_BORROW_INDEX_RAY`, after which both withdraw and repay fail. [14](#0-13) 

### Recommendation
Replace the accrual-time `i128` products with `I256` or otherwise explicitly saturate/clamp the scaled-debt value before multiplying by the index. [1](#0-0)  In particular, cap `new_borrow_index` before calculating debt deltas and make `calculate_supplier_rewards` handle index-capped debt without overflowing. [2](#0-1) [7](#0-6)  Add a production regression for an extremely large high-decimal market proving that `update_indexes`, `repay`, `withdraw`, and liquidation remain executable at the index ceiling. [3](#0-2) 

### Proof of Concept
Conceptual transaction sequence for one attacker-controlled account:

```rust
// Existing users have supplied BIG18, an 18-decimal market.
// The attacker supplies enough collateral and additional BIG18 liquidity.
controller.supply(
    attacker,
    0,
    spoke_id,
    vec![
        (HubAssetKey { hub_id, asset: collateral_asset }, collateral_amount),
        (HubAssetKey { hub_id, asset: big18_asset }, big18_liquidity),
    ],
);

// Against the same account, borrow approximately 98% of BIG18 cash.
controller.borrow(
    attacker,
    attacker_account_id,
    vec![(HubAssetKey { hub_id, asset: big18_asset }, debt_amount)],
    Some(attacker),
);

// Leave the position at sustained high utilization while ledger time advances.
// Each permissionless index update compounds the borrow index.
controller.update_indexes(vec![HubAssetKey { hub_id, asset: big18_asset }]);
```

When `borrowed * borrow_index` crosses the `i128` domain, `scaled_to_original` panics in `accrue_step`, and the transaction rolls back before `last_timestamp` is advanced. [1](#0-0) [15](#0-14)  Subsequent `withdraw`, `repay`, liquidation, or index-update attempts repeat the same failing accrual, leaving the market permanently frozen. [3](#0-2)

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

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/controller/src/lib.rs (L117-133)
```rust
    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
```

**File:** contracts/controller/src/lib.rs (L144-157)
```rust
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
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
