### Title

Bad-debt cleanup leaves wiped suppliers a residual claim that drains later deposits - (File: contracts/pool/src/interest.rs)

### Summary

The bad-debt path converts an account’s unpaid debt into a pro-rata reduction of `supply_index`, but clamps the resulting index to `SUPPLY_INDEX_FLOOR_RAW`. When a loss should reduce the index to zero, every existing scaled supply share retains a small claim instead. After new deposits restore pool cash, those stale shares can withdraw real tokens that are no longer backed by their original socialization outcome.

### Finding Description

`clean_bad_debt` is permissionless and invokes `execute_bad_debt_cleanup`, which submits all remaining deposit and borrow positions to the pool through `pool_seize_positions_call`. [1](#0-0) [2](#0-1) 

For a borrow entry, the pool calculates the debt’s underlying value, calls `apply_bad_debt_to_supply_index`, and burns the debt shares. [3](#0-2) 

`apply_bad_debt_to_supply_index` correctly computes a zero remaining factor when `bad_debt >= total_supplied_value`, but then applies `.max(SUPPLY_INDEX_FLOOR_RAW)`. This changes the outcome from a complete write-down to a nonzero index while leaving all previously issued scaled supply shares alive. [4](#0-3) 

Withdrawals resolve a stored scaled position through `resolve_withdrawal`, enforce cash availability, burn the returned shares, and transfer the gross amount. [5](#0-4) [6](#0-5) 

The repository’s own regression test demonstrates the accounting consequence: a 5,000-unit bad-debt write-down against 1,000 scaled units clamps the index to the floor, preserves a positive claim for the old shares, and lets that claim withdraw the full amount of a subsequent deposit. [7](#0-6) 

### Impact Explanation

This is theft of user funds and can create protocol insolvency.

A permissionless caller can invoke `controller::clean_bad_debt(caller, account_id)` on an account satisfying `total_debt > total_collateral` and `total_collateral <= BAD_DEBT_USD_THRESHOLD`. [8](#0-7) [9](#0-8) 

If the account’s unpaid debt is at least the market’s total supplied value, suppliers should be written down completely. Instead, the floor leaves each supply share with `SUPPLY_INDEX_FLOOR_RAW` value. Once later suppliers add cash, holders of those stale shares—including an attacker who held a pre-cleanup supply position—can withdraw tokens funded by the later deposits.

### Likelihood Explanation

Triggering the bug requires a reachable bad-debt cleanup where the socialized borrow amount reaches or exceeds total supplied value. That can arise after collateral impairment and interest accrual leave an insolvent account with collateral under the dust threshold; no privileged call, leaked key, parameter error, or oracle malfunction is needed at the cleanup step.

The theft becomes practical after subsequent deposits replenish cash in the same market. Fresh supply is measured and minted normally, while the incorrectly preserved old shares remain claimable. [10](#0-9) 

### Recommendation

Do not clamp a completely wiped supply index to `SUPPLY_INDEX_FLOOR_RAW` in `apply_bad_debt_to_supply_index`. Preserve the floor only for positive remaining supply value; when `remaining == 0`, commit a state that makes all existing scaled supply claims zero, or explicitly clear/zero the supplied-share total before assigning the floored index. Add an integration test that performs permissionless `clean_bad_debt`, deposits afterward, and proves pre-cleanup supply positions cannot withdraw the new cash.

### Proof of Concept

1. Reach an insolvent account eligible for permissionless cleanup:
   - `total_debt > total_collateral`
   - `total_collateral <= BAD_DEBT_USD_THRESHOLD`
   - the account’s residual debt is at least the same market’s total supplied value.
2. Call:

   `controller.clean_bad_debt(attacker_or_any_caller, victim_account_id)`

   The cleanup serializes the account’s deposit and debt positions into `PoolSeizeEntry` values and calls `pool.seize_positions`. [2](#0-1) 
3. In the pool’s borrow leg, `apply_bad_debt_to_supply_index` calculates:
   - `capped = total_supplied_value`
   - `remaining = 0`
   - `reduction_factor = 0`
   - calculated `new_supply_index = 0`
   - committed `supply_index = SUPPLY_INDEX_FLOOR_RAW`
4. Existing scaled supply shares therefore still resolve to a positive withdrawal amount.
5. A new supplier calls `controller.supply(...)` for the same hub asset, transferring real tokens into the pool.
6. The owner of the stale shares calls `controller.withdraw(caller, old_account_id, [(hub_asset, 0)], Some(recipient))`. The pool resolves the stale shares at the floored index, debits the newly deposited cash, and transfers it to the recipient.

The existing internal test reproduces the same arithmetic: `old_scaled_raw = 1_000 * RAY`, `bad_debt = 5_000 * RAY`, the index clamps to `SUPPLY_INDEX_FLOOR_RAW`, and the stranded old position withdraws exactly the fresh deposit. [11](#0-10)

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-200)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}
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

**File:** contracts/pool/src/ops/withdraw.rs (L63-80)
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

```

**File:** contracts/pool/src/ops/withdraw.rs (L91-106)
```rust
/// Maps requested amount and position to shares burned and gross asset amount.
/// Panics if a nonzero gross amount would burn zero shares.
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
```

**File:** contracts/pool/tests/interest.rs (L373-427)
```rust
fn test_raw_cache_floor_clamp_strands_claim_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let old_scaled_raw = 1_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: old_scaled_raw,
            borrowed: 0,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let old_scaled = Ray::from(old_scaled_raw);

        apply_bad_debt_to_supply_index(&mut cache, Ray::from(5_000 * RAY));
        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "wipeout clamps supply_index UP to RAY/1000 instead of resetting shares to 0",
        );

        let stranded = cache.unscale_supply_floor(old_scaled);
        assert!(stranded > 0, "floor clamp leaves S_old a phantom claim");
        assert_eq!(
            cache.cash(),
            0,
            "no cash yet: invariant only masked by require_reserves"
        );

        let fresh_cash = stranded;
        let fresh_scaled = cache.calculate_scaled_supply(fresh_cash);
        cache.mint_supply(fresh_scaled);
        cache.credit_cash(fresh_cash);

        let fresh_claim = cache.unscale_supply_floor(fresh_scaled);
        assert_eq!(
            fresh_claim, fresh_cash,
            "fresh supplier's claim equals deposit"
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, old_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "stranded wiped position pays out real tokens");
        assert_eq!(gross, fresh_cash, "S_old drains exactly the fresh deposit");
        assert!(
            cache.cash() < fresh_claim,
            "pool cash ({}) can no longer cover fresh supplier claim ({}): funds lost",
            cache.cash(),
            fresh_claim,
        );
    });
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** contracts/pool/src/ops/supply.rs (L23-41)
```rust
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);

    cache.credit_cash(amount);

    let snapshot = cache.commit();
    (cache.position_mutation(position, amount), snapshot)
```
