### Title
Bad-debt write-down clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing wiped positions, leaving unbacked residual claims that drain any future pool cash - (`contracts/pool/src/interest.rs`)

### Summary
The analog to CVE-2017-15238 (a use-after-free triggered when a dimension is zero) is a "claim-after-wipeout": when bad debt equals or exceeds the total supplied value of a market, `apply_bad_debt_to_supply_index` does not zero the supply index or burn the now-worthless supply shares — it clamps the index up to `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`). Every wiped supply position keeps a residual claim of roughly 1/1000 of its original share value. Those shares were economically destroyed by the socialization, yet they remain withdrawable against any cash that later enters the market.

### Finding Description
In `contracts/pool/src/interest.rs:73-89`, `apply_bad_debt_to_supply_index` computes `remaining = total_supplied_value - min(bad_debt, total_supplied_value)`. When `bad_debt >= total_supplied_value`, `remaining` is zero, so the proportional write-down is zero — but the result is clamped: [1](#0-0) 

A holder of `S` scaled shares therefore retains `floor(S * RAY/1000 / RAY)` ≈ `S/1000` RAY of claim despite a 100% loss. The pool's own tests demonstrate the consequence: `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` and `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard` show a wiped position paying out real tokens and "drain[ing] exactly the fresh deposit" [2](#0-1) , and the certora rule `seize_floor_residual_reachable` proves the state (`borrowed == 0 && cash == 0 && supply_index == FLOOR && legacy_claim > 0`) is reachable via a production `seize_positions` call [3](#0-2) .

Cash can re-enter the wiped market through paths that do not check `require_backed_market`: permissionless `recapitalize` (credits cash up to the shortfall, mints no shares), `repay`/`credit_cash` on any residual or new debt, and `supply` once the floored shortfall rounds to zero in token units (as in `test_bad_debt_wipeout_leaves_market_usable_at_realistic_scale`, where post-wipeout supply succeeds at realistic scale [4](#0-3) ). The wiped holder then calls `withdraw` via the controller; `resolve_withdrawal` + `require_reserves` happily pay out the residual claim against the fresh cash.

### Impact Explanation
Theft of user funds / protocol insolvency. Whoever recapitalizes or newly supplies a fully-written-down market has their cash immediately claimable by legacy "freed" positions — the holders (or the protocol's own revenue shares, which are also clamped rather than zeroed) withdraw value that was already socialized away. This is value paid twice: once written off against suppliers, once paid out again in tokens.

### Likelihood Explanation
Reaching the floor requires a single liquidation/cleanup whose bad debt exceeds the market's total supplied value. `require_utilization_below_max` normally caps borrow draws at 95% of supply, so one liquidation alone lands far from the floor [5](#0-4) ; however a sharp price crash between accruals, repeated cleanups, or a market left with only dust supply after partial exits can push the write-down to the cap. `clean_bad_debt` is permissionless when collateral ≤ $5, and dust-sized markets make the floor cheap to reach. The residual-drain step needs only ordinary `withdraw` — fully unprivileged.

### Recommendation
When `bad_debt >= total_supplied_value` (or whenever `proportional < SUPPLY_INDEX_FLOOR_RAW`), burn or fence the residual: either set `supply_index` to a sentinel that makes `unscale_supply_floor` return zero for pre-wipeout shares (e.g., epoch-stamping positions), or cap each withdrawal's `resolve_withdrawal` payout at the market's post-write-down backing share pro-rata. At minimum, block `withdraw`/`claim_revenue` payouts on claims that predate a floor-clamped write-down until `backing_shortfall == 0`, and make `recapitalize`'s refund semantics explicit that funds cover legacy claims.

### Proof of Concept
1. Alice supplies `S` units of token T to market M; Bob supplies the rest. Dave borrows against M up to the utilization cap.
2. Price crash makes Dave's account eligible for `clean_bad_debt` (or a liquidation) with bad debt ≥ M's total supplied value. Anyone calls the controller cleanup; `seize_positions` → `apply_bad_debt_to_supply_index` clamps `supply_index` to `RAY/1000` while `supplied` shares are unchanged (`seize_floor_residual_reachable` witness).
3. A third party calls `recapitalize(M, amount)` (permissionless; fills the floored shortfall and mints no shares) or a fresh `supply` sneaks in once the floored shortfall rounds to zero — cash now sits in M.
4. Alice calls `controller.withdraw` on her wiped position. `resolve_withdrawal` pays `floor(S_scaled * FLOOR)` from the fresh cash; `burn_supply` removes her shares, but the tokens paid exceed her fair (zero) share — the recapitalizer's/new supplier's funds are stolen. The unit tests reproduce exactly this in-cache: stranded claim > 0, fresh `credit_cash`, then `resolve_withdrawal(i128::MAX, scaled)` pays `gross == fresh_cash` leaving `cash < fresh_claim` [6](#0-5) .

### Citations

**File:** contracts/pool/src/interest.rs (L80-89)
```rust
    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
}
```

**File:** contracts/pool/tests/interest.rs (L395-427)
```rust
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

**File:** certora/pool/spec/core_sanity_rules.rs (L136-159)
```rust
fn seize_floor_residual_reachable(e: Env, admin: Address, asset: Address) {
    cvlr_assume!(e.ledger().timestamp() <= u64::MAX / 1_000);
    seed(
        &e,
        admin,
        asset.clone(),
        params(asset.clone(), 0, false),
        state(100 * RAY, 100 * RAY, 0, RAY, RAY, 0, e.ledger().timestamp()),
    );
    let seized = PoolSeizeEntry {
        hub_asset: hub(asset.clone()),
        side: AccountPositionType::Borrow,
        position: position(100 * RAY),
    };
    crate::ops::seize::apply(&e, &seized);
    let post = read_state(&e, &asset);
    let legacy_claim = Ray::from(post.supplied).mul_floor(&e, Ray::from(post.supply_index));

    cvlr_satisfy!(
        post.borrowed == 0
            && post.cash == 0
            && post.supply_index == SUPPLY_INDEX_FLOOR_RAW
            && legacy_claim.raw() > 0
    );
```

**File:** contracts/pool/tests/flows.rs (L3135-3154)
```rust
fn test_bad_debt_wipeout_leaves_market_usable_at_realistic_scale() {
    let t = TestSetup::new();
    let client = t.client();

    client.supply(&t.sup(0, 10_000_000_000i128));

    t.env.as_contract(&t.pool, || {
        let mut cache = Cache::load(&t.env, &hub(&t.asset));
        let total_supplied_value = cache.supplied().mul(&t.env, cache.supply_index());
        crate::interest::apply_bad_debt_to_supply_index(&mut cache, total_supplied_value);
        cache.commit();
    });

    let floored = t.state_snapshot().supply_index;
    assert_eq!(floored, common::constants::SUPPLY_INDEX_FLOOR_RAW);
    assert_eq!(RAY / floored, 1_000);

    let opened = client.supply(&t.sup(0, 10_000_000_000_000i128));
    assert!(opened.get(0).unwrap().position.scaled_amount > 0);
}
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L640-675)
```rust
/// Pool `ops::seize` commits with no `guards::` assertion. After a large
/// socialization the market stays backed (`require_backed_market` admits new
/// supply) and still holds supply against its debt (the INV-ACCT-09 shape).
///
/// The `SUPPLY_INDEX_FLOOR_RAW` clamp in `apply_bad_debt_to_supply_index` makes
/// a wipeout partial (INV-LIQ-04). `require_utilization_below_max` caps debt at
/// 95% of supply value, so one liquidation cannot drive the index near the floor.
#[test]
fn test_socialization_leaves_the_market_backed_and_open() {
    let mut t = setup();

    // Alice borrows half the ETH supply, so one liquidation makes a large write-down.
    t.supply(BOB, "ETH", 0.01);
    t.supply(ALICE, "USDC", 100.0);
    t.borrow(ALICE, "ETH", 0.005);

    let eth_before = market_state(&t, "ETH");

    t.set_price("USDC", usd_cents(1));
    t.liquidate(LIQUIDATOR, ALICE, "ETH", 0.001);

    let eth_after = market_state(&t, "ETH");
    let (si_after, _) = get_indexes(&t, "ETH");

    assert!(
        si_after < eth_before.supply_index,
        "fixture must actually socialize: before={} after={si_after}",
        eth_before.supply_index
    );

    // The utilization ceiling keeps one liquidation far from the index floor.
    assert!(
        si_after > controller::constants::SUPPLY_INDEX_FLOOR_RAW * 100,
        "one liquidation should not approach the index floor: si={si_after} floor={}",
        controller::constants::SUPPLY_INDEX_FLOOR_RAW
    );
```
