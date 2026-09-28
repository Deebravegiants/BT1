The MySQL report is a *readily reachable, repeatable crash/hang* bug class. Mapping that onto XOXNO Lending: an unprivileged borrower can construct an account that the liquidation planner can never execute — every `liquidate` call reverts — while `clean_bad_debt`'s $5 dust gate also rejects it, leaving bad debt permanently stuck for all unprivileged paths.

Let me confirm the exact rounding/drop mechanics in the insolvent trim.### Title
Insolvent account whose collateral-backed quote is below one debt-token unit is permanently unliquidatable and above the bad-debt dust gate - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
`normalize_repayment_plan` quotes an insolvent account's repayable amount as `floor(C / (1 + base))` and then trims each offered leg down to **whole debt-token units**, dropping any leg that rounds to zero and reverting with `InvalidPayments` when no leg survives. If the quote is smaller than one base unit of the account's only debt token, *every* `liquidate` call reverts regardless of offer size. If the same account's collateral is above `BAD_DEBT_USD_THRESHOLD` ($5 WAD), the permissionless `clean_bad_debt` also rejects it. The two bounds overlap on a non-empty band: an unprivileged borrower can park an account in `BAD_DEBT_USD_THRESHOLD < C < (1 + base) × unit_debt_usd` with `D > C`, where no unprivileged entrypoint can touch it. This is the same bug class as CVE-2021-2031: a readily reachable input state that produces a repeatable, unconditional crash (revert) of the operation.

