### Title

Bad-debt write-down floor resurrects supplier claims and lets them drain recapitalization funds - (File: contracts/pool/src/interest.rs)

### Summary

`apply_bad_debt_to_supply_index` correctly caps a bad-debt write-down at the market’s total supplied value, but then raises a fully wiped `supply_index` back to `SUPPLY_INDEX_FLOOR_RAW` instead of leaving it at zero. [1](#0-0)  This is analogous to mapping more resources than were requested: a loss equal to or greater than the entire supply book should consume every supply claim, yet the floor leaves every scaled share with 0.1% of its former face value. [2](#0-1) 

### Finding Description

`Controller::clean_bad_debt` is permissionless for an insolvent account whose remaining collateral is at or below the dust threshold. [3](#0-2)  Cleanup sends each of the account’s borrow positions to the pool as `PoolSeizeEntry { side: Borrow, position }`. [4](#0-3)  The pool converts that position to a ceiling-valued `bad_debt`, calls `apply_bad_debt_to_supply_index`, and burns the debt shares. [5](#0-4) 

When `bad_debt >= supplied * supply_index`, `remaining` is zero and `new_supply_index` is zero; however, line 88 then applies `max(SUPPLY_INDEX_FLOOR_RAW)`, raising it to `RAY / 1000`. [1](#0-0)  The function does not burn or adjust `cache.supplied`, so all unrelated supply positions retain their scaled shares and now each has a nonzero token claim created solely by the floor. [6](#0-5) 

Those phantom claims are included directly in `backing_shortfall`, because the function compares floored total supply value with cash plus ceiled outstanding debt. [7](#0-6)  `recapitalize` credits real transferred cash up to that computed shortfall. [8](#0-7)  A normal withdrawal then converts the resurrected scaled position into an asset amount, burns the shares, checks cash, and debits/transfers the payout. [9](#0-8) 

### Impact Explanation

A supplier whose position survived a complete bad-debt wipeout receives a claim on assets that should have been fully socialized away. [1](#0-0)  Once any payer recapitalizes the resulting manufactured shortfall, or another borrower repays cash into the affected market, the holder can withdraw real tokens against the phantom residual index. [10](#0-9) [11](#0-10) 

This is theft of recapitalizer or repayer funds rather than merely a temporary freeze: the pool accepts the residual claims as backing liabilities and pays them from newly credited cash. [7](#0-6) [12](#0-11) 

### Likelihood Explanation

The trigger requires a complete or effectively complete bad-debt wipeout in a market, followed by later cash entering that market through recapitalization or debt repayment. [1](#0-0) [10](#0-9)  This is not a privileged or parameter-only path: the attacker can control both the supplier account and the borrowing account, while `clean_bad_debt` is permissionless once the collateral value has fallen to the dust cap. [13](#0-12) [3](#0-2) 

A holder’s claim is proportional to its retained scaled shares, so the attacker need only retain a meaningful fraction of the wiped market to extract a meaningful fraction of later cash injections. [14](#0-13) [15](#0-14) 

### Recommendation

Do not clamp the post-socialization index to `SUPPLY_INDEX_FLOOR_RAW` after computing a zero index from a complete wipeout; the index should remain zero, or the market should transition to an explicit wiped/reset state that burns or invalidates all pre-wipeout scaled supply shares. [1](#0-0) 

If a nonzero floor is required for subsequent arithmetic, it must only apply when the computed index is already nonzero and fell below the floor; it must not resurrect claims when `remaining == 0`. [1](#0-0)  In addition, a wipeout transition should prevent `backing_shortfall` from counting legacy shares as claims until those shares have been explicitly cleared. [7](#0-6) 

### Proof of Concept

Assume a 7-decimal debt asset `D`, `supply_index == borrow_index == RAY`, and no other cash or debt in `D`.

1. Attacker calls `supply(attacker, 0, spoke_id, [(D, 100_000_0000000)])`, creating a supplier account holding all scaled supply shares. [16](#0-15) 
2. Through a second controlled account, the attacker supplies collateral `C` and calls `borrow(attacker, borrower_id, [(D, 100_000_0000000)], Some(attacker))`, draining the `D` cash. [17](#0-16) 
3. `C` falls until the borrower has at most the dust threshold of collateral while still owing `D`; the attacker calls `clean_bad_debt(attacker, borrower_id)`. [3](#0-2) 
4. The pool computes `bad_debt == 100_000_0000000 * RAY` and `total_supplied_value == 100_000_0000000 * RAY`; therefore `remaining == 0`, `new_supply_index == 0`, and the floor sets `supply_index = RAY / 1000`. [1](#0-0) 
5. The attacker’s supplier account still owns all `supplied` scaled shares, whose floored withdrawal value is now `100_00000000` units of `D` even though the market’s cash was fully lost. [18](#0-17) 
6. `backing_shortfall` reports `100_00000000` because it counts that floored supplied claim and there is no remaining cash or debt. [7](#0-6) 
7. Any payer calls `recapitalize(payer, D, 100_00000000)`, causing the pool to credit `100_00000000` of real cash. [8](#0-7) 
8. The attacker calls `withdraw(attacker, supplier_id, [(D, 0)], Some(attacker))`; the zero amount requests a full withdrawal, burns the legacy shares, debits the newly credited cash, and transfers `100_00000000` to the attacker. [19](#0-18) [20](#0-19)

### Citations

**File:** contracts/pool/src/interest.rs (L73-88)
```rust
pub(crate) fn apply_bad_debt_to_supply_index(cache: &mut Cache, bad_debt: Ray) {
    let total_supplied_value = cache.supplied().mul(cache.env(), cache.supply_index());

    if total_supplied_value == Ray::ZERO {
        return;
    }

    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

**File:** contracts/pool/README.md (L187-190)
```markdown
`borrow_index` only ever grows — `update_borrow_index` is its sole writer.
`supply_index` is **not** monotone: `apply_bad_debt_to_supply_index` scales it
down to socialize a loss across suppliers, floored at `SUPPLY_INDEX_FLOOR_RAW`
(`RAY/1000`). Anything caching an index must tolerate a decrease.
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-242)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}

/// Admission condition for bad-debt socialization.
#[derive(Clone, Copy, PartialEq)]
enum BadDebtGate {
    /// Permissionless: insolvent *and* collateral at or below the dust threshold.
    DustCapped,
    /// Owner-only: insolvent alone, with no cap on the collateral left behind.
    InsolventOnly,
}

/// Requires open debt and the selected insolvency gate, then cleans up the account.
fn socialize_bad_debt(env: &Env, account_id: u64, gate: BadDebtGate) {
    let mut cache = Context::new(env);
    let account = storage::get_account(env, account_id);

    assert_with_error!(
        env,
        !account.borrow_positions.is_empty(),
        CollateralError::DebtPositionNotFound
    );

    let totals = risk::calculate_account_risk_totals(
        env,
        &mut cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
}

/// Socializes insolvent debt when remaining collateral is at or below the dust cap.
pub(crate) fn clean_bad_debt_standalone(env: &Env, account_id: u64) {
    socialize_bad_debt(env, account_id, BadDebtGate::DustCapped);
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L35-49)
```rust
    for (hub_asset, position) in iter_debt_positions(&account.borrow_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Borrow,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);
```

**File:** contracts/pool/src/ops/seize.rs (L23-28)
```rust
    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
```

**File:** contracts/pool/src/guards.rs (L60-65)
```rust
/// Asset units by which supplier claims exceed cash + debt (0 if solvent).
pub(crate) fn backing_shortfall(cache: &Cache) -> i128 {
    let supplied_claim = cache.unscale_supply_floor(cache.supplied());
    let outstanding_debt = cache.unscale_borrow_ceil(cache.borrowed());
    let backing = cache.cash().saturating_add(outstanding_debt);
    supplied_claim.saturating_sub(backing).max(0)
```

**File:** contracts/pool/src/ops/recapitalize.rs (L49-58)
```rust
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** contracts/pool/src/ops/withdraw.rs (L93-118)
```rust
fn resolve_close_or_partial(cache: &Cache, amount: i128, position: Ray) -> (Ray, i128) {
    let (burned, gross_amount) = cache.resolve_withdrawal(amount, position);
    assert_with_error!(
        cache.env(),
        gross_amount == 0 || burned.raw() > 0,
        GenericError::WithdrawRoundsToZeroShares
    );
    (burned, gross_amount)
}

/// Burns `burned` from market supply and returns the user's remaining scaled position.
fn burn_position(env: &Env, cache: &mut Cache, position: Ray, burned: Ray) -> Ray {
    cache.burn_supply(burned);
    position.checked_sub(env, burned)
}

/// Enforces reserve, utilization, and solvency guards, then debits cash for
/// the net transfer. Liquidations and footprint-only closes skip utilization.
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
```

**File:** contracts/pool/src/ops/repay.rs (L44-58)
```rust
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

```

**File:** contracts/controller/src/lib.rs (L90-158)
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
    }

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
```

**File:** contracts/pool/src/cache/scale.rs (L59-67)
```rust
    /// Unscales supply shares rounding **down** (conservative claim value).
    pub(crate) fn unscale_supply_floor(&self, scaled: Ray) -> i128 {
        unscale_supply_floor(
            &self.env,
            scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }
```

**File:** contracts/controller/src/positions/supply.rs (L140-169)
```rust
pub(crate) fn process_withdraw(
    env: &Env,
    caller: &Address,
    account_id: u64,
    withdrawals: &Vec<HubPayment>,
    to: Option<Address>,
) -> Vec<HubPayment> {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);

    finalize_position_flow(
        env,
        account_id,
        &account,
        &mut cache,
        PositionSides::Supply,
        true,
    );
    paid
}
```
