### Title
Pending bad-debt write-downs can be dodged by exiting before cleanup and re-entering afterward - (File: contracts/pool/src/ops/seize.rs)

### Summary

The analogous stale-value primitive is the delay between an account becoming insolvent and the permissionless `clean_bad_debt` call that socializes that debt. A supplier can withdraw at the pre-write-down supply index, trigger cleanup, and immediately redeposit, leaving the remaining suppliers to absorb the entire loss. [1](#0-0) [2](#0-1) 

### Finding Description

Every normal pool leg loads the market through `ops::load_leg`, which calls `synced_market` and accrues ordinary interest before conversion, so this is not a stale interest-index issue. [3](#0-2) 

A withdrawal burns supply shares and pays out against the market’s current `supply_index` through `resolve_withdrawal`. [4](#0-3) [5](#0-4) 

That index does not yet reflect a merely eligible bad-debt account: `clean_bad_debt` is a separate permissionless controller call gated only by `debt > collateral` and collateral being at or below the dust threshold. [1](#0-0) [6](#0-5) 

When cleanup runs, the pool computes the debt’s current value, reduces `supply_index` proportionally, and burns the debt shares. [2](#0-1) [7](#0-6) 

Therefore, the economically equivalent sequence is `withdraw` before the value update, `clean_bad_debt`, then `supply` at the reduced exchange rate; the repository’s composition test explicitly proves this atomic path. [8](#0-7) 

### Impact Explanation

The attacker exits with the full pre-loss value of their shares instead of taking a pro-rata write-down. [9](#0-8) 

After cleanup, the same attacker can redeposit the recovered assets at the reduced supply index, while every supplier who remained loses claim value through the lowered index. [7](#0-6) [10](#0-9) 

This is theft of user funds in the same sense as the reported cached-versus-actual NAV arbitrage: value that should have been socialized across all suppliers is shifted onto the suppliers who did not exit first. [11](#0-10) 

### Likelihood Explanation

The attack is fully permissionless: the attacker only needs to own a supply account in the affected market and observe an account satisfying the public `clean_bad_debt` gate. [1](#0-0) [12](#0-11) 

The exit size is constrained by available cash, the max-utilization check after withdrawal, and the rule that open debt cannot remain with zero supply. [13](#0-12) [14](#0-13) 

Those checks bound, but do not eliminate, the extraction: the test demonstrates a full exit, cleanup, and re-entry when utilization permits, and a partial dodge remains possible wherever the withdrawal ceiling is nonzero. [15](#0-14) [16](#0-15) 

### Recommendation

Do not let ordinary supplier exits price claims ahead of pending socializable bad debt.

Conceptually, cleanup should be forced or accounted for before non-liquidation withdrawals and deposits in the affected market, or withdrawal valuation should deduct eligible bad debt even before its bookkeeping is committed. At minimum, batch eligible `clean_bad_debt` processing into the withdrawal path or expose a market-level pending-write-down state that prevents suppliers from racing the socialization event. The affected functions are `Controller::withdraw`, `Controller::clean_bad_debt`, `Pool::withdraw`, and `Pool::seize_positions`. [17](#0-16) [18](#0-17) 

### Proof of Concept

1. Create an ETH market where the attacker owns supply account `A_attacker`, another supplier remains in the market, and victim account `A_victim` has open ETH debt whose collateral value is below the bad-debt dust threshold. [6](#0-5) 

2. In one contract-controlled invocation, call:

   ```text
   Controller.withdraw(
       caller = attacker_contract,
       account_id = A_attacker,
       withdrawals = [(HubAssetKey { hub_id, asset = ETH }, 0)],
       to = None,
   )
   ```

   The zero amount means withdraw the full position, and the pool pays according to the pre-cleanup `supply_index`. [19](#0-18) [20](#0-19) 

3. In the same invocation, call:

   ```text
   Controller.clean_bad_debt(
       caller = attacker_contract,
       account_id = A_victim,
   )
   ```

   The pool values the victim’s debt shares, lowers `supply_index`, and burns those debt shares. [21](#0-20) [2](#0-1) 

4. Re-enter with:

   ```text
   Controller.supply(
       caller = attacker_contract,
       account_id = 0,
       spoke_id = original_spoke,
       assets = [(HubAssetKey { hub_id, asset = ETH }, withdrawn_amount)],
   )
   ```

   The deposit mints shares at the lower post-cleanup supply index, so the attacker retains approximately the entire withdrawn value while other suppliers absorb the write-down. [22](#0-21) [8](#0-7)

### Citations

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

**File:** contracts/pool/src/ops/seize.rs (L24-28)
```rust
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
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

**File:** contracts/pool/src/ops/withdraw.rs (L93-100)
```rust
fn resolve_close_or_partial(cache: &Cache, amount: i128, position: Ray) -> (Ray, i128) {
    let (burned, gross_amount) = cache.resolve_withdrawal(amount, position);
    assert_with_error!(
        cache.env(),
        gross_amount == 0 || burned.raw() > 0,
        GenericError::WithdrawRoundsToZeroShares
    );
    (burned, gross_amount)
```

**File:** contracts/pool/src/cache/scale.rs (L94-104)
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
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
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

**File:** tests/test-harness/tests/composition/supplier_exit_before_socialization_is_bounded_by_utilization.rs (L1-3)
```rust
//! GH-15. A supplier can leave, trigger the permissionless clean-up, and come
//! back in one invocation, dodging its share of the write-down. The exit
//! size is bounded by `max_utilization`: past it the whole script reverts.
```

**File:** tests/test-harness/tests/composition/supplier_exit_before_socialization_is_bounded_by_utilization.rs (L52-79)
```rust
#[test]
fn exit_then_clean_then_re_enter_dodges_the_write_down_when_utilization_allows() {
    let Seed {
        t,
        runner,
        runner_account,
        victim,
    } = seed(true, 0.0);
    let bob_before = t.supply_balance_raw(BOB, "ETH");
    let ops: Vec<Op> = vec![
        &t.env,
        withdraw_op(&t, runner_account, "ETH", 0, None),
        Op::CleanBadDebt(AccountOp { account_id: victim }),
        supply_op(&t, 0, "ETH", 50 * U),
    ];
    let new_id = t
        .run_script(&runner, &ops)
        .expect("atomic exit, clean, re-enter");
    assert!(new_id > 0 && new_id != runner_account);
    assert!(
        t.supply_balance_raw_for(new_id, "ETH") >= 50 * U - 1,
        "the runner kept its whole stake"
    );
    assert!(
        t.supply_balance_raw(BOB, "ETH") < bob_before,
        "BOB absorbed the entire write-down"
    );
}
```

**File:** contracts/pool/src/guards.rs (L19-33)
```rust
pub(crate) fn require_utilization_below_max(env: &Env, cache: &Cache) {
    if cache.supplied() == Ray::ZERO || cache.params().max_utilization >= Ray::ONE {
        return;
    }

    let borrowed = cache.borrowed().mul_ceil(env, cache.borrow_index());
    if borrowed == Ray::ZERO {
        return;
    }
    let supplied = cache.supplied().mul_floor(env, cache.supply_index());
    assert_with_error!(
        env,
        supplied > Ray::ZERO && borrowed.div_ceil(env, supplied) <= cache.params().max_utilization,
        CollateralError::UtilizationAboveMax
    );
```

**File:** contracts/pool/src/guards.rs (L68-73)
```rust
/// Panics with `PoolInsolvent` if supplied is zero while borrowed debt is non-zero.
pub(crate) fn require_supply_for_debt(env: &Env, cache: &Cache) {
    if cache.supplied() == Ray::ZERO && cache.borrowed() != Ray::ZERO {
        panic_with_error!(env, CollateralError::PoolInsolvent);
    }
}
```

**File:** tests/test-harness/tests/controller/bad_debt_netting_and_exit_timing.rs (L131-181)
```rust
/// Measures how much of a market a large supplier can withdraw.
/// `require_utilization_below_max` runs after the burn, so the exit ceiling is
/// `f <= 1 - u / max_utilization` of total supply (`max_utilization` is 95% in
/// the preset). Probes each side of the closed form on a fresh fixture.
#[test]
fn withdrawal_ceiling_tracks_one_minus_utilization_over_max() {
    // 100 ETH of real supply: Bob 80, Carol 20. Dave drives utilization.
    fn fixture(target_u: u32) -> LendingTest {
        let mut t = setup();
        t.supply(BOB, "ETH", 80.0);
        t.supply(CAROL, "ETH", 20.0);
        let borrow = 100.0 * f64::from(target_u) / 100.0;
        t.supply(DAVE, "USDC", borrow * 2000.0 * 2.0);
        t.borrow(DAVE, "ETH", borrow);
        t
    }

    for target_u in [10u32, 50, 80, 90] {
        let u = f64::from(target_u) / 100.0;
        // Closed form, in ETH of the 100 supplied, clamped to Bob's 80.
        let predicted = ((1.0 - u / 0.95) * 100.0).clamp(0.0, 80.0);
        let below = (predicted - 0.5).max(0.0);
        let above = predicted + 0.5;

        let ok_below = fixture(target_u).try_withdraw(BOB, "ETH", below).is_ok();
        let res_above = fixture(target_u).try_withdraw(BOB, "ETH", above);
        let ok_above = res_above.is_ok();

        std::println!(
            "V3 exit ceiling: utilization={}%  predicted_max={:.2} ETH \
             ({:.1}% of Bob\'s 80)  withdraw({:.2})={}  withdraw({:.2})={}",
            target_u,
            predicted,
            predicted / 80.0 * 100.0,
            below,
            if ok_below { "OK" } else { "REVERT" },
            above,
            if ok_above { "OK" } else { "REVERT" }
        );

        assert!(
            ok_below,
            "u={}%: withdrawal just below the ceiling must succeed",
            target_u
        );
        if predicted < 79.9 {
            // Pins the error: a bare `!is_ok()` also passes on insufficient
            // collateral or a fixture break.
            assert_contract_error(res_above, errors::UTILIZATION_ABOVE_MAX);
        }
    }
```

**File:** contracts/controller/src/lib.rs (L117-128)
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
```

**File:** contracts/controller/src/lib.rs (L160-165)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
    }
```

**File:** contracts/controller/src/positions/supply.rs (L180-199)
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
    }
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

**File:** contracts/pool/src/ops/supply.rs (L28-40)
```rust
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
```
