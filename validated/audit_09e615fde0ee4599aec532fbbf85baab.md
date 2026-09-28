### Title
Bad-debt write-down clamps the supply index up to `SUPPLY_INDEX_FLOOR_RAW`, resurrecting phantom supplier claims that drain any later cash entering a wiped market - (File: contracts/pool/src/interest.rs)

### Summary
When `apply_bad_debt_to_supply_index` socializes a loss that equals or exceeds the market's total supplied value, the mathematically correct new supply index is at or near zero. Instead the result is clamped **up** to `SUPPLY_INDEX_FLOOR_RAW = RAY/1000`, which re-inflates every wiped-out supply share to a nonzero claim. Those shares are never burned, so they form a phantom liability against the market that is paid out of any subsequent cash credit (flash-loan fees, liquidation proceeds, `recapitalize` injections). The codebase's own regression test proves a stranded claim drains a fresh deposit end-to-end.

### Finding Description
`apply_bad_debt_to_supply_index` computes the write-down factor and then applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))`: [1](#0-0) 

When `bad_debt >= total_supplied_value`, `reduction_factor` is 0 and the correct index is 0 — all suppliers are wiped. The floor instead sets `supply_index = RAY/1000`, so every surviving share keeps a claim of `shares * RAY/1000` in underlying value. Nothing burns `supplied`; the shares persist.

This is reachable permissionlessly via the seize path used by `clean_bad_debt`/`force_socialize_bad_debt`/post-liquidation cleanup: `seize::apply` unscales the debt position and calls `apply_bad_debt_to_supply_index`: [2](#0-1) 

and `clean_bad_debt` is an unprivileged entrypoint gated only on insolvency plus collateral below the dust cap: [3](#0-2) 

After the wipe, the market's books are insolvent: `supplied_claim(floor) = supplied * RAY/1000 > 0` while `cash + debt = ~0`, so `backing_shortfall` is positive and `require_backed_market` blocks new `supply`: [4](#0-3) 

However, cash can still enter without that guard:
- `recapitalize` credits `min(amount, backing_shortfall)` to cash permissionlessly — and the shortfall it pays is *entirely phantom* (there is no real debt anymore): [5](#0-4) 
- Flash-loan fees, liquidation fee settlements, and seized-collateral realizations credit cash/revenue into the same market on later operations.
- Holders of the stranded shares then withdraw ahead of the protocol's `claim_revenue`, because withdrawal is first-come-first-served against `cash` with only the `require_reserves` liquidity check — there is no check that the claim corresponds to a pre-wipe real deposit.

The project's own test demonstrates the drain mechanism exactly — a stranded post-wipe claim pays out real cash from a subsequent deposit, leaving the fresh depositor unbacked: [6](#0-5) 

(The test's guard caveat only covers the `supply` path; `recapitalize` and fee/revenue cash credits bypass `require_backed_market` by design.)

### Impact Explanation
Theft of user funds / permanent misallocation of protocol cash. Any token that later lands in a wiped market's `cash` — a recapitalizer's injection, a flash-loan fee, liquidation-settled proceeds — is claimable pro-rata by phantom shares that should have been worth zero. The market also remains permanently "insolvent" per `backing_shortfall` until someone pays off the phantom claims, so honest recapitalizers pay ~0.1% of the wiped notional into dead claims before the market can reopen. For large wiped markets this is a material, attacker-harvestable sum: an attacker who dominates supply of a thin market, borrows it heavily against collateral, lets the position go insolvent (price moves are an ordinary market condition, not oracle manipulation), and calls `clean_bad_debt` ends up holding the majority of the resurrected floor claims and captures most of every subsequent cash credit.

### Likelihood Explanation
Requires a near-total wipeout on one `(hub, token)` book: outstanding debt value ≥ total supplied value, with the position's remaining collateral at/below the dust threshold for the permissionless path (or owner/admin cooperation for `force_socialize_bad_debt`). This is most feasible on thin, high-utilization markets where accrued debt can approach or exceed supply value, or after a collateral crash. No privileged role is needed for `clean_bad_debt` or `recapitalize`, and the attacker can hold the dominant share of the stranded claims. Likelihood is moderate: it needs a real insolvency event plus subsequent cash inflow, but the payout is automatic once both occur.

### Recommendation
Do not floor the write-down at `SUPPLY_INDEX_FLOOR_RAW` in a way that *raises* the index. Options:
- When `reduction_factor` computes to below the floor (i.e., `capped == total_supplied_value`), burn the remaining `supplied`/`revenue` shares alongside the index write-down so no phantom claims survive — a full wipeout should zero out share balances, not just the index.
- Alternatively, track a "wiped" flag: set `supply_index = 0` semantics by zeroing `supplied` and `revenue`, keeping a nonzero index only to preserve share-minting math for future deposits.
- At minimum, exclude the phantom residual from `backing_shortfall` so `recapitalize` does not pay dead claims, and block `withdraw` of supply shares when the committed index equals the floor after a full wipeout.

### Proof of Concept
1. Market (hub H, token T): attacker supplies S of T (dominant share, possibly via multiple accounts), other suppliers add more; utilization is high.
2. Attacker borrows nearly all of T's cash against collateral C on a separate account.
3. C's price drops (market movement), leaving the account insolvent with collateral ≤ dust threshold.
4. Attacker calls `controller.clean_bad_debt(caller, account_id)`. Seize path: `unscale_borrow_ceil` ≈ full debt → `apply_bad_debt_to_supply_index` computes `reduction_factor = 0` → index is clamped **up** to `RAY/1000`; `supplied` shares are untouched.
5. Result: `supplied_claim = supplied * RAY/1000 > 0`, `cash ≈ 0`, `borrowed = 0` → `backing_shortfall > 0`.
6. Any later cash credit — e.g., a third party calling `controller.recapitalize(payer, hub_asset, amount)` (applied = the full phantom shortfall), or a flash-loan/liquidation fee settling in T — raises `cash`.
7. Attacker calls `controller.withdraw` on their stranded supply positions; `require_reserves` passes and the phantom claim is paid in real tokens, ahead of `claim_revenue` or the recapitalizer's intent. The recap payer / fee payer's funds are diverted to claims that should have been zero, matching the mechanism proven in `contracts/pool/tests/interest.rs::test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard`.

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

**File:** contracts/pool/src/ops/seize.rs (L23-34)
```rust
    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
        AccountPositionType::Deposit => {
            cache.absorb_supply_as_revenue(position);
        }
    }

    cache.commit()
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

