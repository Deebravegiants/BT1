### Title
Bad-debt supply-index floor mints unbacked collateral value: wiped suppliers can borrow real cash against residual claims — ([File: contracts/pool/src/interest.rs](contracts/pool/src/interest.rs))

### Summary
Analog of CVE-2019-20202 (`realloc`/free on a block that was never allocated → operating on memory/value that has no backing allocation). In XOXNO Lending, `apply_bad_debt_to_supply_index` socializes bad debt by scaling `supply_index` down, but clamps the result up to `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`) instead of letting it reach zero. When a write-down exceeds total supplied value, survivors' supply shares are left with a residual floored claim whose computed value (`scaled × floor_index`) is real on the books but backed by no cash and no collectible debt — a value "allocation" that was never funded. The controller then values that residual claim at face as borrow collateral.

### Finding Description
`apply_bad_debt_to_supply_index` computes `new_supply_index = old_index × floor(remaining / total)` and then applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))`, so a wipeout (`bad_debt ≥ total_supplied_value`) leaves `supply_index = RAY/1000` rather than 0. [1](#0-0) 

The pool's own unit tests demonstrate the phantom claim concretely: after a wipeout, `unscale_supply_floor(scaled)` returns a positive "stranded" amount that can drain fresh cash absent a guard. [2](#0-1) 

The documented mitigation only gates *new token-funded supply* (`INV-ACCT-04`, `require_backed_market`). But the residual claim still enters risk math: `calculate_ltv_collateral_wad` and the HF path value every supply position as `position_value_floor(position.scaled_amount, market_index.supply_index, price)`, with no per-market backing check. [3](#0-2) 

So after a wipeout, a holder of residual supply shares in market A can call `borrow` on market B (a different, solvent pool book over the same physical balance) using collateral value that the index floor fabricated out of nothing — exactly the "use of a block that was never allocated" shape. The borrowed tokens are real cash; the resulting position is immediately bad debt that will be socialized onto market B's honest suppliers.

Reproduction path (single unprivileged address):
1. Supply into a small market A and into nothing else; wait for an account with outsized debt in A to become insolvent (or engineer it via a price move within bands across the dual-leg oracle).
2. Call `clean_bad_debt(account_id)` — permissionless when `ceil debt > collateral` and collateral ≤ $5 (`INV-LIQ-04`), causing `ops::seize` → `apply_bad_debt_to_supply_index` to clamp A's `supply_index` to `RAY/1000`.
3. With residual `scaled_amount` still on the account, call `borrow` for market B assets. `calculate_ltv_collateral_wad` credits `scaled × RAY/1000 × price_A` of LTV collateral backed by ~zero cash in A.
4. Withdraw B tokens; never repay. The debt is eventually cleaned and socialized onto B's suppliers — theft of user funds.

### Impact Explanation
Theft of user funds / protocol insolvency: the attacker converts an unbacked residual claim into real token withdrawals from unrelated markets; the loss is socialized onto honest suppliers of the borrowed asset. The floor clamp is what creates the free "allocation" — had the index reached zero, the residual shares would be worthless.

### Likelihood Explanation
Requires a market wipeout: bad debt in one market meeting or exceeding that market's total supplied value, then a surviving supply position in that market. Utilization ceilings make this rare in a single liquidation, but accrued interest plus a collateral price crash within sanity bands can produce it on thin markets. Documentation acknowledges the residual-claim state but only addresses supply-side gating, not collateral reuse; likelihood is bounded but the exploit needs no privileged role — `clean_bad_debt`, `borrow`, and `withdraw` are all permissionless.

### Recommendation
When `bad_debt ≥ total_supplied_value`, either zero the index and mark the market as wiped (rejecting its positions from collateral valuation), or have the controller treat a market at `SUPPLY_INDEX_FLOOR_RAW` as contributing zero LTV/threshold collateral in `calculate_ltv_collateral_wad`/`calculate_account_risk_totals` until recapitalization restores backing. Alternatively, gate `borrow`/`withdraw`/`update_account_threshold` on a per-position backing check comparing the leg's floored claim against that market's `cash + debt`.

### Proof of Concept
The mechanism is already exercised by pool unit tests `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` and `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard`, which show the floored index leaving `scaled` shares with a positive claim while `cash == 0`. The missing piece in those tests is only the guard; the controller risk path has none — `calculate_ltv_collateral_wad` consumes `supply_index` directly. End-to-end: supply X units in market A; create and crash a debt account in A; `clean_bad_debt`; observe `supply_index == RAY/1000`, `unscale_supply_floor(scaled) > 0`, `cash ≈ 0`; then `borrow` market B — the residual claim passes `ltv_collateral` and `min_borrow_collateral_usd` checks against phantom value.

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

**File:** contracts/controller/src/risk/totals.rs (L84-97)
```rust
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = position_value_floor(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        let effective_ltv = position.loan_to_value.min(position.liquidation_threshold);
        ltv = ltv.checked_add(env, effective_ltv.apply_to_wad_floor(env, value));
    }
```
