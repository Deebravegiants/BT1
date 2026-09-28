### Title
Bad-debt wipeout resurrects a stranded supplier claim that drains later deposits - ([File: contracts/pool/src/interest.rs])

### Summary
`clean_bad_debt` can write a market’s supply index down to `SUPPLY_INDEX_FLOOR_RAW` without reducing outstanding scaled supply shares. When the calculated index would fall below that floor, surviving suppliers retain a positive residual token claim even though the debt write-down consumed the entire market value. A later deposit creates fresh cash backing for that stale claim, allowing the old supplier to withdraw the new depositor’s funds.

### Finding Description
`apply_bad_debt_to_supply_index` calculates the market’s total supplied value, subtracts capped bad debt, multiplies the old index by the remaining fraction, and then clamps the result upward to `SUPPLY_INDEX_FLOOR_RAW`. [1](#0-0)  The borrow-side pool seize path calls this function and then burns only the insolvent account’s debt shares. [2](#0-1)  Other suppliers’ scaled shares are not burned or otherwise normalized, so clamping the index upward revives claims that the write-down should have reduced to zero.

The controller reaches this code through permissionless `clean_bad_debt`, which requires authorization only from an arbitrary caller, rejects active flash loans, validates that the account is insolvent and collateral is at or below the dust threshold, and executes cleanup. [3](#0-2) [4](#0-3)  The cleanup submits every remaining supply and debt position to the pool as seize entries. [5](#0-4) 

Afterward, withdrawal resolves an account’s shares against the floored index and the pool only verifies that accounting cash is sufficient before debiting and transferring tokens. [6](#0-5) [7](#0-6) [8](#0-7)  The repository’s own regression-style test demonstrates the exact defect: after a wipeout clamps the index upward, a stranded claim extracts a fresh deposit and leaves the new depositor undercollateralized. [9](#0-8) 

### Impact Explanation
This is theft of user funds. The old supplier’s economic claim should be zero after a full supply-index write-down, but the nonzero floor leaves a residual token claim. Once any later supplier deposits cash, the stale holder can call `withdraw` and receive real tokens that should belong to the new supplier. The market then has supply claims exceeding cash and outstanding debt, creating protocol insolvency and potentially permanently freezing later suppliers’ funds.

### Likelihood Explanation
An unprivileged caller can invoke `clean_bad_debt` whenever a real account becomes insolvent with remaining collateral at or below the dust threshold. [10](#0-9)  A full wipeout requires unpaid debt at least equal to the market’s supplied value; such markets can exist after borrowed cash has been withdrawn and collateral has collapsed. The attacker does not need oracle dishonesty or privileged access: they need only hold surviving supply shares in a market where a bad-debt cleanup drives the calculated index to the floor. A later deposit by any victim makes the stranded claim payable.

### Recommendation
Do not clamp the post-write-down supply index upward while nonzero scaled supply remains. Either allow the index to become zero and make subsequent share minting/deposit behavior explicitly handle that state, or proportionally burn/zero surviving supply positions when a cleanup consumes all supplied value. At minimum, reject commits where `supplied != 0`, the computed post-loss index is below `SUPPLY_INDEX_FLOOR_RAW`, and floored residual claims exceed actual backing. Add an end-to-end regression covering `clean_bad_debt`, a subsequent `supply`, and withdrawal by the pre-cleanup supplier.

### Proof of Concept
1. Establish a market where Alice has `1_000` scaled supply and an insolvent account has `1_000` scaled debt, with indexes at `RAY` and no remaining cash.
2. Invoke `clean_bad_debt(caller, account_id)` from any authenticated caller once the account satisfies the dust-gated insolvency condition.
3. The borrow seize calls `apply_bad_debt_to_supply_index`; because the bad debt consumes all supplied value, the computed index becomes zero but is stored as `SUPPLY_INDEX_FLOOR_RAW`.
4. Alice’s scaled supply remains unchanged, so `unscale_supply_floor(alice_scaled)` still returns a positive residual claim.
5. Bob supplies `alice_stranded` tokens, creating fresh pool cash.
6. Alice calls `withdraw(account_id, [(hub_asset, 0)], to)` for a full close, burns her stale shares, and receives Bob’s deposit.
7. Bob’s resulting claim exceeds remaining cash, so later withdrawal fails despite Bob’s honest deposit.

The test at `contracts/pool/tests/interest.rs:430-493` already models these cache-level steps and confirms Alice extracts exactly Bob’s fresh deposit. [11](#0-10)

### Citations

**File:** contracts/pool/src/interest.rs (L73-89)
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
}
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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-199)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L222-237)
```rust
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

**File:** contracts/pool/src/ops/withdraw.rs (L109-119)
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
}
```

**File:** contracts/pool/src/cache/cash.rs (L14-21)
```rust
    /// Panics if cash reserves are below `amount`.
    pub(crate) fn require_reserves(&self, amount: i128) {
        assert_with_error!(
            self.env,
            self.cash >= amount,
            CollateralError::InsufficientLiquidity
        );
    }
```

**File:** contracts/pool/tests/interest.rs (L430-493)
```rust
#[test]
fn test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let alice_scaled_raw = 1_000 * RAY;
        let borrowed_scaled_raw = 1_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: alice_scaled_raw,
            borrowed: borrowed_scaled_raw,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let alice_scaled = Ray::from(alice_scaled_raw);
        let borrow_scaled = Ray::from(borrowed_scaled_raw);

        let bad_debt = cache.unscale_borrow_ceil_ray(borrow_scaled);
        apply_bad_debt_to_supply_index(&mut cache, bad_debt);
        cache.burn_debt(borrow_scaled);

        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "seize wipeout clamps supply_index UP to RAY/1000, leaving unburned shares a residual"
        );

        let alice_stranded = cache.unscale_supply_floor(alice_scaled);
        assert!(alice_stranded > 0, "wiped survivor keeps a stranded claim");
        assert_eq!(
            cache.cash(),
            0,
            "empty market: claim masked by require_reserves"
        );

        let deposit = alice_stranded;
        let bob_scaled = cache.calculate_scaled_supply(deposit);
        cache.mint_supply(bob_scaled);
        cache.credit_cash(deposit);

        let total_owed = cache.unscale_supply_floor(cache.supplied());
        assert!(
            total_owed > cache.cash(),
            "post-deposit books insolvent: owed {} > cash {}",
            total_owed,
            cache.cash()
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, alice_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "wiped position pays out real cash");
        assert_eq!(gross, deposit, "Alice extracts exactly Bob's fresh deposit");

        let bob_claim = cache.unscale_supply_floor(bob_scaled);
        assert!(
            cache.cash() < bob_claim,
            "cash {} cannot cover Bob's honest claim {}: fresh depositor lost funds",
            cache.cash(),
            bob_claim
        );
```
