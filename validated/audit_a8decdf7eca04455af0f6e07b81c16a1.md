### Title
Bad-debt socialization clamps `supply_index` to a floor instead of zeroing wiped shares, leaving freed supplier claims redeemable against fresh deposits - (File: contracts/pool/src/interest.rs)

### Summary
The Vim bug class is a use-after-free: a value is released, then still accessed because the guard missed an aliased path (`*`/`+` falling back to register 0). The lending analog lives in bad-debt cleanup: `apply_bad_debt_to_supply_index` writes suppliers down by lowering the supply index, but when the write-down exceeds total supply it clamps the index up to `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing or burning the scaled shares. The wiped suppliers' "freed" claims remain live and can be withdrawn against cash deposited by later suppliers.

### Finding Description
During `clean_bad_debt`, the pool seizes the borrower leg by calling `apply_bad_debt_to_supply_index` and then `burn_debt` [1](#0-0) . When the socialized debt meets or exceeds total supply, the index is clamped up to the floor rather than the residual shares being burned, so `unscale_supply_floor` still returns a positive stranded claim [2](#0-1) . Nothing in the withdraw path distinguishes a stranded claim from an honest one: `resolve_close_or_partial` resolves it to a nonzero gross and `gate_and_debit` admits it once `cash` covers the payout [3](#0-2) . The raw-cache test demonstrates a wiped position withdrawing exactly a fresh depositor's full deposit, leaving the honest supplier undercollateralized [4](#0-3) .

### Impact Explanation
Theft of user funds. After a full bad-debt wipeout (reachable permissionlessly via `clean_bad_debt`), previously wiped suppliers retain a phantom claim proportional to their scaled shares at the floor index. When new suppliers deposit into the emptied market, the stranded holders can withdraw real tokens, directly draining fresh deposits [5](#0-4) . The seized-supply variant shows the same drain when the survivor's shares were not burned [6](#0-5) .

### Likelihood Explanation
Requires a bad-debt wipeout where socialized debt reaches total supply, then new deposits into the market. `clean_bad_debt` is permissionless once dust-threshold conditions hold, and the stranded claim persists indefinitely until exercised. The phantom payout is bounded to roughly `scaled_shares / 1000` unscaled at the floor, capping per-incident theft, which keeps this at Medium.

### Recommendation
On wipeout, burn or zero the stranded scaled supply (or record a write-down flag that forces `resolve_withdrawal` to return zero) instead of clamping `supply_index` up to the floor. Alternatively, gate withdrawals on a market "wiped" marker until the residual shares are reclaimed.

### Proof of Concept
Pin down by the in-repo test `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard`: bad debt of 2× total supply clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`, `unscale_supply_floor` returns a positive stranded claim, a fresh deposit of the same size is made, and `resolve_withdrawal(i128::MAX, scaled_a)` pays out the entire fresh deposit to the wiped holder, leaving `cash` below the honest claim [7](#0-6) .

Caveat I could not fully verify: whether a controller-level guard (e.g., a wiped-market flag checked in `withdraw`) blocks this end-to-end; the pool-side withdraw path itself contains no such guard [3](#0-2) .

### Citations

**File:** contracts/pool/src/ops/seize.rs (L24-28)
```rust
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

**File:** contracts/pool/tests/interest.rs (L452-494)
```rust
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
    });
```

**File:** contracts/pool/src/ops/withdraw.rs (L111-119)
```rust
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
}
```
