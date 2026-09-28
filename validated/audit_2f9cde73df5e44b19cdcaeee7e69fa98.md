### Title
Bad-debt wipeout clamps `supply_index` up to `SUPPLY_INDEX_FLOOR_RAW`, leaving wiped suppliers with phantom claims that drain future deposits - (File: contracts/pool/src/interest.rs)

### Summary
When `apply_bad_debt_to_supply_index` socializes bad debt equal to or exceeding the market's entire supplied value, the computed index collapses to zero but is then clamped **up** to `SUPPLY_INDEX_FLOOR_RAW = RAY/1000`. Every pre-existing supply share thereby retains a claim worth `scaled × RAY/1000`, even though the book was fully written down. Any later deposit into the market is withdrawable by those wiped positions, letting an unprivileged holder of stranded shares steal fresh suppliers' funds.

### Finding Description
`apply_bad_debt_to_supply_index` computes `remaining = total_supplied_value − min(bad_debt, total_supplied_value)` and `new_index = supply_index × remaining / total_supplied_value`, then applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))` [1](#0-0) . When `bad_debt ≥ total_supplied_value`, `remaining = 0`, so `new_index` computes to `0` and the floor clamp raises it to `RAY/1000` — a strictly positive index attached to shares whose backing was declared zero. No guard zeroes the `supplied` share total or blocks withdrawals against the floored index.

The pool's own test suite demonstrates the consequence: after a wipeout clamp, `unscale_supply_floor(old_scaled) > 0` ("floor clamp leaves userA a phantom claim"), a fresh deposit mints honest shares, and `resolve_withdrawal(i128::MAX, old_scaled)` pays `gross == fresh_cash` — the stranded position "drains exactly the fresh deposit out of the pool" and `cash < fresh_claim` [2](#0-1) . The same accounting is exercised at `contracts/pool/tests/interest.rs:316-369`.

The entry path is reachable by an unprivileged address: debt write-down is driven by `seize::apply` on `AccountPositionType::Borrow` legs during `liquidate`/`clean_bad_debt` [3](#0-2) , and permissionless `clean_bad_debt` admits any insolvent account with collateral ≤ $5 via `BadDebtGate::DustCapped` [4](#0-3) . An attacker controls their own insolvency (borrow max, let the position go under) and the attacker need not even be the one holding stranded shares — every wiped supplier holds them.

### Impact Explanation
Theft of user funds and protocol insolvency. Stranded (economically wiped) supply shares keep a positive floor-indexed claim. The first deposits into the market after the clamp are paid out to old share withdrawals, so new suppliers lose their principal to prior suppliers — a direct transfer of funds that the write-down was supposed to have destroyed. The book is also permanently insolvent: `supplied × floor_index` claims exceed `cash` by construction, so the market cannot honor all claims.

### Likelihood Explanation
Triggering requires a market where a single insolvent account's ceiled debt value (`bad_debt`, computed via `unscale_borrow_ceil_ray`) meets or exceeds `supplied × supply_index`. Because the borrow index grows strictly faster than the supply index (reserve factor skims interest), debt that once matched its funding grows past it over time, so sustained delinquency on a concentrated market reaches the wipeout bound. `clean_bad_debt` is callable by anyone once the account's collateral is dust — precisely the case when the debt is huge relative to collateral — and the attacker can engineer this with their own account at negligible cost. No privileged role, oracle manipulation, or timing race is needed.

### Recommendation
Do not clamp a wiped-out index upward to a nonzero floor while `supplied` shares remain outstanding. Either (a) when `capped == total_supplied_value`, zero the `supplied` share total alongside setting the index (burning all claims, possibly crediting a residual distribution), or (b) allow the index to reach a value that makes all claims zero and gate new deposits/restarts on `supplied == 0`. Additionally, reject or reset `supplied` when the clamp engages, and have `recapitalize`/`supply` treat a floor-indexed market with nonzero `supplied` as requiring explicit re-initialization rather than silently inheriting phantom claims.

### Proof of Concept
The in-tree test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:372-428`) is an executable PoC on the production `Cache`/`apply_bad_debt_to_supply_index` code path:

1. Market holds `supplied = 1_000 RAY` shares at `supply_index = RAY` (userA's position).
2. `apply_bad_debt_to_supply_index(cache, 5_000 RAY)` — a bad-debt write-down exceeding total supplied value, reachable through `clean_bad_debt` on an insolvent dust-collateral account.
3. Assert `supply_index == SUPPLY_INDEX_FLOOR_RAW` — wiped book clamped *up* to a positive index.
4. `unscale_supply_floor(1_000 RAY) > 0` — userA retains a phantom claim with zero backing.
5. userB supplies `c = stranded` tokens (`mint_supply`, `credit_cash`); `unscale_supply_floor(scaled_b) == c`.
6. userA calls `withdraw` (resolves to `resolve_withdrawal(i128::MAX, scaled_a)`); `gross == c` — userA drains exactly userB's deposit, `cash` ends at `0 < fresh_claim`.

Same pattern at `contracts/pool/tests/interest.rs:317-369` (`test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard`), and `contracts/pool/tests/flows.rs:3134-3154` confirms the floored market still accepts new supply end-to-end.

### Citations

**File:** contracts/pool/src/interest.rs (L80-88)
```rust
    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
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

**File:** contracts/pool/src/ops/seize.rs (L24-28)
```rust
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-243)
```rust
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
