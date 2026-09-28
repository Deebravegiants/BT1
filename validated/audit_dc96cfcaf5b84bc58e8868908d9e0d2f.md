### Title
Liquidator can front-run a borrower's rescue transaction to deny self-cure and seize the liquidation bonus - ([File: contracts/controller/src/positions/liquidation/plan.rs](contracts/controller/src/positions/liquidation/plan.rs))

### Summary
`controller::liquidate` is permissionless and executable by any unprivileged address whenever an account's health factor is below 1 WAD. A borrower who is near liquidation and submits a `repay`, `supply`, or `repay_debt_with_collateral` transaction to restore health can be front-run by an attacker who calls `liquidate` first, seizing the collateral at a bonus and paying a protocol fee that the borrower would never have owed. This is the same griefing class as the reference Tracer finding (mempool front-running that denies a user a beneficial state transition), mapped onto liquidation instead of order matching — the attacker is literally "a liquidator stopping a user who is close to liquidation from becoming liquid again".

### Finding Description
- `liquidate(liquidator, account_id, debt_payments, seize_mode)` requires only caller authorization; the docs confirm "anyone may liquidate an account whose health factor is below one, including the account's own owner" (`scripts/permissionless_entrypoints.txt` line 71). [1](#0-0) 
- Eligibility is computed at execution time in `build_liquidation_plan`, which only requires `totals.health_factor < Wad::ONE`; there is no grace window, no owner opt-out, and no check that a cure transaction is pending. [2](#0-1) 
- The seizure price includes a bonus: `total_seizure_usd = repay_usd × (1 + b)` where `b` comes from the HF-based bonus curve (`calculate_linear_bonus_with_target`), and a `liquidation_fees` share of the bonus is withheld for the protocol in both `SeizeMode::Transfer` and `SeizeMode::Credit`. [3](#0-2) 
- The borrower's alternative — `repay` (callable on any account, including by the owner) or `repay_debt_with_collateral` — retires debt at par. If the liquidation lands first, the borrower pays `repay × (1 + b) + fee` worth of collateral instead of `repay`.
- On Soroban, transaction ordering is driven by inclusion fee bidding, so a motivated liquidator can observe a user's submitted rescue transaction and outbid it for earlier inclusion, exactly the mempool-observation attack in the reference report. The attacker's cost is only the repaid principal (which it recovers plus bonus), mirroring the report's "just paying the fees" economics.

### Impact Explanation
Theft of user funds. The victim loses collateral equal to the liquidation bonus and protocol fee on the seized leg — funds that would have remained theirs had the front-run rescue transaction executed. In the documented band case (`cap < base`), a full-debt liquidation seizes up to `C/D` of collateral; more generally the loss is `repay × b` plus `liquidation_fees` on the bonus. Severity Medium: the loss is bounded by the configured bonus (typically a few hundred BPS up to the HF-preserving cap) and requires the account to already be at HF < 1.

### Likelihood Explanation
Requires the victim's account to already sit below HF 1 and the victim to broadcast an unbundled cure transaction. Both conditions occur naturally after oracle price moves; `is_liquidatable` and `get_health_factor` make such accounts trivially discoverable. The attacker needs only a funded wallet and higher inclusion fee — no privileged role. A borrower can fully mitigate by bundling the cure atomically (e.g., `repay_debt_with_collateral`/`flash_position` in a single transaction) rather than submitting standalone `repay`/`supply` transactions, which lowers the practical frequency but does not remove the vulnerability for users using simple transactions.

### Recommendation
Introduce a short cure window or self-cure priority: e.g., record a pending repay/supply intent and reject `liquidate` on the account within N ledgers of a health-improving action, or allow the account owner to flag the account for a brief liquidation delay. Alternatively document that rescues must be bundled atomically (Soroban supports multi-operation transactions) and surface that guidance in the SDK builders, since standalone `repay` transactions are inherently front-runnable.

### Proof of Concept
1. Alice supplies 10,000 USDC and borrows ETH to an HF of 0.975 (as in `test_deep_underwater_higher_bonus` in `tests/test-harness/tests/controller/liquidation_math.rs`). [4](#0-3) 
2. Alice submits `repay(caller=alice, account_id, payments=[(ETH, 3_0000000)])` to retire the debt at par.
3. Attacker `keeper` observes the pending transaction and submits `liquidate(keeper, alice_id, payments=[(ETH, debt)], SeizeMode::Transfer)` with a higher inclusion fee. `build_liquidation_plan` passes because HF < 1. [2](#0-1) 
4. The liquidation executes first: keeper pays the debt and receives `repay × (1 + bonus)` of USDC minus the `liquidation_fees` share. Alice's subsequent `repay` reverts on `HealthFactorTooHigh` / missing debt, and she has permanently lost the bonus + fee portion of her collateral instead of paying only the debt. [5](#0-4)

### Citations

**File:** scripts/permissionless_entrypoints.txt (L71-72)
```text
controller::liquidate | caller-auth | INV-AUTH-03, INV-LIQ-01, INV-LIQ-02 | Anyone may liquidate an account whose health factor is below one, including the account's own owner; in Credit seize mode the receiving account must be a different account that the liquidator owns or is an active delegate of, and seizure stays coupled to the debt actually repaid.
controller::clean_bad_debt | caller-auth | INV-AUTH-03, INV-LIQ-04 | Anyone may socialize an insolvent account's residual debt, but only once its remaining collateral is at or below the dust threshold; only the owner-gated force_socialize_bad_debt omits the dust cap.
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L40-44)
```rust
    assert_with_error!(
        env,
        totals.health_factor < Wad::ONE,
        CollateralError::HealthFactorTooHigh
    );
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L60-80)
```rust
pub(crate) fn calculate_linear_bonus_with_target(
    env: &Env,
    hf: Wad,
    base: Bps,
    max: Bps,
    curve: &LiquidationCurve,
    target: Wad,
) -> Bps {
    if hf >= target {
        return base;
    }
    let scale = curve.bonus_scale(env, hf, target);

    let bonus_range = max.checked_sub(env, base);
    let bonus_increment = Wad::from(bonus_range.raw()).mul(env, scale).raw();
    let scaled_increment = curve.bonus_factor.apply_to(env, bonus_increment);
    Bps::from(
        base.raw()
            .checked_add(scaled_increment)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
    )
```

**File:** tests/test-harness/tests/controller/liquidation_math.rs (L96-115)
```rust
fn test_deep_underwater_higher_bonus() {
    let mut t = LendingTest::new().standard_two_asset().build();

    t.supply(ALICE, "USDC", 10_000.0);
    t.borrow(ALICE, "ETH", 3.0);
    t.set_price("USDC", usd_cents(74));

    let id_alice = t.resolve_account_id(ALICE);
    let payments =
        soroban_sdk::Vec::from_array(&t.env, [(hub_asset(t.resolve_asset("ETH")), 3_0000000)]);
    let light =
        t.ctrl_client()
            .get_liquidation_estimate(&id_alice, &payments, &SeizeMode::Transfer);
    let hf_light = t.ctrl_client().get_health_factor(&id_alice);
    let hf_light_f64 = hf_light as f64 / WAD as f64;
    assert!(
        hf_light_f64 > 0.95 && hf_light_f64 < 1.0,
        "light case HF should be 0.95-1.0, got {:.4}",
        hf_light_f64
    );
```

**File:** contracts/controller/tests/positions/liquidation_zero_threshold.rs (L371-392)
```rust
    let receiver = client.liquidate(
        &fx.liquidator,
        &VICTIM,
        &payment(&fx, 30),
        &SeizeMode::Transfer,
    );

    assert_eq!(receiver, 0, "transfer mode credits no account");
    assert_eq!(
        fx.debt_scaled(VICTIM),
        60 * RAY,
        "$30 of the $90 debt must be gone"
    );
    let left = fx
        .supply_of(VICTIM, &fx.zeroed)
        .expect("a partial seizure must leave a position behind");
    assert_eq!(
        left.scaled_amount,
        70 * RAY,
        "$30 of collateral seized at a zero bonus, no more and no less"
    );
    assert_eq!(
```
