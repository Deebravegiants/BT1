### Title
`liquidate` pulls debt repayment with no minimum-seizure slippage control, so a liquidator can pay and receive zero collateral - (File: contracts/controller/src/positions/liquidation/plan.rs)

### Summary
The analog of the NFT-ID slippage bug is present in `liquidate(liquidator, account_id, debt_payments, seize_mode)`: the liquidator commits debt-token payments, but the collateral legs it will actually seize are computed at execution time by `build_liquidation_plan`, with no parameter letting the liquidator pin a minimum seizure or expected collateral asset. The protocol's own runbook documents that "the contract accepts a liquidation that repays debt and seizes nothing, so the liquidator would pay and receive no collateral" ( [1](#0-0) ). Like `mint(1)` returning whatever ID is next, `liquidate` returns whatever the (possibly changed) plan yields — including nothing.

### Finding Description
`build_liquidation_plan` derives repayment and a pro-rata seizure schedule from live state: cached prices, supply indexes, and the account's current `supply_positions`/`borrow_positions` ( [2](#0-1) ). `calculate_seized_collateral` iterates every supply position and drops legs whose seizure rounds to zero ( [3](#0-2) ). The plan `validate` permits a nonzero repayment with an empty `seized` vector; planning only reverts with `InvalidPayments` in the specific whole-unit/insolvency trimming paths, not when ordinary rounding zeroes all seizure legs ( [4](#0-3) ).

