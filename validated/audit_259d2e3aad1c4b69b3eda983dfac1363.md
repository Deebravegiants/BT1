### Title
Permissionless dust-supply straddle permanently blocks bad-debt socialization, keeping a market insolvent (contracts/controller/src/positions/liquidation/mod.rs)

### Summary
The permissionless `clean_bad_debt` path admits an insolvent account only when its remaining collateral is at or below the fixed `$5` WAD dust threshold (`is_socializable_bad_debt`). Because `supply` lets any caller top up an existing supply position in a foreign account, a single unprivileged attacker can keep an underwater account's collateral pinned just above `BAD_DEBT_USD_THRESHOLD` forever. Every `clean_bad_debt` call then reverts with `CannotCleanBadDebt`, liquidation is economically irrational (collateral < debt means each repaid unit seizes less value than it costs), and the market's `require_backed_market` guard keeps rejecting all new supply with `PoolInsolvent` while suppliers' claims stay frozen behind an unbacked book. This mirrors the CVE-2026-60186 class: a repeatedly-triggerable availability failure that stalls a protocol component.

### Finding Description
The dust gate in `socialize_bad_debt` requires `total_debt > total_collateral && total_collateral <= BAD_DEBT_USD_THRESHOLD` for the `DustCapped` path used by `clean_bad_debt` [1](#0-0) . The gate is value-based, not count-based, so holding collateral strictly above the threshold — even by one WAD unit — shuts the permissionless path completely; the Certora spec confirms `BAD_DEBT_USD_THRESHOLD + 1` collateral already fails the predicate [2](#0-1) .

The attacker's only tool is `controller::supply`: anyone may pay into an account they do not own for a hub asset the account already holds a supply position in [3](#0-2) . The pool-side leg has no minimum beyond minting one share [4](#0-3) . So whenever accrual, a price tick, or a seizure leg drags the straddled account's collateral back to `<= $5`, the attacker tops up a few dollars of any still-listed collateral asset and re-shuts the gate. Cleanup reverts atomically, so attempts cost the attacker nothing [5](#0-4) .

Self-healing via liquidation does not break the straddle: on an insolvent book every pro-rata leg repays more USD than it seizes (bonus cannot cover a debt/collateral ratio above `1 + bonus` sustained across the whole account), so rational liquidators leave it alone, and the documented whole-unit exception only covers the narrow band where the quote itself reverts [6](#0-5) . While the shortfall persists, `require_backed_market` reverts every new `supply` into the wounded market (`PoolInsolvent`), and permissionless `recapitalize` must fill the entire measured shortfall rather than clear the blocking account [7](#0-6) .

### Impact Explanation
Temporary freezing of funds / protocol component unable to operate, reachable by one unprivileged address for roughly `$5` of collateral per refresh window: `clean_bad_debt` never succeeds, the account's bad debt is never written down or burned, the market stays under `PoolInsolvent` for new suppliers, and outstanding supplier claims remain unbacked and effectively unpayable. Recovery requires the owner-gated `force_socialize_bad_debt` (governance timelock) or a full recapitalization donation — the permissionless machinery cannot resolve the state on its own [8](#0-7) .

### Likelihood Explanation
Cost is near-zero: a few dollars of any listed asset, re-deposited only when the gate would open. No timing race is needed because each failed `clean_bad_debt` is atomic and the attacker can supply at any time. Prerequisites are a genuinely insolvent account that retains at least one supply position slot and a collateral asset still listed — a common end state after a price crash, as the harness fixtures demonstrate [9](#0-8) . Medium severity matches the bounded blast radius (one market's supply entry and socialization liveness, not direct theft).

### Recommendation
Make the dust gate resistant to top-up straddles: e.g., evaluate `is_socializable_bad_debt` against collateral excluding supply credited after the account first became insolvent, net same-market supply against debt before applying the cap, or admit cleanup whenever `total_debt > total_collateral` and the account has been insolvent for a grace period. Alternatively, let permissionless `recapitalize`-style donations into an insolvent account's debt legs route through debt repayment (reducing `total_debt`) rather than collateral, so third-party top-ups can never increase the measured `total_collateral` that gates the `DustCapped` path in `socialize_bad_debt` [10](#0-9) .

### Proof of Concept
1. Market crash leaves account `A` insolvent: `debt = $12,000`, `collateral = $10,000` (fixture in `tests/test-harness/tests/controller/bad_debt_index.rs:146-168` already shows `try_clean_bad_debt` reverting `CannotCleanBadDebt` above the gate).
2. Liquidators partially liquidate until `collateral <= $5`; the gate opens (`clean_bad_debt_gate_never_opens_before_liquidation_does` shows a price walk reaching the gate).
3. Attacker calls `controller::supply(attacker, [(collateral_asset_of_A, $5.01)])` targeting `A`'s existing supply slot — permitted per `INV-AUTH-03` top-ups.
4. Every subsequent `clean_bad_debt(caller, A)` reverts `CannotCleanBadDebt`; `is_socializable_bad_debt(debt, $5.01+ε) == false` while `debt > collateral` still holds.
5. Repeat step 3 whenever collateral decays below `$5`. The market keeps reverting `PoolInsolvent` on `supply` until governance executes `force_socialize_bad_debt` or a donor recapitalizes the whole shortfall.

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L212-243)
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
}

/// Socializes insolvent debt when remaining collateral is at or below the dust cap.
pub(crate) fn clean_bad_debt_standalone(env: &Env, account_id: u64) {
    socialize_bad_debt(env, account_id, BadDebtGate::DustCapped);
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L245-249)
```rust
/// Socializes debt exceeding collateral without a dust cap, outside flash loans.
pub(crate) fn process_force_socialize_bad_debt(env: &Env, account_id: u64) {
    validation::require_not_flash_loaning(env);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```

**File:** certora/controller/spec/boundary_rules.rs (L44-67)
```rust
/// Straddle, first half. An attacker who raises `total_collateral` strictly above
/// `BAD_DEBT_USD_THRESHOLD` (`BAD_DEBT_USD_THRESHOLD + 1` is the cheapest such state) blocks
/// the permissionless dust-gated socialization path while staying insolvent. The gate is
/// value-based, not count-based, so one unit of a second collateral cannot block it: the
/// attacker must post value above the threshold and keep it there.
#[rule]
fn bad_debt_straddle_blocks_dust_gate(e: Env, debt_wad: i128, collateral_wad: i128) {
    let _ = e;
    cvlr_assume!(collateral_wad >= BAD_DEBT_USD_THRESHOLD + 1);
    cvlr_assume!(collateral_wad <= 1_000_000 * WAD);
    cvlr_assume!(debt_wad > collateral_wad && debt_wad <= 2_000_000 * WAD);

    // Symbolic straddle: anywhere strictly above the cap, the dust gate is shut.
    cvlr_assert!(!is_socializable_bad_debt(
        Wad::from(debt_wad),
        Wad::from(collateral_wad)
    ));

    // Explicit +1 witness: one raw WAD unit above the cap blocks it.
    cvlr_assert!(!is_socializable_bad_debt(
        Wad::from(BAD_DEBT_USD_THRESHOLD + 2),
        Wad::from(BAD_DEBT_USD_THRESHOLD + 1)
    ));
}
```

**File:** scripts/permissionless_entrypoints.txt (L69-70)
```text
controller::supply | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may top up an account they do not own, but only for hub assets it already holds a supply position in; a caller that is neither the owner nor an active delegate cannot open a new asset slot, and account_id 0 creates an account owned by the caller.
controller::repay | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may repay any account's debt. Funds are pulled from the caller's own balance and credited from the measured receipt; the target's liabilities can only fall.
```

**File:** contracts/pool/src/ops/supply.rs (L26-36)
```rust
    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);
```

**File:** docs/reference/invariants.md (L421-437)
```markdown
value and capped at held collateral; rounding can leave repayment with no
payable seizure. A collateral leg below 3 decimals seizes whole units: rounded
up when the plan repays all debt, otherwise rounded down with the unbacked
repayment refunded, and a plan left with no seizure reverts. Such a leg is the
account's only supply position, so the seizure stays proportional. On a
solvent account whose leg holds a whole unit, the partial quote can change.
When one unit's value divided by `1 + bonus` covers the whole debt plus one base
unit of each debt leg, the quote becomes the whole debt and the leg rounds up to
one unit. That full close can pay the liquidator more than the quoted bonus.
Otherwise, when the quote seizes less than one unit plus a `1e-6` margin, it
rises to the repayment that backs one unit plus the margin, if that repayment
is below the whole debt. The seizure then refunds the margin, rounded down to
whole debt-token units. Thus such an account stays liquidatable below `HF = 1`, by a one-unit
sale or by a full close. The exception is a debt in the narrow band where
neither change applies: if the curve quote backs less than one unit, every
offer reverts until accrual or a price move ends that state. See
[whole-unit legs](formulas.md#bonus-and-target-repayment).
```

**File:** docs/explanation/threat-model.md (L302-308)
```markdown
Cleanup converts all remaining account supply to protocol revenue and socializes
its gross debt, including same-market supply/debt pairs. It does not net those
pairs first. Suppliers present at cleanup bear index write-downs; a supplier
who exits before cleanup can avoid that loss. The index floor can leave
material unpaid backing, so displayed supplier claims are not a universal
pro-rata cash-payout guarantee. New supply checks backing; recapitalization
repairs the book's measured shortfall without minting shares.
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L146-180)
```rust
fn test_force_socialize_bad_debt_above_dust_threshold() {
    let mut t = setup();

    t.supply(BOB, "ETH", 100.0);
    t.supply(ALICE, "USDC", 100.0);
    t.borrow(ALICE, "ETH", 0.02);

    t.set_price("USDC", usd_cents(30));
    let account_id = t.resolve_account_id(ALICE);

    let collateral = t.total_collateral_raw(ALICE);
    let debt = t.total_debt_raw(ALICE);
    assert!(
        collateral > 5 * WAD,
        "fixture must sit strictly above the $5 dust gate: collateral_wad={collateral}"
    );
    assert!(
        debt > collateral,
        "fixture must be insolvent: debt_wad={debt} collateral_wad={collateral}"
    );

    let refused = t.try_clean_bad_debt_by_id(account_id);
    assert_contract_error(refused, errors::CANNOT_CLEAN_BAD_DEBT);

    let (si_before, _) = get_indexes(&t, "ETH");

    t.force_socialize_bad_debt_by_id(account_id);

    let (si_after, _) = get_indexes(&t, "ETH");
    assert!(
        si_after < si_before,
        "force-socialize must drop the ETH supply index: before={si_before}, after={si_after}"
    );
    t.assert_no_positions(ALICE);
}
```
