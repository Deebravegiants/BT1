### Title
Stable-LP collateral price is manipulable within its sanity band via a single unprivileged swap, enabling unfair liquidation of LP-backed borrowers - (File: common/src/oracle/lp_stable.rs)

### Summary
The analog of the dForce `get_virtual_price` manipulation is the `AquariusStableLp` price source. `fair_stable_lp_price_wad` prices an LP share as `D * min(price_a, price_b) / total_shares`, where `D` is solved from the pool's **live reserves** (`solve_stable_d`). For a StableSwap invariant, `D` is maximized when the pool is balanced and falls strictly as reserves are skewed. An attacker can skew the pool with one large swap (flash-funded), drop the derived LP price toward `min_sanity_price_wad`, and call `liquidate` in the same transaction, because seizure converts USD to collateral units by dividing by the manipulated `feed.price`.

Unlike the Curve bug, no reentrancy is needed — Soroban blocks reentry anyway — because the manipulation is done by a plain Aquarius trade *before* the liquidation call, which the prompt explicitly allows ("own trades on Aquarius/Soroswap").

### Finding Description
- `common/src/oracle/lp_stable.rs:80-109`: `fair_stable_lp_price_wad` computes `D` from `reserve_a`/`reserve_b` and multiplies by `min_price`. `D` is a decreasing function of reserve imbalance; `min_price` does not correct for imbalance — a 90/10 skew collapses `D` even though both leg prices are still honest external feeds. [1](#0-0) 
- `solve_stable_d` (same file, lines 30-69) solves the invariant on the spot reserves with no smoothing, no TWAP, and no balance-ratio check.
- `contracts/price-aggregator/src/providers/aquarius.rs:88-114`: `read` fetches `aquarius_pool_reserves_call` and `aquarius_total_shares_call` at call time and feeds them directly into `fair_stable_lp_price_wad`. [2](#0-1) 
- `admin.rs:181-197`: LP oracles are forced single-source (`has_lp && sources.len() != 1` reverts) and tolerance validation is waived for them — the only bound is the sanity band. [3](#0-2) 
- Deployed bands are wide enough to matter: `PYUSDUSDC_LP` (stable) has `[0.9, 1.2]` WAD (~25% deflation headroom) and `USTRYUSDC_LP`/`USDYUSDC_LP` have `[1.74, 2.44]`/`[1.79, 2.51]` (~29-29%). [4](#0-3) 
- `contracts/controller/src/positions/liquidation/math.rs:398`: `seizure_amount_wad = seizure_usd / feed.price` — a depressed `feed.price` inflates the number of LP units seized for a given repayment. Combined with the bonus (`total_seizure_usd = repay_usd * (1+b)`), the liquidator receives collateral worth materially more than `repay * (1+b)` at the true price. [5](#0-4) 

The constant-product variant `fair_lp_price_wad` (`2*sqrt(va*vb)/supply`) is largely skew-immune because swaps preserve `reserve_a * reserve_b`; the stable variant is not — `D` is not swap-invariant under imbalance.

### Impact Explanation
Theft of user funds. Every account holding an `AquariusStableLp` token as collateral with `HF` between 1.0 and ~`1/deflation` becomes liquidatable at a manipulated price; the liquidator seizes `repay*(1+b)/p_manipulated` units instead of `repay*(1+b)/p_true`, extracting the difference (up to ~25-29% of seized value on configured bands) directly from the victim. If pushed past `min_sanity_price_wad` the read fails closed instead, so the attacker sizes the skew to stay just inside the band.

### Likelihood Explanation
Medium. Requires (a) stable-LP collateral positions with modest HF margin, (b) pool liquidity shallow enough to skew `D` by the needed amount — Aquarius stable pools are small relative to Curve, so skew cost is low — and (c) skew capital, obtainable via the pool's own `flash_loan` on any flashloanable asset or `flash_position`. Round-trip un-skewing recovers most of the manipulation capital; net cost is swap slippage/fees. No privileged role, leaked key, or reentrancy is needed; a single EOA submits `aquarius.swap` → `controller.liquidate` → `aquarius.swap` in one transaction.

### Recommendation
Add an imbalance guard to the stable-LP path: reject or clamp when `min(xa_wad, xb_wad) / max(xa_wad, xb_wad)` falls below a configured ratio, or price the share as `min(D-based fair value, naive_reserve_sum_value)` / use a conservative lower bound such as `2 * min(xa, xb) * min_price` which is far less sensitive to skew. Alternatively require a second independent source for stable-LP oracles so the dual-source tolerance check applies, and tighten `min_sanity_price_wad` for stable-LP markets (a stable pair's fair price should not admit a 25% band).

### Proof of Concept
1. Attacker EOA calls `pool.flash_loan` (or `controller.flash_position`) for token A in the Aquarius stable pool backing listed collateral `S_LP`.
2. In the same tx, attacker executes `aquarius_router.swap(A → B)` sized to push the pool to ~85-95% imbalance; `solve_stable_d` now yields `D' < D`, so `read` returns `price_wad' = D' * min_price / shares`, above `min_sanity_price_wad` but e.g. 20% below fair.
3. Attacker calls `controller.liquidate(liquidator, victim_account_id, payments, SeizeMode::Transfer)` on a victim whose only collateral is `S_LP` and whose `HF ∈ [1, ~1.25]`; `calculate_seized_collateral` divides `seizure_usd` by `price_wad'` (math.rs:398), transferring ~25% more LP units to the attacker than fair.
4. Attacker swaps B → A on Aquarius to restore balance, repays the flash loan, and holds victim LP shares redeemable for their full (restored) value — net profit equals the over-seized units minus swap fees.

### Citations

**File:** common/src/oracle/lp_stable.rs (L96-109)
```rust
    let xa_wad = try_amount_to_wad(env, a.reserve, a.decimals)?;
    let xb_wad = try_amount_to_wad(env, b.reserve, b.decimals)?;
    let d = solve_stable_d(env, xa_wad, xb_wad, amp)?;

    let min_price = a.price_wad.min(b.price_wad);
    let share_supply_wad = try_amount_to_wad(env, supply.total_shares, supply.decimals)?;
    if share_supply_wad <= 0 {
        return Err(OracleError::InvalidPrice);
    }

    let fair = d
        .mul(&U256::from_u128(env, min_price as u128))
        .div(&U256::from_u128(env, share_supply_wad as u128));
    try_u256_to_i128(&fair).ok_or(OracleError::InvalidPrice)
```

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L88-114)
```rust
    let price_a = engine::resolve_nested(session, &lp.key_a, depth + 1)?;
    let price_b = engine::resolve_nested(session, &lp.key_b, depth + 1)?;
    let (reserve_a, reserve_b) =
        aquarius_pool_reserves_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
    let total_shares =
        aquarius_total_shares_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;

    let leg_a = LpLeg {
        reserve: reserve_a,
        decimals: lp.reserve_a_decimals,
        price_wad: price_a.price_wad,
    };
    let leg_b = LpLeg {
        reserve: reserve_b,
        decimals: lp.reserve_b_decimals,
        price_wad: price_b.price_wad,
    };
    let supply = LpSupply {
        total_shares,
        decimals: share_decimals,
    };
    let price_wad = if stable {
        let amp = aquarius_amp_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
        fair_stable_lp_price_wad(&env, &leg_a, &leg_b, &supply, amp)?
    } else {
        fair_lp_price_wad(&env, &leg_a, &leg_b, &supply)?
    };
```

**File:** contracts/price-aggregator/src/admin.rs (L181-197)
```rust
    let has_lp = oracle.sources.iter().any(|source| source.is_aquarius_lp());
    if has_lp && oracle.sources.len() != 1 {
        panic_with_error!(env, OracleError::SourceCountOutOfRange);
    }

    validation::composition_depth(env, &derived.first);
    if let Some(second) = derived.second.as_ref() {
        validation::composition_depth(env, second);
    }
    validation::staleness_envelope(env, oracle.max_price_stale_seconds, &derived.combined());
    if !oracle.has_aquarius_lp_source() {
        validation::smoothing(env, &derived.first, derived.second.as_ref());
    }

    if !oracle.has_aquarius_lp_source() {
        validate_oracle_tolerance(env, &oracle.tolerance);
    }
```

**File:** configs/mainnet/markets.json (L1552-1558)
```json
        "tolerance": {
          "upper_ratio_bps": 0,
          "lower_ratio_bps": 0
        },
        "independence": "RequireDisjoint",
        "min_sanity_price_wad": "900000000000000000",
        "max_sanity_price_wad": "1200000000000000000"
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L395-399)
```rust
        let share = asset_value.div(env, total_collateral);
        let seizure_for_asset_usd = total_seizure_usd.mul(env, share);

        let seizure_amount_wad = seizure_for_asset_usd.div(env, feed.price);
        let mut seizure_ray = seizure_amount_wad.to_ray(env);
```
