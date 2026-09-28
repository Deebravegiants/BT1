### Title
Bad-debt write-down clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing wiped claims, leaving dangling supply shares that drain future depositors - (File: contracts/pool/src/interest.rs)

### Summary
The OpenSSL bug class is a cleanup path that frees an object while the caller retains a live pointer to it (a dangling reference usable after free). The on-chain analog is `apply_bad_debt_to_supply_index`: when bad debt equals or exceeds total supplied value, the write-down "frees" all backing for supply shares but, instead of zeroing them, clamps `supply_index` up to `SUPPLY_INDEX_FLOOR_RAW = RAY/1000`. Every pre-wipeout supply share therefore retains a positive, withdrawable claim backed by nothing — a dangling claim. Once any new liquidity enters the market, those stranded claims withdraw real cash and directly take it from fresh suppliers.

### Finding Description
`apply_bad_debt_to_supply_index` caps `bad_debt` at `total_supplied_value`, computes `remaining = total_supplied_value - capped`, and sets `new_supply_index = supply_index * remaining / total_supplied_value`, then applies `.max(SUPPLY_INDEX_FLOOR_RAW)` [1](#0-0) . On a full wipeout (`bad_debt >= total_supplied_value`), `remaining = 0`, so the index should be 0 — every share's claim is gone — but the clamp raises it to `RAY/1000` [2](#0-1) . Share balances (`supplied` and per-position `scaled_amount`) are untouched, so each share keeps a claim of `scaled * RAY/1000` — 0.1% of pre-wipeout value — against a pool with no cash.

Withdrawals value claims via `resolve_withdrawal`/`unscale_supply_floor` against the live index and are gated only by `require_reserves` against actual `cash` [3](#0-2) . The pool's own test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` demonstrates the full shape: after the clamp, an old scaled position's `unscale_supply_floor` is still positive, a fresh deposit of that amount is credited to a new supplier, and the old position withdraws exactly the fresh deposit, leaving the new supplier's claim unbacked [4](#0-3) .

The path is reachable permissionlessly: `liquidate` ends with `check_bad_debt_after_liquidation`, and `clean_bad_debt` admits any caller once `total_debt > total_collateral` and collateral ≤ $5 [5](#0-4) [6](#0-5) . Cleanup writes each debt market's remaining debt off against that market's supply index via `execute_bad_debt_cleanup` → the pool seize/write-down path [7](#0-6) .

### Impact Explanation
Theft of user funds / protocol insolvency: suppliers whose claims were economically wiped by socialized bad debt retain 0.1%-of-face-value claims with zero backing. The first ~0.1%-of-old-TVL of new deposits into the affected market is withdrawable by old share holders (including an attacker holding shares through the wipeout), so new suppliers' principal is stolen and the pool's cash cannot cover their claims — exactly the pool-insolvency outcome the clamp tries to avoid, deferred onto the next depositor.

### Likelihood Explanation
Medium. Requirements: a market where total debt approaches total supplied value (near-100% utilization, achievable where `max_utilization` is ≥1 RAY or after long interest accrual on a fully-borrowed market), an insolvent account whose collateral is ≤ $5 (a borrower at max LTV whose debt crosses collateral purely by accrual, or by an allowed in-bands price move — attacker-controlled timing), then any unprivileged `clean_bad_debt` or a dust-finishing `liquidate`. The attacker's cost is forfeiting a dust-sized collateral position; the profit is bounded by ~0.1% of pre-wipeout supply value plus the defaulted borrowed principal. It then needs one subsequent deposit in that market to realize the drain — plausible since the market stays listed.

### Recommendation
On full wipeout, burn/zero the outstanding `supplied` shares (or reset them pro-rata) instead of clamping the index: when `capped == total_supplied_value`, set `supplied` (and position-level scaled amounts) to zero alongside the index, or store a wiped flag that makes `resolve_withdrawal`/`unscale_supply_floor` return 0 for shares minted before the write-down. Alternatively, clamp the index but reduce total `supplied` shares by the same `remaining` fraction so phantom value cannot accumulate.

### Proof of Concept
1. Market M: attacker and others supply `S` tokens; utilization is driven to ~100% (attacker borrows `B ≈ S` against collateral in market C, sized so collateral is worth ≤ $5 after accrual, or an account naturally reaches this).
2. Interest accrual pushes the account's `total_debt > total_collateral` with `total_collateral ≤ 5 WAD`; the attacker calls `controller.clean_bad_debt(caller, account_id)`.
3. `execute_bad_debt_cleanup` calls the pool write-down for market M with `bad_debt = remaining_debt ≥ total_supplied_value`. `remaining = 0`, but `supply_index` becomes `RAY/1000` while all `scaled_amount` shares persist.
4. A new supplier deposits `D` into market M (`supply` mints shares at the floored index and credits real cash).
5. Any holder of pre-wipeout shares calls `withdraw` for `min(unscale_supply_floor(shares, RAY/1000), cash)`; `require_reserves` passes against the fresh cash `D`, transferring tokens for shares that the write-down had already declared worthless — `D` is drained from the new supplier.

The unit test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` already exercises steps 3–5 at cache level, asserting `gross == fresh_cash` and that pool cash can no longer cover the fresh supplier's claim [8](#0-7) .

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

**File:** common/src/constants/pool.rs (L6-9)
```rust
/// Minimum value the supply index is clamped to when bad debt is written down against
/// suppliers, in raw ray units. Interest accrual does not apply this floor; it only guarantees
/// the index never decreases.
pub const SUPPLY_INDEX_FLOOR_RAW: i128 = RAY / 1_000;
```

**File:** contracts/pool/src/cache/scale.rs (L60-67)
```rust
    pub(crate) fn unscale_supply_floor(&self, scaled: Ray) -> i128 {
        unscale_supply_floor(
            &self.env,
            scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }
```

**File:** contracts/pool/tests/interest.rs (L388-426)
```rust
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
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L300-316)
```rust
/// Removes empty accounts or socializes insolvent debt under the collateral dust cap.
pub(crate) fn check_bad_debt_after_liquidation(
    env: &Env,
    cache: &mut Context,
    account_id: u64,
    account: &Account,
    totals: &AccountRiskTotals,
) {
    if account.borrow_positions.is_empty() {
        account::cleanup_account_if_empty(env, account, account_id);
        return;
    }

    if is_socializable_bad_debt(totals.total_debt, totals.total_collateral) {
        bad_debt::execute_bad_debt_cleanup(env, cache, account_id, account, totals);
    }
}
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L212-237)
```rust
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
```
