### Title
Bad-debt cleanup floor leaves wiped suppliers a recoverable claim - (File: contracts/pool/src/interest.rs)

### Summary

When bad debt meets or exceeds the market’s total supplied value, `apply_bad_debt_to_supply_index` clamps `supply_index` upward to `SUPPLY_INDEX_FLOOR_RAW` instead of reducing surviving supply shares to zero. [1](#0-0)  Existing supply positions therefore retain a positive floor-valued claim even though cleanup was intended to write the market down completely. [2](#0-1)  Once another supplier deposits fresh cash, the wiped supplier can withdraw that residual claim and consume the new deposit. [3](#0-2) 

### Finding Description

Permissionless `clean_bad_debt` accepts an insolvent account whose collateral is at or below the dust threshold and invokes `execute_bad_debt_cleanup`. [4](#0-3)  Cleanup sends every remaining borrow position to the pool as a borrow-side seizure. [5](#0-4) 

For a borrow-side seizure, the pool converts the removed debt shares to an asset value, writes that amount down against the supply index, and burns the debt. [6](#0-5)  The write-down caps the loss at the total supplied value, but then applies `max(SUPPLY_INDEX_FLOOR_RAW)`, producing a nonzero index even when the capped loss removes all supplier value. [7](#0-6) 

The pool does not clear or separately mark the surviving suppliers’ scaled share counts. [8](#0-7)  A later withdrawal resolves those same shares against the clamped index and transfers the resulting gross amount if accounting `cash` is sufficient. [9](#0-8)  A fresh supplier adds both scaled shares and cash through the normal controller `supply` path. [10](#0-9) 

### Impact Explanation

A supplier whose claim should have been fully written down can drain cash deposited after the cleanup. [1](#0-0)  The floor leaves `scaled_supply * SUPPLY_INDEX_FLOOR_RAW` claimable; with enough scaled supply or decimal scaling, that residual can be economically meaningful. [2](#0-1)  The attacker’s withdrawal is authorized because it uses their own surviving supply position, while the pool only checks whether `cash >= amount` before paying. [11](#0-10)  This is theft of the fresh supplier’s funds and leaves the market undercollateralized. [12](#0-11) 

### Likelihood Explanation

The required state is reachable through normal borrowing followed by bad debt that equals or exceeds the market’s supplied value, such as after near-total utilization plus interest accrual or collateral devaluation. [13](#0-12)  `clean_bad_debt(caller, account_id)` is permissionless once the dust and insolvency gates pass. [14](#0-13)  The final theft only requires an unrelated or attacker-created fresh deposit and a normal owner withdrawal. [15](#0-14) 

### Recommendation

When `bad_debt >= total_supplied_value`, clear all outstanding scaled supply claims or set the supply index to an explicit zero-value state that cannot later unscale into assets. [1](#0-0)  If the nonzero floor must remain to avoid division by zero, carry a separate market tombstone/claim-disabled flag and have `calculate_scaled_supply`, `resolve_withdrawal`, revenue claiming, and rescue logic honor it. [16](#0-15)  Add an end-to-end test that performs `clean_bad_debt`, deposits fresh cash, and asserts that a pre-cleanup supplier withdraws zero. [17](#0-16) 

### Proof of Concept

1. Attacker calls `supply(attacker, 0, spoke_id, [(debt_market, attacker_amount)])`, creating a supplier account in the market that will later absorb the write-down. [18](#0-17) 
2. A victim account supplies dust collateral and borrows the market asset; subsequent interest accrual or collateral devaluation makes `total_debt > total_collateral` while collateral remains at or below the cleanup threshold. [19](#0-18) 
3. Any caller invokes `clean_bad_debt(caller, victim_account_id)`. [14](#0-13) 
4. The pool burn-side seizure computes bad debt at least equal to total supplied value, causing `remaining == 0` but storing `supply_index = SUPPLY_INDEX_FLOOR_RAW`. [1](#0-0) 
5. A fresh supplier calls `supply(fresh_user, 0, spoke_id, [(debt_market, fresh_amount)])`; the pool mints shares and credits the measured deposit to `cash`. [10](#0-9) 
6. The attacker calls `withdraw(attacker, attacker_account_id, [(debt_market, 0)], None)`, where zero requests the entire surviving position. [20](#0-19) 
7. The pool resolves the attacker’s old shares against the floored index, passes the reserve check using the fresh supplier’s cash, debits that cash, and transfers it to the attacker. [9](#0-8)

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

**File:** contracts/pool/src/cache/scale.rs (L60-66)
```rust
    pub(crate) fn unscale_supply_floor(&self, scaled: Ray) -> i128 {
        unscale_supply_floor(
            &self.env,
            scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
```

**File:** contracts/pool/src/cache/scale.rs (L94-105)
```rust
    /// Resolves a withdrawal request into (shares burned, gross asset amount).
    ///
    /// Caps against `pos_scaled` so the user cannot withdraw more than held.
    pub(crate) fn resolve_withdrawal(&self, amount: i128, pos_scaled: Ray) -> (Ray, i128) {
        resolve_withdrawal(
            &self.env,
            amount,
            pos_scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }
```

**File:** contracts/pool/src/ops/withdraw.rs (L65-80)
```rust
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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-199)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-237)
```rust
    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L35-45)
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
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L48-60)
```rust
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);

    cache.persist_spoke_usage();

    CleanBadDebtEvent {
        account_id,
        total_borrow_usd_wad: totals.total_debt.raw(),
        total_collateral_usd_wad: totals.total_collateral.raw(),
    }
    .publish(env);

    remove_account_and_burn_nft(env, account_id);
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

**File:** contracts/pool/src/cache/shares.rs (L19-23)
```rust
    /// Burns scaled supply shares, then asserts revenue ≤ total supply.
    pub(crate) fn burn_supply(&mut self, scaled: Ray) {
        self.supplied = self.supplied.checked_sub(&self.env, scaled);
        self.require_revenue_backed();
    }
```

**File:** contracts/controller/src/positions/supply.rs (L40-63)
```rust
pub(crate) fn process_supply(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    assets: &Vec<HubPayment>,
) -> u64 {
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);

    process_deposit(env, caller, &mut account, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/supply.rs (L116-134)
```rust
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_supply_leg(env, account, &entry.action, &result, cache);
```

**File:** contracts/controller/src/positions/supply.rs (L140-157)
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
```

**File:** contracts/controller/src/positions/supply.rs (L180-198)
```rust
    let mut entries: Vec<PoolWithdrawEntry> = Vec::new(env);
    for (hub_asset, amount) in aggregated.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &hub_asset,
            FreezePolicy::AllowOnExit,
        );
        let position = get_supply_position_or_panic(env, account, &hub_asset);
        let requested = if amount == 0 {
            WITHDRAW_ALL_SENTINEL
        } else {
            amount
        };
        entries.push_back(PoolWithdrawEntry {
            action: make_pool_action(&position, requested, hub_asset.clone()),
            protocol_fee: 0,
        });
```

**File:** contracts/pool/src/cache/cash.rs (L14-20)
```rust
    /// Panics if cash reserves are below `amount`.
    pub(crate) fn require_reserves(&self, amount: i128) {
        assert_with_error!(
            self.env,
            self.cash >= amount,
            CollateralError::InsufficientLiquidity
        );
```
