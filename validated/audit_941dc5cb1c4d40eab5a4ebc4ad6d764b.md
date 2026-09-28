### Title
Dust-gate straddle: an unprivileged third-party `supply` locks permissionless `clean_bad_debt` for an insolvent account - ([File: contracts/controller/src/positions/liquidation/curve.rs])

### Summary
The external report's class — an unprivileged caller front-running a legitimate owner/keeper action and permanently flipping a state bit that locks a protocol-level management function — maps directly onto XOXNO Lending's bad-debt cleanup gate. `clean_bad_debt` is permissionless but only admits accounts whose total collateral is at or below `BAD_DEBT_USD_THRESHOLD` ($5 WAD) while debt strictly exceeds collateral. Any unprivileged address can call `controller::supply` against an existing supply slot of a foreign insolvent account, pushing `total_collateral` just above the dust cap and shutting the dust gate, so the only remaining cleanup path is the governance-timelocked `force_socialize_bad_debt`.

### Finding Description
`socialize_bad_debt` selects `BadDebtGate::DustCapped` for the permissionless `clean_bad_debt` entrypoint and `InsolventOnly` for the owner-gated force path [1](#0-0) . The dust gate is a pure value predicate: `total_debt > total_collateral && total_collateral <= BAD_DEBT_USD_THRESHOLD` [2](#0-1) .

`controller::supply` is permissionless and allows a caller who is neither owner nor delegate to top up a foreign account for any hub asset the account already holds a supply position in [3](#0-2) . The `AccountRiskTotals` used by the gate are computed from the position's current supply shares, so the attacker's donation counts as victim collateral [4](#0-3) .

The Certora spec itself proves the straddle: at `collateral_wad = BAD_DEBT_USD_THRESHOLD + 1` with `debt_wad > collateral_wad`, `is_socializable_bad_debt` is false while the `InsolventOnly` gate still admits the account — meaning that without governance intervention the bad debt cannot be socialized at all [5](#0-4) . `check_bad_debt_after_liquidation` applies the same predicate, so the straddle also suppresses the automatic post-liquidation cleanup [6](#0-5) .

### Impact Explanation
The donated collateral keeps the insolvent account above the dust cap indefinitely. `clean_bad_debt` reverts with `CannotCleanBadDebt`, and the residual debt is never written down against the market's supply index — the protocol's documented insolvency-resolution path stalls. The unwritten bad debt keeps accruing interest at `max_borrow_rate`-bounded chunks, deepening the backing shortfall borne by suppliers. Cleanup then requires the owner-gated `force_socialize_bad_debt`, which runs through the Sensitive governance timelock delay, so the lockout is real but bounded by governance latency [7](#0-6) . This is a denial of service on a protocol-critical maintenance function, the direct analog of the license-token-mint lock on `addIp`/`removeIp`. One mitigating asymmetry: the attacker's donated collateral is itself liquidatable (the account remains HF < 1), so a liquidator can repay a slice, seize the straddle collateral, and reopen the dust gate — the attacker's cost (~$5+ USD per straddle) is forfeited on seizure or reclassified as revenue on cleanup. That limits the finding to a griefing/DoS rather than permanent insolvency.

### Likelihood Explanation
- Entrypoint is fully permissionless: `supply(caller, account_id, spoke_id, assets)` with `caller.require_auth()` only; no ownership check on topping up an existing slot [3](#0-2) .
- Cost is ~`BAD_DEBT_USD_THRESHOLD` ($5) plus fees, scaled by however long the attacker wants to keep topping back up after each liquidation.
- The attacker must monitor liquidation/cleanup attempts and re-straddle if a liquidator drains the donated collateral; it is an active, repeatable grief rather than a one-shot lock.
- No economic profit motive is required; a competitor, or the account owner themselves (to delay socialization of their own bad debt), can execute it.

### Recommendation
Make the dust gate robust to donated collateral. Options: (a) evaluate `is_socializable_bad_debt` against collateral excluding supply legs added after the account became insolvent, or against collateral net of the most recent permissionless top-up window; (b) raise the gate to compare `total_debt - total_collateral` shortfall against the dust cap rather than raw collateral, so straddling does not help; or (c) restrict third-party `supply` into insolvent accounts (HF < 1) so only the owner or delegate can add collateral once the account is under water. The simplest consistent fix is (b): an insolvent account's cleanup eligibility should depend on the size of the unbacked shortfall, not on how much forfeitable collateral a stranger parks on top of it.

### Proof of Concept
```rust
// Shape only; mirrors tests/test-harness helpers.
#[test]
fn stranger_dust_supply_blocks_permissionless_clean_bad_debt() {
    let mut t = LendingTest::new().standard_two_asset().build();
    t.supply(BOB, "ETH", 100.0);
    // ALICE: small USDC collateral, borrowed ETH that goes underwater.
    t.supply(ALICE, "USDC", 4.0);
    t.borrow(ALICE, "ETH", /* debt worth > $4 */);

    // Price crash: debt > collateral, collateral <= $5 -> dust gate open.
    t.set_price("USDC", /* crash so collateral = $4, debt = $10 */);
    let alice_id = t.resolve_account_id(ALICE);
    assert!(t.try_clean_bad_debt_by_id(alice_id).is_ok() /* or gate predicate true */);

    // Rebuild state; now CAROL (a stranger) straddles the gate.
    // `supply` to ALICE's account on her existing USDC slot is allowed
    // for non-owner/non-delegate callers.
    t.supply_to(CAROL, alice_id, "USDC", 2.0); // collateral: $4 -> $6 > $5 cap

    // Permissionless cleanup is now denied even though debt ($10) > collateral ($6).
    assert_contract_error(
        t.try_clean_bad_debt_by_id(alice_id),
        errors::CANNOT_CLEAN_BAD_DEBT,
    );
    // Only the owner-gated force path can still clean it:
    // t.force_socialize_bad_debt_by_id(alice_id) // requires ADMIN auth
}
```
The arithmetic is pinned by `bad_debt_straddle_blocks_dust_gate`: `collateral_wad = BAD_DEBT_USD_THRESHOLD + 1` with `debt_wad > collateral_wad` closes the dust gate while `InsolventOnly` still admits the account [8](#0-7) . The analogous live-path denial is already exercised in reverse by `test_force_socialize_bad_debt_above_dust_threshold`, which shows collateral strictly above $5 makes `clean_bad_debt` revert with `CannotCleanBadDebt` while `force_socialize_bad_debt` succeeds [9](#0-8) .

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L202-243)
```rust
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

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** scripts/permissionless_entrypoints.txt (L69-69)
```text
controller::supply | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may top up an account they do not own, but only for hub assets it already holds a supply position in; a caller that is neither the owner nor an active delegate cannot open a new asset slot, and account_id 0 creates an account owned by the caller.
```

**File:** certora/controller/spec/boundary_rules.rs (L44-103)
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

/// Straddle, second half. The owner-gated force path
/// (`force_socialize_bad_debt`, `BadDebtGate::InsolventOnly`) admits exactly the straddling
/// state that `bad_debt_straddle_blocks_dust_gate` shows the dust gate rejects. The dust gate
/// does not cover the whole insolvent domain, so without the force path straddled bad debt
/// cannot be socialized.
#[rule]
fn bad_debt_straddle_admitted_by_force_gate(e: Env, debt_wad: i128, collateral_wad: i128) {
    let _ = e;
    cvlr_assume!(debt_wad >= 0 && debt_wad <= 2_000_000 * WAD);
    cvlr_assume!(collateral_wad >= 0 && collateral_wad <= 2_000_000 * WAD);

    let debt = Wad::from(debt_wad);
    let collateral = Wad::from(collateral_wad);
    let dust_gate = is_socializable_bad_debt(debt, collateral);
    let force_gate = insolvent_gate_admits(debt, collateral);

    // Containment: the force gate is strictly looser, so it never rejects what the
    // permissionless path accepts.
    cvlr_assert!(!dust_gate || force_gate);

    // Anchor: the dust gate is exactly the force gate conjoined with the dust cap. Keeps the
    // mirrored `InsolventOnly` predicate from drifting away from production silently.
    cvlr_assert!(dust_gate == (force_gate && collateral_wad <= BAD_DEBT_USD_THRESHOLD));

    // The straddle separates the two gates: dust blocked, force admits.
    if collateral_wad > BAD_DEBT_USD_THRESHOLD && debt_wad > collateral_wad {
        cvlr_assert!(!dust_gate);
        cvlr_assert!(force_gate);
    }

    // Explicit +1 witness, on the same concrete point the dust-gate rule rejects.
    let witness_collateral = Wad::from(BAD_DEBT_USD_THRESHOLD + 1);
    let witness_debt = Wad::from(BAD_DEBT_USD_THRESHOLD + 2);
    cvlr_assert!(!is_socializable_bad_debt(witness_debt, witness_collateral));
    cvlr_assert!(insolvent_gate_admits(witness_debt, witness_collateral));
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

**File:** docs/reference/runbooks/force-socialize-bad-debt.md (L3-15)
```markdown
This runbook covers governance-authorized removal of an insolvent account.
Use it when collateral exceeds the fixed $5 dust limit of permissionless
`clean_bad_debt`. Cleanup can also proceed when `no_seize` blocks ordinary
liquidation.

The account must hold debt, with ceil risk debt strictly greater than half-up
unweighted collateral (`D > C`). An unhealthy health factor alone does not
qualify. The forced path has no collateral dust cap.

**Cleanup is irreversible.** All remaining collateral becomes protocol revenue.
All remaining debt is written off against its own markets' supply indexes,
including when collateral and debt share a market. There is no automatic netting
or insurance payment. The account is deleted and its position NFT burns.
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L145-179)
```rust
#[test]
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
```
