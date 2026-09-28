### Title
Bad-debt index floor resurrects wiped supply claims, letting stranded suppliers drain repayments - (File: contracts/pool/src/interest.rs)

### Summary

Borrow-side seizure socializes bad debt by reducing `supply_index`, but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` even when the bad debt consumes the entire supply claim. This leaves every existing scaled supply position with a positive claim after an economic wipeout. A permissionless `clean_bad_debt` call can create this state; later debt repayments restore pool cash without restoring the intended zero supplier claim, allowing a stranded supplier to withdraw those repayments and leave remaining lenders unpaid.

### Finding Description

`clean_bad_debt` is permissionless once an insolvent account's remaining collateral is at or below the dust cap. [1](#0-0)  Cleanup submits every debt position to `pool_seize_positions_call`, while also reclassifying the account's residual deposit positions as revenue. [2](#0-1) 

For a borrow-side pool seizure, the pool converts the seized debt shares to a ceiled debt value, calls `apply_bad_debt_to_supply_index`, and then burns the debt. [3](#0-2)  The write-down computes `remaining = total_supplied_value - capped_bad_debt`, so a complete wipeout should produce a zero-valued aggregate supplier claim. [4](#0-3) 

The bug is that the resulting index is raised to `SUPPLY_INDEX_FLOOR_RAW`, not merely prevented from becoming zero when a nonzero remaining claim exists. [5](#0-4)  Because user balances are stored as scaled shares and later valued at the live `supply_index`, all pre-wipeout supply shares retain `scaled_amount * floor` of claim even though the socialization arithmetic determined they should be worth zero. [6](#0-5) 

Subsequent `repay` calls burn debt shares and credit actual measured repayments to market cash. [7](#0-6)  Withdrawal then values stale supply shares at the floored index, requires only that current cash covers the payout, burns those shares, and debits cash. [8](#0-7)  Cash withdrawal does not require the market to become backed first, so stale claims can consume funds repaid by other borrowers. [9](#0-8) 

### Impact Explanation

An attacker holding wiped supply shares can wait for honest borrowers to repay, then call `withdraw` and take cash that was intended to back remaining debt and recapitalize the market. The stale floor claims can also leave the market permanently undercollateralized until an outside payer recapitalizes it, at which point the stale claims can consume the recapitalization. This causes theft of user funds and can leave the market unable to resume normal operation.

### Likelihood Explanation

The trigger is reachable by an unprivileged address through ordinary market activity followed by permissionless `clean_bad_debt`. The required condition is severe insolvency where accrued unbacked debt meets or exceeds the total scaled supply value, causing `remaining` to reach zero. That can arise when borrowed cash has left the pool and debt later grows beyond supply through interest. No privileged role, leaked key, route manipulation, or off-chain service is required; any authenticated caller can invoke cleanup once the dust gate is satisfied. [10](#0-9) 

### Recommendation

Only apply `SUPPLY_INDEX_FLOOR_RAW` when `remaining` is nonzero. A complete write-down should produce a zero supply index and simultaneously handle revenue claims consistently, or alternatively burn all outstanding supply/revenue shares during total bad-debt socialization.

For example, replace the unconditional maximum with logic equivalent to:

```rust
let new_supply_index = if remaining == Ray::ZERO {
    Ray::ZERO
} else {
    cache
        .supply_index()
        .mul_floor(env, reduction_factor)
        .max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))
};
```

The implementation must also ensure that views and withdrawal code safely handle a zero supply index, and that a zero index does not permit subsequent deposits to mint unbounded shares. A safer accounting approach is to zero or burn the outstanding scaled supply and revenue balances when the bad-debt write-down exhausts total supplied value.

### Proof of Concept

1. Supplier Alice calls `supply` for market `(hub_id, asset)`, creating `S` scaled supply shares.
2. Borrower creates an account and calls `borrow`, removing most pool cash while minting `D` scaled debt shares.
3. Time passes and the debt index grows until Borrower's debt value is at least the market's entire supplied value, while the account's collateral is worth no more than the bad-debt dust cap.
4. Any authenticated caller invokes `clean_bad_debt(caller, account_id)`.
5. `execute_bad_debt_cleanup` submits the borrow position as a `PoolSeizeEntry` with `side = AccountPositionType::Borrow`. [11](#0-10) 
6. `seize::apply` computes the debt value and calls `apply_bad_debt_to_supply_index`. [3](#0-2) 
7. Since `bad_debt >= total_supplied_value`, `remaining` becomes zero and `reduction_factor` becomes zero. [12](#0-11) 
8. The unconditional floor changes the mathematically correct index of zero to `SUPPLY_INDEX_FLOOR_RAW`, preserving a positive value for Alice's stale `S` shares. [13](#0-12) 
9. Another borrower later calls `repay`, which burns debt shares and credits cash to the pool. [14](#0-13) 
10. Alice calls controller `withdraw` for her old supply position. The pool resolves her shares at the floored index, passes `require_reserves` because the repayment added cash, burns the stale shares, and transfers the repaid tokens to Alice. [15](#0-14) 
11. The repaying borrower's cash has been consumed by an economically wiped claim, while the remaining market claims remain under-backed.

### Citations

**File:** contracts/controller/src/lib.rs (L160-164)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L21-49)
```rust
    let mut entries: Vec<PoolSeizeEntry> = Vec::new(env);
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Supply,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Deposit,
            position: (&position).into(),
        });
    }
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

**File:** contracts/pool/src/cache/scale.rs (L49-66)
```rust
    /// Unscales supply shares to asset units with half-up rounding.
    pub(crate) fn unscale_supply(&self, scaled: Ray) -> i128 {
        unscale_supply(
            &self.env,
            scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }

    /// Unscales supply shares rounding **down** (conservative claim value).
    pub(crate) fn unscale_supply_floor(&self, scaled: Ray) -> i128 {
        unscale_supply_floor(
            &self.env,
            scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
```

**File:** contracts/pool/src/ops/repay.rs (L44-59)
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

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/withdraw.rs (L63-82)
```rust
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
    let mutation = cache.position_mutation(remaining, gross_amount);
```

**File:** contracts/pool/src/ops/withdraw.rs (L109-118)
```rust
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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-237)
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
```
