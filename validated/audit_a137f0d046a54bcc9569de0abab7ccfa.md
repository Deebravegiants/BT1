### Title
RAY-value overflow during mandatory accrual permanently freezes an oversized market - (File: `common/src/rates/index.rs`)

### Summary
A sufficiently large market can reach an `i128` fixed-point value overflow before the borrow-index ceiling is reached. Because every pool operation synchronizes interest before applying the requested action, the first overflow permanently blocks repayment, withdrawal, liquidation, bad-debt cleanup, recapitalization, and index updates for that market. An unprivileged account can create the required market state through ordinary `supply`, `borrow`, and `update_indexes` calls when the configured caps and token liquidity permit the required size.

### Finding Description
The controller exposes permissionless or account-owner entrypoints for `supply`, `borrow`, `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, `update_indexes`, and `recapitalize`. [1](#0-0) [2](#0-1) 

Each pool operation loads the market through `synced_market`, which unconditionally calls `interest::global_sync`. [3](#0-2)  `global_sync` applies every elapsed accrual chunk before the operation proceeds. [4](#0-3) 

Accrual calculates total supplied value as `supplied * old_index`, and debt interest as `borrowed * old_borrow_index` and `borrowed * new_borrow_index`. [5](#0-4) [6](#0-5)  These products are RAY-scaled `i128` values. At a sufficiently large scaled balance, the product can exceed `i128::MAX` even though `borrow_index` remains below `MAX_BORROW_INDEX_RAY`; therefore the index cap does not prevent the overflow. [7](#0-6) 

The repository's stress test establishes the concrete cliff: a one-billion-whole-token, 18-decimal market at 98% utilization eventually causes `update_indexes` to return `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`. [8](#0-7)  Afterward, both withdrawal and repayment fail with the same error because they attempt accrual first. [9](#0-8) 

Repay and withdraw specifically call `ops::load_leg`, which performs the same mandatory synchronization before resolving and committing the requested mutation. [10](#0-9) [11](#0-10)  Recapitalization also loads a synced market before calculating the backing shortfall, so the documented recovery path is blocked by the same panic. [12](#0-11) 

### Impact Explanation
This is a permanent market-level denial of service and permanent freezing of user funds. Once the next accrual step requires an overflowing RAY value, no operation can advance the market past `last_timestamp`, while every user-facing exit, repayment, liquidation, cleanup, and recapitalization path attempts that accrual before mutating state. Suppliers cannot withdraw cash, borrowers cannot reduce debt, and liquidators cannot close the underwater position through the affected market. The test explicitly demonstrates `update_indexes`, `withdraw`, and `repay` all failing with `MATH_OVERFLOW`. [13](#0-12) 

### Likelihood Explanation
Medium. The attack does not require privileged access, oracle dishonesty, reentry, or malformed token behavior: one account can supply the target asset, post collateral, borrow at high utilization, and later call `update_indexes`. [14](#0-13) [15](#0-14) 

The practical requirements are substantial. The market must admit a book approaching the RAY value ceiling, the attacker or another borrower must sustain high utilization, and enough ledger time must pass for the index to grow into the overflow region. The reproduced configuration uses one billion 18-decimal tokens and 98% utilization. [16](#0-15)  Thus the issue is economically constrained, but it is reachable through normal protocol actions on a market with sufficiently permissive caps.

### Recommendation
Make accrual saturate before the total RAY value can overflow, rather than allowing the multiplication to panic. In particular:

- bound `supplied * supply_index` and `borrowed * borrow_index` before updating indexes;
- stop index growth at the largest index whose total market value still fits the fixed-point domain;
- keep repayment, withdrawal, liquidation, cleanup, and recapitalization callable after saturation;
- add a market-level regression test showing those paths remain executable at the value ceiling.

A safer design can also split accrual bookkeeping so total-value saturation prevents further interest accounting without blocking debt reduction or exits.

### Proof of Concept
The repository already contains a deterministic reproduction:

1. Create an 18-decimal market using the steep XLM interest-rate curve and a collateral market.
2. Raise the harness caps to the admitted maximum.
3. Supply `1_000_000_000 * 10^18` units of the target asset.
4. Supply sufficient collateral and borrow 98% of the target market.
5. Advance ledger time and invoke `update_indexes` until accrual fails.
6. Observe `MATH_OVERFLOW` while `borrow_index` remains below `MAX_BORROW_INDEX_RAY`.
7. Attempt `withdraw` and `repay`; both fail with `MATH_OVERFLOW` because each path accrues first.

The exact setup and assertions are implemented in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [17](#0-16)

### Citations

**File:** contracts/controller/src/lib.rs (L90-127)
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
```

**File:** contracts/controller/src/lib.rs (L130-164)
```rust
    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }

    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
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

**File:** contracts/pool/src/ops/mod.rs (L29-34)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L29-41)
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
```

**File:** common/src/rates/index.rs (L73-86)
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

**File:** contracts/pool/src/ops/repay.rs (L40-59)
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

    cache.credit_cash(net_repay);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-81)
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

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/recapitalize.rs (L44-58)
```rust
pub(crate) fn accounting(
    env: &Env,
    hub_asset: HubAssetKey,
    amount: i128,
) -> RecapitalizationOutcome {
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
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