### Finding Description
- The insolvent branch of the quote is set in `normalize_repayment_plan`: when `snap.total_collateral < snap.total_debt` the ideal is the collateral-backed quote, and `process_excess_payment` trims kept legs down to whole token units; per the documented behavior, "a leg whose kept amount rounds to zero is dropped and its whole offer refunded; if no leg remains, `liquidate` reverts with `InvalidPayments`" (`docs/reference/formulas.md`, seizure/sizing section). The quote itself is `min(D, floor(C × WAD / (WAD + base)))`. [1](#0-0) [2](#0-1) 
- The `whole_unit_repayment` promotion that rescues sub-unit quotes only runs on **solvent** accounts (`insolvent || curve_repayment_usd >= snap.total_debt` selects `curve_repayment_usd` directly), so it never lifts the insolvent quote to one unit. [3](#0-2) 
- `build_liquidation_plan` then releases repayment against the seized legs and calls `plan.validate`, which rejects a plan with repayment but no seizure — the unconditional revert. [4](#0-3) 
- The permissionless cleanup gate requires `total_collateral <= BAD_DEBT_USD_THRESHOLD`, so `C > $5` blocks `clean_bad_debt`. [5](#0-4) [6](#0-5) 
- The test `test_insolvent_liquidation_reverts_when_no_debt_unit_fits_the_backed_quote` demonstrates exactly the stuck state: $9 collateral backing a $8.57 quote against a debt token whose unit is $10 — estimate shows `max_payment_wad == 0`, empty `seized_collaterals`, and `liquidate` reverts `INVALID_PAYMENTS` — while $9 > $5 blocks the dust gate. [7](#0-6) 

### Impact Explanation
An unprivileged borrower can create an account that no liquidator and no `clean_bad_debt` caller can ever close: `liquidate` reverts `InvalidPayments` for every possible payment vector, and `clean_bad_debt` reverts `CannotCleanBadDebt`. The account's debt keeps accruing interest against a market whose suppliers are owed funds the protocol cannot recover; the collateral (>$5) is locked inside an account no one can seize. Only the owner-gated `force_socialize_bad_debt` (`BadDebtGate::InsolventOnly`, governance delay tier) can remove it. This is a permanent freezing of funds plus accruing protocol insolvency reachable entirely through `supply`/`borrow`, matching the Medium-severity availability impact of the reference CVE.

### Likelihood Explanation
The band is wide and cheap to hit. For a debt token with unit value `U_d` and base bonus `b`, the attacker needs `5 USD < C < U_d × (1 + b)` and `D > C`. With a 0–2-decimal/high-priced debt asset (e.g., a $10-or-higher unit), the band is several dollars wide. The attacker supplies collateral in that range, borrows just above `C` worth of the coarse debt token, and any downward price tick (or accrued interest pushing `D` over `C`) lands the account in the stuck state — `D > C` is trivially satisfiable by borrowing near the LTV limit and letting accrual work. Because liquidation seizure on such an account is economically meaningless anyway (the quote backs less than one unit), the borrower's collateral is already lost to them; their cost is only the collateral, while the protocol is left holding unbacked, unclosable debt. Any user can repeat this across many accounts.

### Recommendation
In the insolvent branch of `normalize_repayment_plan` / `process_excess_payment`, do not floor kept repayment legs to whole token units when doing so empties the plan — either keep the last surviving leg at its exact (sub-unit) amount, or promote the ideal to the smallest whole unit of one debt leg, mirroring `whole_unit_repayment` for the insolvent side. Alternatively, extend `is_socializable_bad_debt` to also admit the case where the collateral-backed quote cannot pay one whole unit of any debt leg, so `clean_bad_debt` remains reachable for residue that liquidation structurally cannot collect.

### Proof of Concept
1. Attacker supplies ~$9.5 of a normal collateral asset and borrows 1 unit of a debt token `EXP` priced at $10/unit with 0 decimals (max LTV permitting `D ≈ C` at open).
2. A small price move or interest accrual makes `D = $10+ > C = $9` → insolvent, `HF < 1`, `is_liquidatable == true`.
3. Liquidator calls `liquidate(liquidator, account_id, [(EXP, 1)], SeizeMode::Transfer)`. `estimate_liquidation_amount` returns `floor(9/1.09) ≈ $8.26`; trimming rounds the kept EXP leg down to 0 whole units, the leg is dropped, `seized_collaterals` is empty, and `plan.validate` reverts `InvalidPayments` — identically for every offer amount, since any offer is capped by the same sub-unit quote.
4. Any user calls `clean_bad_debt(caller, account_id)` → `is_socializable_bad_debt(D, C)` is false because `C > 5 WAD` → reverts `CannotCleanBadDebt`.
5. The account is permanently stuck absent a governance `ForceSocializeBadDebt` operation; the borrowed $10 is kept by the attacker and the market's debt accrues unrecoverably. This exact state is exercised by `test_insolvent_liquidation_reverts_when_no_debt_unit_fits_the_backed_quote` (`tests/test-harness/tests/controller/liquidation_extreme.rs:721-745`), which confirms zero `max_payment_wad`, empty seizure, and the `INVALID_PAYMENTS` revert.

### Citations

**File:** contracts/controller/src/positions/liquidation/math.rs (L186-205)
```rust
    let (curve_repayment_usd, bonus) = estimate_liquidation_amount(env, snap, bonus_bounds, curve);
    let insolvent = snap.total_collateral < snap.total_debt;
    let ideal_repayment_usd = if insolvent || curve_repayment_usd >= snap.total_debt {
        curve_repayment_usd
    } else {
        whole_unit_repayment(env, account, snap, curve_repayment_usd, bonus, cache)
    };
    let full_close = ideal_repayment_usd >= snap.total_debt;

    let mut final_repayment_tokens = repaid_tokens;
    if !full_close && total_debt_payment_usd > ideal_repayment_usd {
        let excess_usd = total_debt_payment_usd.checked_sub(env, ideal_repayment_usd);
        process_excess_payment(
            env,
            &mut final_repayment_tokens,
            &mut refunds,
            excess_usd,
            insolvent,
        );
    }
```

**File:** docs/reference/formulas.md (L255-264)
```markdown
Insolvency is the exact unweighted comparison `C < D`. With positive `p`, the
insolvency branch quotes the repayment the collateral backs at the base bonus,
floored, so an offer above it is trimmed and the liquidator never pays more
than it seizes. On an insolvent account the trim rounds each kept leg down to
whole token units, so the kept
value never exceeds the quote. A leg whose kept amount rounds to zero is
dropped and its whole offer refunded; if no leg remains, `liquidate` reverts
with `InvalidPayments` (16) and the estimate shows a zero payment. This insolvency
branch does not promote the quote to full debt; bad-debt cleanup takes the unbacked
residue. With `p == 0`, the target formula and dust promotion below apply instead.
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L73-96)
```rust
    let (seized_collaterals, unbacked_usd) =
        calculate_seized_collateral(env, account, totals.total_collateral, &repayment, cache);
    release_unbacked_repayment(env, &mut repayment, unbacked_usd);
    if unbacked_usd > Wad::ZERO && seized_collaterals.is_empty() {
        let repay_usd = repayment.repay_usd;
        release_unbacked_repayment(env, &mut repayment, repay_usd);
    }

    for entry in seized_collaterals.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &entry.hub_asset,
            FreezePolicy::SeizureLeg,
        );
    }

    let plan = LiquidationPlan {
        repayment,
        seized: seized_collaterals,
    };
    plan.validate(env);
    plan
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L23-27)
```rust
/// Admits socialization when debt exceeds collateral and collateral is at or
/// below `BAD_DEBT_USD_THRESHOLD` (WAD USD).
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-235)
```rust
    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);
```

**File:** tests/test-harness/tests/controller/liquidation_extreme.rs (L719-744)
```rust
/// $9 of collateral backs $8.57, less than one $10 EXP unit: the estimate
/// keeps no repayment and refunds the whole offer, and execution reverts.
#[test]
fn test_insolvent_liquidation_reverts_when_no_debt_unit_fits_the_backed_quote() {
    let (mut t, account_id) = insolvent_book_with_a_ten_dollar_unit(usd(9) / 1_000);
    let exp = t.resolve_asset("EXP");
    let payments = vec![&t.env, (hub_asset(exp.clone()), 2)];
    let estimate =
        t.ctrl_client()
            .get_liquidation_estimate(&account_id, &payments, &SeizeMode::Transfer);
    assert_eq!(estimate.max_payment_wad, 0);
    assert!(estimate.seized_collaterals.is_empty());
    let refund = estimate.refunds.get(0).expect("EXP refund");
    assert_eq!((refund.asset, refund.amount), (exp, 2));

    let liquidator = t.get_or_create_user(LIQUIDATOR);
    t.resolve_market("EXP").token_admin.mint(&liquidator, &2);
    let result = map_try_ok_value(t.ctrl_client().try_liquidate(
        &liquidator,
        &account_id,
        &payments,
        &SeizeMode::Transfer,
    ));
    assert_contract_error(result, errors::INVALID_PAYMENTS);
    assert_eq!(t.token_balance_raw(LIQUIDATOR, "EXP"), 2);
    assert_eq!(t.borrow_balance_raw(ALICE, "EXP"), 2);
```
