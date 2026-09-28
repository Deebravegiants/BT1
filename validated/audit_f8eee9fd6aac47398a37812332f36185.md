### Title
Interest-accrual `i128` overflow permanently freezes an oversized high-utilization market - (File: common/src/rates/index.rs)

### Summary

A sufficiently large market can drive the RAY-valued debt or supply calculation past `i128::MAX` before `MAX_BORROW_INDEX_RAY` is reached, causing every subsequent pool operation on that market to panic during mandatory interest synchronization. [1](#0-0) [2](#0-1) 

### Finding Description

`Controller::update_indexes` is permissionless and forwards the selected markets to the pool, where `ops::market::accrue` calls `interest::global_sync` for each one. [3](#0-2) [4](#0-3)  During each accrual chunk, `calculate_supplier_rewards` computes `borrowed * old_borrow_index` and `borrowed * new_borrow_index`, while `update_supply_index` computes `supplied * old_index`; each product is represented as a RAY value that must fit in `i128`. [5](#0-4) [1](#0-0) 

The borrow-index ceiling does not prevent this condition because the scaled debt value can exceed the `i128` domain before `new_borrow_index` reaches `MAX_BORROW_INDEX_RAY`; once the multiplication panics, no state is committed and `last_timestamp` remains behind ledger time. [6](#0-5) [7](#0-6)  Supply, repay, withdraw, liquidation settlement, revenue claims, recapitalization, and explicit index updates all load the market through the same accrue-first path, so the panic is repeated rather than bypassed. [2](#0-1) [8](#0-7) [9](#0-8) 

### Impact Explanation

This permanently freezes all supplier cash remaining in the affected market, prevents borrowers and third parties from repaying, and prevents liquidators or bad-debt cleanup from touching that debt market. [2](#0-1) [4](#0-3)  Accounts whose collateral is encumbered by debt in the frozen market can also lose the ability to withdraw otherwise unaffected collateral because the debt cannot be repaid, liquidated, or socially resolved. [10](#0-9) [11](#0-10) 

### Likelihood Explanation

Severity: Medium. An unprivileged attacker can create the state using ordinary `supply`, collateral `supply`, and `borrow` calls, but the market must approach the protocol’s RAY numeric domain and maintain high utilization long enough for an accrual step to produce an unrepresentable debt or supply value. [12](#0-11) [13](#0-12)  The repository’s deterministic regression test demonstrates that a one-billion-whole-token 18-decimal market at 98% utilization reaches `MathOverflow` before the index cap and that subsequent withdrawal and repayment fail. [14](#0-13) 

### Recommendation

Bound market state by the maximum RAY-valued amount, not merely by token-unit caps and index ceilings, so `borrowed * MAX_BORROW_INDEX_RAY / RAY` and `supplied * MAX_SUPPLY_INDEX_RAY / RAY` remain representable. [5](#0-4) [1](#0-0)  Alternatively, make accrual clamp index growth before evaluating debt and supply values that cannot fit `i128`, while ensuring that exits, third-party repayment, liquidation, and bad-debt cleanup retain a path that does not require evaluating the overflowing market-wide value. [15](#0-14) [2](#0-1) 

### Proof of Concept

The existing regression test constructs an 18-decimal market, supplies `BILLION * 10^18` base units, borrows 98% of it, advances ledger time in chunks, and observes `try_update_indexes_for(["BIG18"])` fail with `MathOverflow`; subsequent `withdraw` and `repay` calls fail with the same error before the borrow-index cap is reached. [14](#0-13) 

```rust
// Simplified call sequence for an admitted 18-decimal market.
let debt_asset = HubAssetKey { hub_id, asset: big18 };
let principal = 1_000_000_000i128 * 10i128.pow(18);
let debt = principal * 98 / 100;

// Attacker funds the market.
controller.supply(
    attacker,
    0,                         // create account
    spoke_id,
    vec![&env, (debt_asset.clone(), principal)],
);

// Separately collateralized account keeps utilization near 98%.
controller.borrow(
    attacker,
    borrower_account_id,
    vec![&env, (debt_asset.clone(), debt)],
    None,
);

// Repeat once per accrual window until the RAY-valued debt or supply
// calculation no longer fits i128.
controller.update_indexes(attacker, vec![&env, debt_asset.clone()]);

// These subsequently panic during mandatory accrual:
controller.repay(anyone, borrower_account_id, vec![&env, (debt_asset.clone(), 1)]);
controller.withdraw(supplier, supplier_account_id, vec![&env, (debt_asset, 1)], None);
```

### Citations

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L29-44)
```rust
pub fn update_supply_index(env: &Env, supplied: Ray, old_index: Ray, rewards_increase: Ray) -> Ray {
    if supplied == Ray::ZERO || rewards_increase == Ray::ZERO {
        return old_index;
    }

    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
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

**File:** contracts/controller/src/lib.rs (L120-133)
```rust
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

**File:** contracts/controller/src/lib.rs (L144-164)
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
    }

    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
```

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/pool/src/ops/market.rs (L65-71)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
```

**File:** contracts/pool/src/cache/mod.rs (L133-146)
```rust
    /// Milliseconds between last accrual and the stamped current time.
    pub(crate) fn elapsed_ms(&self) -> u64 {
        self.current_timestamp.saturating_sub(self.last_timestamp)
    }

    /// `true` when interest should be compounded before further mutations.
    pub(crate) fn needs_accrual(&self) -> bool {
        self.elapsed_ms() > 0
    }

    /// Marks the market as fully accrued through `current_timestamp`.
    pub(crate) fn mark_accrued(&mut self) {
        self.last_timestamp = self.current_timestamp;
    }
```

**File:** contracts/pool/src/ops/repay.rs (L40-47)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-65)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
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
