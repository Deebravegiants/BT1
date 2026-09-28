### Title
Supply-index floor preserves wiped-out lender claims and lets them steal later deposits - (File: contracts/pool/src/interest.rs)

### Summary
The bad-debt write-down clamps the supply index to `SUPPLY_INDEX_FLOOR_RAW` even when the loss exceeds all supplier claims. That leaves the wiped market’s old shares with a positive claim instead of zero. A subsequent deposit can then be withdrawn by the supposedly wiped-out supplier, transferring the new cash to shares that should have no backing. [1](#0-0) [2](#0-1) 

### Finding Description
`clean_bad_debt` is a permissionless authenticated path for accounts whose remaining collateral is at or below the dust threshold. [3](#0-2)  During cleanup, pool bad debt is written down through `apply_bad_debt_to_supply_index`. In the extreme case where the bad debt exceeds the market’s total supplied value, the production policy clamps the supply index upward to `RAY / 1000` rather than making the old share supply worthless. [1](#0-0) 

The existing boundary test demonstrates the resulting accounting failure: starting with `old_scaled_raw = 1000 * RAY`, applying a `5000 * RAY` write-down leaves `supply_index == SUPPLY_INDEX_FLOOR_RAW`; the old shares still unscale to a positive amount. After a fresh deposit of that same amount, resolving a full withdrawal for the old shares produces `gross == fresh_cash`, leaving the fresh supplier under-backed. [2](#0-1) 

Withdrawal resolution treats a request at least equal to the half-up current supply as a full close and pays the floor-rounded position value, so the residual phantom claim is directly payable once new cash exists. [4](#0-3) 

### Impact Explanation
An attacker can receive the borrowed principal, have the resulting deficit socialized, and still retain a positive supply claim because the index is clamped above zero. When another user later supplies the asset, the attacker can withdraw the phantom residual claim and take the new deposit. This is theft of user funds and leaves the later supplier’s real claim under-collateralized. [5](#0-4) 

The issue is not a normal pro-rata loss: the write-down is already greater than total supplier claims. The floor creates value after complete loss instead of merely bounding precision during a partial write-down. [6](#0-5) 

### Likelihood Explanation
The attacker can supply the borrow asset, borrow it against a small collateral position, allow accrued debt to exceed the debt-asset supply, and permissionlessly call `update_indexes` and then `clean_bad_debt` once the collateral remainder is within the socialization gate. [7](#0-6) [8](#0-7)  No admin call, leaked key, upgrade, or forged signature is required. The attacker then waits for an unrelated supplier to replenish cash and calls `withdraw` to collect the residual claim. [4](#0-3) 

### Recommendation
Handle complete or over-complete write-downs as a distinct branch in `contracts/pool/src/interest.rs`: when `bad_debt >= total_supplied_value`, set the old share supply’s claim to zero atomically with the cleanup rather than clamping `supply_index` to a positive floor. Keep the positive floor only for strictly partial write-downs where it bounds precision without resurrecting shares. If a nonzero index is required for subsequent deposits, reset the market’s scaled supply and share accounting in the complete-loss branch or use an explicit generation/epoch so pre-wipeout shares cannot be unscaled against post-wipeout cash. Add a regression test asserting that a write-down above total supply leaves `unscale_supply_floor(old_scaled) == 0` and cannot withdraw a later deposit. [9](#0-8) 

### Proof of Concept
1. Attacker supplies asset `A`, supplies a small amount of collateral `B`, and borrows `A`.
2. Interest accrues until the `A` debt exceeds the market’s total `A` supplier claims; the collateral falls to the dust-capped socialization range.
3. Any unprivileged caller executes `clean_bad_debt(caller, victim_account_id)`.
4. The write-down takes the complete-loss branch but clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`; the attacker’s old `A` supply shares still unscale to a positive claim.
5. A victim supplies `A`, crediting real cash to the pool.
6. The attacker calls `withdraw` for the old position. `resolve_withdrawal` returns a positive `gross`, the pool debits the newly deposited cash, and the victim’s claim is left under-backed. [3](#0-2) [2](#0-1)

### Citations

**File:** contracts/pool/README.md (L250-251)
```markdown
Bounds: `MAX_BORROW_INDEX_RAY` and `MAX_SUPPLY_INDEX_RAY` at `1e36`;
`SUPPLY_INDEX_FLOOR_RAW` at `RAY/1000` floors bad-debt write-down.
```

**File:** contracts/pool/tests/interest.rs (L372-427)
```rust
#[test]
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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-243)
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
}
```

**File:** common/src/rates/scaling.rs (L105-120)
```rust
pub fn resolve_withdrawal(
    env: &Env,
    amount: i128,
    pos_scaled: Ray,
    supply_index: Ray,
    decimals: u32,
) -> (Ray, i128) {
    let current_supply_actual = unscale_supply(env, pos_scaled, supply_index, decimals);
    let current_supply_floor = unscale_supply_floor(env, pos_scaled, supply_index, decimals);
    if amount >= current_supply_actual {
        return (pos_scaled, current_supply_floor);
    }
    (
        calculate_scaled_supply_ceil(env, amount, decimals, supply_index),
        amount,
    )
```

**File:** contracts/controller/src/lib.rs (L367-395)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }

    /// Claims pool revenue and forwards measured receipts to the accumulator.
    /// Returns those amounts in asset units, in input order. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn claim_revenue(env: Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
        markets::claim_revenue(&env, caller, assets)
    }

    /// Refreshes supply LTV snapshots. With `has_risks`, also refreshes gated
    /// liquidation parameters and requires a final health factor of at least
    /// 1.05 WAD. Permissionless; requires caller authorization.
    #[when_not_paused]
    fn update_account_threshold(env: Env, caller: Address, has_risks: bool, account_ids: Vec<u64>) {
        risk::params::update_account_threshold(&env, caller, has_risks, account_ids);
    }

    /// Covers a pool backing shortfall using measured receipts from `payer`.
    /// Refunds excess and returns the amount applied in asset units.
    /// Permissionless; requires payer authorization.
    fn recapitalize(env: Env, payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128 {
        markets::recapitalize(&env, payer, hub_asset, amount)
    }
```
