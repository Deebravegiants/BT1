### Title
Insolvent accounts with collateral above the $5 bad-debt cap can be unliquidatable and un-cleanable when no whole debt unit fits the collateral-backed quote — (`contracts/controller/src/positions/liquidation/math.rs`)

### Summary
The bad-debt mechanism has a coverage gap between two conservative "minimum" rules. Permissionless `clean_bad_debt` requires `total_collateral <= BAD_DEBT_USD_THRESHOLD` ($5 WAD). On an insolvent account (`C < D`), `liquidate` caps the repayment quote at `floor(C / (1 + base_bonus))` and rounds each kept repayment leg **down to whole token units**; a leg whose kept amount rounds to zero is dropped, and if no leg remains the call reverts with `InvalidPayments` (16). The insolvency branch deliberately never promotes the quote to full debt, expecting cleanup to absorb the residue. When a borrowable asset's base unit is worth more than the backed quote while collateral sits just above $5, neither mechanism can touch the account: every `liquidate` reverts and every `clean_bad_debt` reverts `CannotCleanBadDebt` (114). Bad debt then accrues interest indefinitely at supplier expense until the owner-only `force_socialize_bad_debt` is invoked.

### Finding Description
- The dust gate: permissionless cleanup requires `ceil` debt `>` half-up collateral **and** `total_collateral <= 5 WAD`, so `collateral = $5.01` is rejected [1](#0-0) . The straddle is explicitly acknowledged as reachable by an unprivileged actor in the Certora spec: "an attacker who raises `total_collateral` strictly above `BAD_DEBT_USD_THRESHOLD` … blocks the permissionless dust-gated socialization path while staying insolvent" [2](#0-1) .
- The liquidation side: `build_liquidation_plan` → `normalize_repayment_plan` quotes `min(D, floor(C × WAD / (WAD + base)))` for insolvent accounts and trims each kept leg down to whole token units; legs rounding to zero are dropped and a plan with no legs reverts `InvalidPayments` [3](#0-2) . Confirmed by test: a $10-unit debt leg against $9 collateral keeps no repayment, refunds the whole offer, and execution reverts [4](#0-3) . The plan pipeline has no fallback for this case [5](#0-4) .
- Note `MIN_BORROWABLE_ASSET_DECIMALS` only affects collateral seizure legs; the whole-unit trim on the **debt** side applies to any asset regardless of decimals [6](#0-5) .

The stuck band is: `D > C > 5 WAD` and `floor(C / (1 + base)) < unit_value_usd(debt)` for every debt leg. Interest accrual only deepens insolvency, and collateral staying above $5 keeps the dust gate shut forever.

### Impact Explanation
Permanent (absent privileged intervention) accumulation of unresolvable bad debt. The account's debt compounds while suppliers' claims cannot be written down through the permissionless path, degrading market backing — protocol insolvency accrual plus a permissionless-cleanup DoS. Recovery requires the owner-gated `force_socialize_bad_debt`, so the permissionless resolution path the protocol advertises is dead for these accounts.

### Likelihood Explanation
An unprivileged borrower reaches the band through ordinary market movement or interest accrual: open a position borrowing a high-unit-value asset (e.g., a 3–4 decimal token priced above ~$5k/unit, so one base unit exceeds $5), let collateral drift below debt but above $5. Any griefer can also hold an already-insolvent account above the dust cap indefinitely by topping up its existing supply position (supply top-ups on existing positions are permitted to arbitrary callers). Requires a listed borrowable asset whose unit value exceeds roughly `$5/(1+bonus)`, which constrains but does not eliminate feasibility — hence Medium rather than High likelihood.

### Recommendation
Close the gap on one side: either (a) in the insolvent branch, when no kept leg survives whole-unit rounding, promote the quote to a full close at the collateral-backed effective bonus (mirroring `whole_unit_repayment`'s rule-1 logic for collateral units) [7](#0-6) ; or (b) relax `is_socializable_bad_debt` so an insolvent account whose collateral-backed quote fits zero whole units of every debt leg is socializable regardless of the $5 cap; or (c) bound the admitted unit value of borrowable listings relative to `BAD_DEBT_USD_THRESHOLD` at listing time.

### Proof of Concept
1. Governance lists a borrowable asset `BIG` with `asset_decimals = 3` and price $10,000 ⇒ `unit_value_usd = $10`.
2. Attacker supplies $11 of collateral (LTV 75%) and borrows 1 unit of `BIG` ($10). Position is healthy at open.
3. Collateral price drifts so `C = $8`, `D ≈ $10 + interest`. HF < 1, `C < D`, `C > $5`.
4. Any liquidator calls `liquidate`: quote `= floor(8 / (1+base)) ≈ $7.6 < $10` ⇒ the single debt leg keeps `floor(7.6/10) = 0` units, is dropped, no legs remain ⇒ revert `InvalidPayments` [8](#0-7) .
5. Anyone calls `clean_bad_debt`: `total_collateral = $8 > 5 WAD` ⇒ revert `CannotCleanBadDebt` [9](#0-8) .
6. The debt compounds forever; only `force_socialize_bad_debt` (owner) resolves it. A third party can additionally top up the supply leg if price moves push collateral back under $5.

Uncertainty: feasibility depends on a listed borrowable market whose base-unit value exceeds ~$5/(1+base bonus); if all borrowable listings have small units, the stuck band is unreachable and the finding collapses to the documented straddle.

### Citations

**File:** docs/reference/invariants.md (L463-475)
```markdown
### INV-LIQ-04 — Bad-debt socialization is explicit and total

Permissionless cleanup requires ceil risk debt greater than half-up unweighted
collateral and collateral at or below the fixed $5 dust threshold. Owner-only
forced cleanup omits the dust cap. Both require debt, readable account and NFT
state, valid required prices and no active flash guard. Listing flags and
global pause do not block standalone cleanup.

Cleanup reclassifies all remaining collateral shares as revenue and writes off
all remaining debt against each debt's market. It releases spoke usage and
atomically removes account entries and the NFT. It does not net same-market
supply against debt. Standalone cleanup emits `CleanBadDebtEvent` with
pre-cleanup USD totals, without a controller position-update batch.
```

**File:** certora/controller/spec/boundary_rules.rs (L44-60)
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

**File:** tests/test-harness/tests/controller/liquidation_extreme.rs (L719-745)
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
}
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L63-96)
```rust
    let mut repayment = normalize_repayment_plan(
        env,
        account,
        raw_payments,
        &snap,
        bonus_bounds,
        &curve,
        cache,
    );

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

**File:** contracts/controller/src/positions/liquidation/math.rs (L269-290)
```rust
    let unit_at_bonus = Wad::from(mul_div_floor(
        env,
        unit_usd.raw(),
        Wad::ONE.raw(),
        one_plus_bonus.raw(),
    ));
    let full_close_ceiling = snap
        .total_debt
        .checked_add(env, one_unit_per_debt_leg_usd(env, account, cache));
    if unit_at_bonus >= full_close_ceiling {
        return snap.total_debt;
    }
    let unit_repayment = Wad::from(mul_div_ceil(
        env,
        unit_with_margin.raw(),
        Wad::ONE.raw(),
        one_plus_bonus.raw(),
    ));
    if unit_repayment >= snap.total_debt {
        return quote_usd;
    }
    unit_repayment
```

**File:** contracts/controller/tests/positions/liquidation_math.rs (L855-868)
```rust
/// $10 of collateral backs $9.52, less than one $10 unit: the leg keeps
/// nothing, its whole offer is refunded and no repayment leg remains.
#[test]
fn an_insolvent_trim_drops_a_leg_whose_smallest_unit_exceeds_the_backed_quote() {
    let env = Env::default();
    let (keys, plan) = plan_on_insolvent_book(&env, &[(10_000 * WAD, 3, 5, 2)], 10 * WAD, 50 * WAD);

    assert!(plan.repaid.is_empty(), "no leg fits the backed quote");
    assert_eq!(plan.repay_usd, Wad::ZERO);
    assert_eq!(plan.refunds.len(), 1);
    let refund = plan.refunds.get_unchecked(0);
    assert_eq!(refund.asset, keys.get_unchecked(0).asset);
    assert_eq!(refund.amount, 2, "the whole offer is refunded");
}
```

**File:** docs/reference/errors.md (L66-66)
```markdown
| 114 `CannotCleanBadDebt` | Debt does not exceed collateral, or permissionless cleanup has collateral above `BAD_DEBT_USD_THRESHOLD` (5 USD, WAD). | Liquidate further; governance force-socialization bypasses only the collateral dust cap. |
```