**File:** contracts/pool/src/guards.rs (L52-66)
```rust
pub(crate) fn require_backed_market(env: &Env, cache: &Cache) {
    assert_with_error!(
        env,
        backing_shortfall(cache) == 0,
        CollateralError::PoolInsolvent
    );
}

/// Asset units by which supplier claims exceed cash + debt (0 if solvent).
pub(crate) fn backing_shortfall(cache: &Cache) -> i128 {
    let supplied_claim = cache.unscale_supply_floor(cache.supplied());
    let outstanding_debt = cache.unscale_borrow_ceil(cache.borrowed());
    let backing = cache.cash().saturating_add(outstanding_debt);
    supplied_claim.saturating_sub(backing).max(0)
}
```

**File:** contracts/pool/src/ops/recapitalize.rs (L44-59)
```rust
pub(crate) fn accounting(
    env: &Env,
    hub_asset: HubAssetKey,
    amount: i128,
) -> RecapitalizationOutcome {
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();

```

**File:** contracts/pool/tests/interest.rs (L430-494)
```rust
#[test]
fn test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let alice_scaled_raw = 1_000 * RAY;
        let borrowed_scaled_raw = 1_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: alice_scaled_raw,
            borrowed: borrowed_scaled_raw,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let alice_scaled = Ray::from(alice_scaled_raw);
        let borrow_scaled = Ray::from(borrowed_scaled_raw);

        let bad_debt = cache.unscale_borrow_ceil_ray(borrow_scaled);
        apply_bad_debt_to_supply_index(&mut cache, bad_debt);
        cache.burn_debt(borrow_scaled);

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
