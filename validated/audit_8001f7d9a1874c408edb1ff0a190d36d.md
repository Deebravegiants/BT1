### Title
Bad-debt supply-index floor clamp resurrects wiped-out supplier claims, letting insolvent-market shares drain fresh deposits - (File: contracts/pool/src/interest.rs)

### Summary
The bEarn Fi incident is a share-price/withdrawal-accounting failure: the vault paid out more than shares were truly backed for. The analog in XOXNO Lending is in `apply_bad_debt_to_supply_index` (`contracts/pool/src/interest.rs:73-89`). When socialized bad debt meets or exceeds the total supplied value, every supply share should be worth zero. Instead, the new supply index is clamped up to `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`), leaving every pre-wipeout `scaled_amount` a permanently positive, unbacked claim. Because `withdraw` only enforces `require_reserves` (cash on hand) and `supply`'s `require_backed_market` gate is only checked at deposit entry, a wiped-out holder can wait for fresh deposits and withdraw real tokens against phantom share value — draining other users' funds, exactly the "withdraw pays more than fair share value" shape of the bEarn bug. [1](#0-0) [2](#0-1) 

### Finding Description
`apply_bad_debt_to_supply_index` computes `new_supply_index = supply_index * (total_supplied_value - bad_debt) / total_supplied_value` and then applies `.max(SUPPLY_INDEX_FLOOR_RAW)` (`contracts/pool/src/interest.rs:84-88`). On full wipeout (`bad_debt >= total_supplied_value`), `remaining` is zero, the computed index is zero, and the clamp raises it to `RAY/1000` — a positive index. Suppliers' `scaled_amount` shares are untouched, so `unscale_supply_floor(pos_scaled, RAY/1000)` returns a positive token amount for every pre-wipeout position.

The reachability chain is fully unprivileged: a liquidator calls controller `clean_bad_debt` on an insolvent account → `execute_bad_debt_cleanup` builds `PoolSeizeEntry` items (`contracts/controller/src/positions/liquidation/bad_debt.rs:21-49`) → pool `seize_positions` → `seize::apply` → `interest::apply_bad_debt_to_supply_index` with `bad_debt = unscale_borrow_ceil(position)` (`contracts/pool/src/ops/seize.rs:24-28`). Debt exceeding total supplied value is reachable through interest accrual (borrow index compounds independently of supply index) or price moves between liquidation and cleanup.

After the clamp, withdrawal pays `floor(pos_scaled × RAY/1000)` with no backing check — the repo's own test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` demonstrates the full exploit: clamp leaves a phantom claim, a fresh supplier deposits, the wiped position withdraws, and pool cash can no longer cover the fresh supplier's claim (`contracts/pool/tests/interest.rs:414-426`).

### Impact Explanation
Theft of user funds / protocol insolvency. The clamp mints aggregate unbacked claims worth `~supplied_shares × RAY/1000` — roughly 0.1% of the pre-wipeout supply face value — payable out of any future cash. Any subsequent depositor (via controller `supply`) provides the liquidity that the phantom claims withdraw first. On a large market this residual is material, and the theft is fully permissionless: the attacker only needs a pre-existing (or newly created before cleanup) supply position in the market, plus the ability to trigger or wait for `clean_bad_debt`.

### Likelihood Explanation
Requires a market to reach full-wipeout bad debt (debt ≥ total supplied value at cleanup), which is a tail event but is precisely the scenario bad-debt socialization exists for — deep undercollateralization plus stalled liquidations or fast price crashes. Once the clamp binds, no further precondition exists: the phantom claim is passive and withdrawable by any holder of the old shares whenever new cash arrives. No privileged role, oracle manipulation, or upgrade is needed.

### Recommendation
When `remaining == Ray::ZERO` (or when the clamp would bind), zero out the market's claims instead of flooring the index: e.g., set `supply_index` such that claims are truly worthless by also resetting `supplied`/`revenue` scaled totals to zero (or snapshot-and-zero shares), rather than reviving the index to `RAY/1000`. At minimum, gate `withdraw`/`resolve_withdrawal` on `backing_shortfall` when `supply_index == SUPPLY_INDEX_FLOOR_RAW`, and reconcile the `revenue`/`supplied` totals so no scaled supply outlives a complete write-down.

### Proof of Concept
1. Market M has supplier A holding `S` scaled shares and borrower B with debt that grows (accrual/price move) until `unscale_borrow_ceil(B_debt) >= supplied × supply_index`.
2. Attacker (or keeper) calls controller `clean_bad_debt(B_account)`; `seize::apply` socializes the debt → `supply_index` clamps to `RAY/1000` instead of 0.
3. A fresh depositor C calls `supply(amount)`; `require_backed_market` passes because it measures the shortfall of stored totals, not the phantom-claim liability at the floored index.
4. Holder of old shares (A, or the attacker who supplied before step 2) calls `withdraw(0)` → `resolve_withdrawal` returns `floor(S × RAY/1000) > 0` → `require_reserves` passes against C's cash → tokens transfer out. C's claim is now unbacked: `cash < floor(C_scaled × supply_index)`.

This is exactly the scenario encoded in `contracts/pool/tests/interest.rs:372-427`, which asserts `gross == fresh_cash` and `cache.cash() < fresh_claim` — "S_old drains exactly the fresh deposit".

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