There is no `min_seized`/`expected_collateral` argument anywhere in the liquidate path — the only caller input besides payments is `SeizeMode`, which chooses delivery form, not amount ( [5](#0-4) ). The seizure is always pro rata across all collateral, so a liquidator cannot even restrict which assets it receives ( [6](#0-5) ).

Front-running scenario mirroring the report's Eve/Frank case:

- Liquidator L simulates `liquidate` on account A intending to repay X debt and seize collateral legs.
- A competing liquidator executes a partial liquidation first (or accrual/index updates shift values), changing prices, indexes, and held positions — all inputs to `calculate_seized_collateral` ( [7](#0-6) ).
- L's already-authorized transaction executes against the new state: repayment is pulled at the recomputed plan, but seizure legs round to zero or to far less collateral than L priced.

The threat model explicitly assigns "execution-time bonus, rounding, and route-quality risk" to liquidators and confirms "a tiny repayment can retire debt while its pro-rata seizure rounds to zero" ( [8](#0-7) ).

### Impact Explanation
Theft of user funds: a liquidator transfers debt tokens to the pool and receives zero or materially less collateral than the simulated estimate promised, with no revert to protect it. The loss is unbounded up to the full offered repayment, since refunds only cover *unaccepted* offered amounts, not amounts accepted against a zero-seizure plan ( [9](#0-8) ).

### Likelihood Explanation
Liquidation is a competitive, race-prone flow: candidates are publicly discoverable via `is_liquidatable` and events, multiple bots target the same account, and every "re-simulate immediately before signature" warning in the runbook exists precisely because state drifts between simulation and execution ( [10](#0-9) ). Any competing liquidation, `update_indexes`, or price recompute landing between L's simulation and inclusion reorders the outcome — the exact same "your transaction gets whatever is next" dynamic as the Dutch auction. A deliberate front-runner can also craft the intervening partial liquidation to push remaining legs below seizure-rounding thresholds.

### Recommendation
Add a caller-specified slippage bound to `liquidate`, e.g. a `min_seized_usd_wad` (or per-leg `expected_seized` vector mirroring the repayment vector), and revert with a dedicated error in `LiquidationPlan::validate` / after `calculate_seized_collateral` when the computed seizure falls below it. At minimum, revert unconditionally when `repayment.repay_usd > 0` and `seized_collaterals.is_empty()` in `build_liquidation_plan` ( [4](#0-3) ), instead of documenting the pay-for-nothing outcome as acceptable.

### Proof of Concept
1. Borrower account A holds two supply legs (e.g. USDC + USDT) and a USDT debt; price drop makes `is_liquidatable(A)` true (pattern as in the split-collateral test [11](#0-10) ).
2. Liquidator L simulates `liquidate(L, A, [USDT payment], SeizeMode::Transfer)` via `get_liquidation_estimate`; sees nonzero `seized_collaterals`; signs token transfer auth for the accepted amount.
3. Before inclusion, competing liquidator M executes a partial liquidation (or `update_indexes`/price recompute lands), reducing each remaining supply leg's seizure to below the rounding floor — each leg is dropped at `seizure_ray <= Ray::ZERO → continue` ( [12](#0-11) ).
4. L's transaction executes: `build_liquidation_plan` returns a plan with nonzero repayment and empty `seized` and `validate` accepts it; the pool pulls L's USDT repayment, credits A's debt reduction, and L receives no collateral and no revert. This is the documented accepted outcome ( [1](#0-0) ).

### Citations

**File:** skills/xoxno-lending-liquidations/SKILL.md (L178-180)
```markdown
Reject an estimate whose `seized_collaterals` is empty. The contract accepts a
liquidation that repays debt and seizes nothing, so the liquidator would pay
and receive no collateral.
```

**File:** skills/xoxno-lending-liquidations/SKILL.md (L213-214)
```markdown
Re-simulate immediately before signature because prices, indexes, and received
token amounts can change.
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L34-44)
```rust
    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );
    assert_with_error!(
        env,
        totals.health_factor < Wad::ONE,
        CollateralError::HealthFactorTooHigh
    );
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

**File:** contracts/controller/src/positions/liquidation/math.rs (L383-398)
```rust
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let actual_ray = position.scaled_amount.mul(env, market_index.supply_index);
        let asset_value = risk::position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        let share = asset_value.div(env, total_collateral);
        let seizure_for_asset_usd = total_seizure_usd.mul(env, share);

        let seizure_amount_wad = seizure_for_asset_usd.div(env, feed.price);
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L419-429)
```rust
        if seizure_ray <= Ray::ZERO {
            continue;
        }

        let capped_ray = if repayment.seize_all {
            actual_ray
        } else {
            seizure_ray.min(actual_ray)
        };
        if capped_ray <= Ray::ZERO {
            continue;
```

**File:** common/src/types/controller.rs (L226-243)
```rust
/// How a liquidator takes delivery of the collateral seized from the liquidated account.
///
/// One mode governs the whole call rather than one mode per asset: seizure is pro-rata across
/// every collateral the account holds, so a per-asset choice would have no meaning.
#[contracttype]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SeizeMode {
    /// The pool transfers the underlying tokens to the liquidator, withholding the protocol
    /// fee from the outbound amount.
    Transfer,

    /// The seized supply shares are credited to a controller account instead of being
    /// withdrawn. `0` creates a fresh account owned by the liquidator and bound to the
    /// liquidated account's spoke; any other id must already exist, not be the liquidated
    /// account itself, be owned by (or delegated to) the liquidator, sit in the liquidated
    /// account's spoke, and be in `PositionMode::Normal`.
    Credit(u64),
}
```

**File:** docs/explanation/threat-model.md (L277-281)
```markdown
Liquidators bear execution-time bonus, rounding, and route-quality risk.
A tiny repayment can retire debt while its pro-rata seizure rounds to zero.
Admission does not couple collateral price, decimals, bonus and fee to the
minimum-collateral floor. Expensive low-decimal collateral can yield zero
seizure even for a $5 repayment; assess that precision risk before listing.
```

**File:** docs/reference/invariants.md (L416-424)
```markdown
Repayment planning caps each input by its leg's actual debt. A partial plan
also trims the excess above the liquidation curve's quote before transfers.
Planned refunds are unused input: a partial plan never pulls them; a full-debt
plan pulls the offered amount and the pool returns what exceeds each leg's
debt, which equals the planned refund. Seizure is proportional to collateral
value and capped at held collateral; rounding can leave repayment with no
payable seizure. A collateral leg below 3 decimals seizes whole units: rounded
up when the plan repays all debt, otherwise rounded down with the unbacked
repayment refunded, and a plan left with no seizure reverts. Such a leg is the
```

**File:** tests/test-harness/tests/controller/spoke_liquidation_combo.rs (L83-98)
```rust
    let usdt_collat_before = t.supply_balance(ALICE, "USDT");
    // USD weights at the crashed price: USDC 5_000 x 0.60 = 3_000, USDT 4_000 x 1.00 = 4_000.
    t.liquidate(LIQUIDATOR, ALICE, "USDT", 500.0);

    let usdc_seized_usd = (usdc_collat_before - t.supply_balance(ALICE, "USDC")) * 0.60;
    let usdt_seized_usd = usdt_collat_before - t.supply_balance(ALICE, "USDT");

    assert!(
        usdc_seized_usd > 0.0,
        "USDC collateral must decrease after liquidation, got {usdc_seized_usd}"
    );
    assert!(
        usdt_seized_usd > 0.0,
        "the USDT leg must be seized too - seizure is pro-rata across every collateral, \
         got {usdt_seized_usd}"
    );
```
