### Title
Bad-debt index floor preserves phantom supplier claims that drain later deposits - ([File: contracts/pool/src/interest.rs]) [1](#0-0) 

### Summary
When bad debt exceeds the remaining value of all supply shares, `apply_bad_debt_to_supply_index` clamps the supply index to `SUPPLY_INDEX_FLOOR_RAW` instead of reducing supplier claims to zero or burning the corresponding shares. Existing suppliers therefore retain positive shares that regain value as soon as new cash enters the pool. [2](#0-1) 

### Finding Description
`controller::clean_bad_debt` is permissionless once an account is insolvent and its residual collateral is at or below the dust threshold. [3](#0-2)  Cleanup sends every borrow position to `pool_seize_positions_call`, where a `Borrow` entry is converted to RAY-denominated bad debt and passed to `apply_bad_debt_to_supply_index`. [4](#0-3) 

The function caps the debt at total supplied value, computes a zero `remaining` amount and a zero `reduction_factor`, but then applies `new_supply_index.max(SUPPLY_INDEX_FLOOR_RAW)`. [5](#0-4)  The floor makes every preexisting scaled supply position retain a positive claim even though the debt write-off consumed the entire backing value. [6](#0-5) 

A withdrawal resolves the stale scaled shares against that floored index, checks only available reserves, and debits pool cash. [7](#0-6) 

### Impact Explanation
An existing supplier whose claim should have been wiped out can wait for an honest supplier to deposit into the distressed market and then withdraw the new deposit. [8](#0-7)  This is theft of user funds and leaves the honest supplier under-backed; it also means `recapitalize` donations can be captured by the phantom supplier rather than restoring the market. [9](#0-8) 

### Likelihood Explanation
The attacker needs only a preexisting scaled supply position in a market that later undergoes a full bad-debt write-down, plus a subsequent deposit or recapitalization. `clean_bad_debt` itself is callable by any authorized address when the documented dust-gated insolvency condition is met. [10](#0-9)  The repository’s own unit test demonstrates the full residual-claim and fresh-cash drain arithmetic directly against the production cache functions. [11](#0-10) 

### Recommendation
Do not restore supplier value with a global index floor after a complete write-down. Either burn or proportionally reduce all scaled supply/revenue claims during the wipeout, or maintain a separate residual-loss ledger so floored accounting cannot turn exhausted shares into claims on later deposits. [1](#0-0)  Add an end-to-end invariant that total withdrawable supply cannot exceed pool cash after `clean_bad_debt`, including after fresh deposits and recapitalization. [12](#0-11) 

### Proof of Concept
1. Supplier A deposits `1_000_000` asset units and receives scaled supply in a market with `cash = 0` backing after accounting.
2. A borrower’s unpaid debt equivalent to `2_000_000` units becomes eligible for `clean_bad_debt`.
3. `clean_bad_debt` invokes the pool seize operation, which calls `apply_bad_debt_to_supply_index`. [4](#0-3) 
4. Because debt exceeds total supplied value, `remaining = 0`, `reduction_factor = 0`, and the supply index is nevertheless clamped to `SUPPLY_INDEX_FLOOR_RAW`. [5](#0-4) 
5. Supplier A’s original shares still unscale to a positive stranded claim. [13](#0-12) 
6. Supplier B deposits `c`; A requests a full withdrawal, passes `require_reserves`, burns the floored shares, and receives exactly `c`. [14](#0-13) 
7. The pool is left with zero cash while B still has a positive recorded claim, proving loss transfer to the later depositor. [15](#0-14)

### Citations

**File:** contracts/pool/src/interest.rs (L68-89)
```rust
/// Socializes `bad_debt` by reducing the supply index (capped at total supply value).
///
/// Used when seizing unpaid debt: remaining supplier claims shrink pro-rata.
/// No-op when total supplied value is zero. Floors the resulting index at
/// [`SUPPLY_INDEX_FLOOR_RAW`] to avoid a zero index.
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

**File:** contracts/controller/src/lib.rs (L160-164)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
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

**File:** contracts/pool/tests/interest.rs (L316-369)
```rust
#[test]
fn test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let scaled_a_raw = 1_000_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: scaled_a_raw,
            borrowed: 0,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let scaled_a = Ray::from(scaled_a_raw);

        apply_bad_debt_to_supply_index(&mut cache, Ray::from(2_000_000 * RAY));
        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "wipeout must clamp supply index UP to the floor, not reset the base"
        );

        let stranded = cache.unscale_supply_floor(scaled_a);
        assert!(stranded > 0, "floor clamp leaves userA a phantom claim");
        assert_eq!(cache.cash(), 0, "empty market: no cash to extract yet");

        let c = stranded;
        let scaled_b = cache.calculate_scaled_supply(c);
        cache.mint_supply(scaled_b);
        cache.credit_cash(c);

        let b_claim = cache.unscale_supply_floor(scaled_b);
        assert_eq!(b_claim, c, "userB's honest claim equals their deposit");

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, scaled_a);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "stranded position pays out non-zero");
        assert_eq!(
            gross, c,
            "userA drains exactly userB's fresh deposit out of the pool"
        );

        assert!(
            cache.cash() < b_claim,
            "pool cash ({}) can no longer cover userB's claim ({}): honest supplier lost funds",
            cache.cash(),
            b_claim
        );
        assert_eq!(cache.cash(), 0, "userA drained the pool to empty");
    });
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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-220)
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
```
