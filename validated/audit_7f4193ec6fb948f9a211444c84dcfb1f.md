### Title
Delisted collateral remains risk-weighted for borrow and withdrawal gates - (contracts/controller/src/risk/totals.rs)

### Summary
XOXNO Lending marks each supply position with only a positive amount, LTV, liquidation threshold, liquidation bonus, and liquidation fee. `SpokeAssetConfig.is_collateralizable` controls whether an asset may enter as collateral, but it is not included when the account's existing supply positions are converted into `ltv_collateral` or `weighted_collateral`. Therefore, after governance sets `can_collateral` to `false`, the account owner can still use the old position as collateral for `borrow`, and it can still back outstanding debt during `withdraw`, flash-position, multiply, swap-collateral, and other strategy solvency gates.

### Finding Description
`process_borrow` calls `enforce_post_pool_solvency` after the pool borrows the requested assets, and `process_withdraw` calls the same gate after withdrawing collateral. `enforce_post_pool_solvency` first calls `restamp_listed_supply_ltv`, then calls `require_post_pool_risk_gates`. [1](#0-0) [2](#0-1) [3](#0-2) 

The vulnerability is that `restamp_listed_supply_ltv` only checks that the hub asset is still listed in the account's spoke. It does not check `SpokeAssetConfig.is_collateralizable`, does not zero the position's LTV, and does not remove the position from the account. It copies the current listed `loan_to_value` into every existing supply leg. [4](#0-3) 

`calculate_account_risk_totals_body` then iterates over every entry in `account.supply_positions`, values each leg, applies its stored effective LTV to `ltv_collateral`, and applies its stored liquidation threshold to `weighted_collateral`. There is no collateral-enabled check in this loop. [5](#0-4) 

The stored configuration does distinguish collateral eligibility from borrow eligibility, but the risk calculation receives only the position's `loan_to_value` and `liquidation_threshold`, not a predicate that suppresses disabled collateral. [6](#0-5) [7](#0-6) 

As a result, setting `can_collateral = false` prevents new supply but does not prevent old supply from being counted for:

```rust
ltv_collateral >= total_debt
health_factor >= 1e18
ltv_collateral >= min_borrow_collateral_usd_wad
```

Those are the three post-action solvency requirements enforced while debt remains. [8](#0-7) 

### Impact Explanation
Protocol insolvency and theft of pool liquidity are possible.

If governance disables collateral because the asset is vulnerable, illiquid, incorrectly priced, unsafe to seize, or otherwise unsuitable, existing holders can continue to extract liquidity against it. In the strongest path:

1. The account supplies asset `A` while `can_collateral = true`.
2. Governance edits the spoke listing and sets `can_collateral = false`, while retaining a nonzero LTV and liquidation threshold.
3. The account calls `borrow` for another listed borrowable asset.
4. `restamp_listed_supply_ltv` retains or refreshes the disabled asset's nonzero LTV because the asset is still listed.
5. `calculate_account_risk_totals` counts the disabled asset toward both LTV collateral and threshold-weighted collateral.
6. The borrow succeeds if the resulting totals satisfy the normal solvency gates.

The same account can also withdraw other healthy collateral while leaving only the disabled asset behind, provided that disabled asset's weighted and LTV value still covers the debt.

This weakens the intended emergency control. If collateral eligibility was disabled to prevent lending against a compromised asset, the protocol can still release good liquidity against that asset. If the asset later falls or cannot be liquidated safely, suppliers absorb the shortfall through bad debt or a supply-index write-down.

### Likelihood Explanation
Likelihood is moderate.

The exploit requires a governance configuration state in which a previously collateralizable asset remains listed but has `is_collateralizable = false` and nonzero stored LTV or liquidation threshold. That is plausible because `edit_asset_in_spoke` stores all of these fields independently and does not force `loan_to_value` or `liquidation_threshold` to zero when `can_collateral` is false. [9](#0-8) 

An unprivileged account owner or delegate can reach the vulnerable path through `borrow`, `withdraw`, `flash_position`, `multiply`, `swap_collateral`, `swap_debt`, or `repay_debt_with_collateral`. No leaked key, oracle manipulation, flash-loan exploit, or privileged user action is required after the disabled-collateral configuration exists.

### Recommendation
Do not allow `is_collateralizable = false` supply positions to contribute to risk-bearing collateral totals.

At minimum, make `restamp_listed_supply_ltv` or `calculate_account_risk_totals_body` treat non-collateralizable assets as zero collateral:

```rust
if !listed.is_collateralizable {
    continue;
}
```

This should apply consistently to both:

- `ltv_collateral`, used by borrow and withdrawal capacity;
- `weighted_collateral`, used by health factor and liquidation eligibility.

If an existing disabled asset must remain withdrawable, keep exit behavior open through the existing flag policy but exclude it from solvency calculations. A safer design is for governance edits that set `can_collateral = false` to require `ltv = 0`, `threshold = 0`, or both; however, relying on callers to keep those fields coherent is weaker than enforcing the exclusion directly in the risk engine.

### Proof of Concept
Conceptual transaction sequence for an unprivileged account owner:

1. Assume spoke `1` lists `(hub_id = 1, asset = RISKY)` with `can_collateral = true`, `ltv = 7500`, and `liquidation_threshold = 8000`.
2. Alice calls:

   ```text
   supply(
       caller = alice,
       account_id = 0,
       spoke_id = 1,
       assets = [((hub_id = 1, asset = RISKY), 1_000_000)]
   )
   ```

   The supply position is stored with nonzero `loan_to_value` and `liquidation_threshold`.

3. Governance later calls `edit_asset_in_spoke` for the same spoke asset with:

   ```text
   can_collateral = false
   can_borrow     = false
   ltv            = 7500
   threshold      = 8000
   ```

   The asset remains listed, so `cached_spoke_asset` still returns its configuration.

4. Alice calls:

   ```text
   borrow(
       caller = alice,
       account_id = alice_account,
       borrows = [((hub_id = 1, asset = USDC), borrow_amount)],
       to = alice
   )
   ```

5. During the post-pool solvency check:
   - `restamp_listed_supply_ltv` sees that `RISKY` is still listed and preserves/restamps its LTV;
   - `calculate_account_risk_totals_body` adds `RISKY`'s USD value to `ltv_collateral` and `weighted_collateral`;
   - the disabled asset therefore supplies the capacity that admits the USDC borrow.

6. Alternatively, Alice first borrows against both `RISKY` and healthy collateral, governance disables `RISKY`, and Alice calls `withdraw` for all healthy collateral. The withdrawal still passes if the disabled `RISKY` leg alone satisfies `ltv_collateral >= total_debt` and `health_factor >= 1 WAD`.

The decisive flaw is that the risk engine never tests `SpokeAssetConfig.is_collateralizable`; collateral eligibility affects admission but not the value of collateral that was admitted before the flag changed.

### Citations

**File:** contracts/controller/src/positions/debt.rs (L50-60)
```rust
    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);

    let restamped = enforce_post_pool_solvency(env, &mut cache, &mut account);
    let sides = if restamped {
```

**File:** contracts/controller/src/positions/supply.rs (L157-159)
```rust
    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);

```

**File:** contracts/controller/src/positions/mod.rs (L81-90)
```rust
/// Restamps listed supply LTVs, then checks collateral coverage, health factor,
/// and minimum borrow collateral. Returns whether any LTV changed.
pub(crate) fn enforce_post_pool_solvency(
    env: &Env,
    cache: &mut Context,
    account: &mut Account,
) -> bool {
    let restamped = risk::restamp_listed_supply_ltv(cache, account);
    validation::require_post_pool_risk_gates(env, cache, account);
    restamped
```

**File:** contracts/controller/src/risk/params.rs (L42-60)
```rust
/// Refreshes stored LTV snapshots in memory for listed supply assets, skipping
/// unlisted assets. Returns whether any position changed.
pub(crate) fn restamp_listed_supply_ltv(cache: &mut Context, account: &mut Account) -> bool {
    let mut changed = false;
    let keys = account.supply_positions.keys();
    for hub_asset in keys.iter() {
        let Some(listed) = cache.cached_spoke_asset(account.spoke_id, &hub_asset) else {
            continue;
        };
        let config: AssetConfig = (&listed).into();
        let Some(raw) = account.supply_positions.get(hub_asset.clone()) else {
            continue;
        };
        let mut position = AccountPosition::from(&raw);
        if position.loan_to_value.raw() == config.loan_to_value.raw() {
            continue;
        }
        position.loan_to_value = config.loan_to_value;
        update_or_remove_supply_position(account, &hub_asset, &position);
```

**File:** contracts/controller/src/risk/totals.rs (L168-198)
```rust
    let mut total_collateral = Wad::ZERO;
    let mut ltv_collateral = Wad::ZERO;
    let mut weighted_collateral = Wad::ZERO;
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );
        let gate_value = position_value_floor(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        total_collateral = total_collateral.checked_add(env, value);
        // A gated threshold can stay below refreshed LTV; clamp the borrow limit to it.
        let effective_ltv = position.loan_to_value.min(position.liquidation_threshold);
        ltv_collateral =
            ltv_collateral.checked_add(env, effective_ltv.apply_to_wad_floor(env, gate_value));
        weighted_collateral = weighted_collateral.checked_add(
            env,
            position
                .liquidation_threshold
                .apply_to_wad_floor(env, gate_value),
        );
```

**File:** common/src/types/controller.rs (L17-27)
```rust
pub struct AssetConfig {
    pub loan_to_value: Bps,

    pub liquidation_threshold: Bps,

    pub liquidation_bonus: Bps,

    pub liquidation_fees: Bps,
    pub is_collateralizable: bool,
    pub is_borrowable: bool,
}
```

**File:** common/src/types/controller.rs (L108-122)
```rust
#[contracttype]
#[derive(Clone, Debug)]
pub struct SpokeAssetConfig {
    pub is_collateralizable: bool,
    pub is_borrowable: bool,
    pub paused: bool,
    pub frozen: bool,

    pub no_seize: bool,
    pub loan_to_value: u32,
    pub liquidation_threshold: u32,
    pub liquidation_bonus: u32,
    pub liquidation_fees: u32,
    pub supply_cap: i128,
    pub borrow_cap: i128,
```

**File:** contracts/controller/src/risk/validation.rs (L27-60)
```rust
/// Requires debt coverage by LTV-weighted collateral, health factor >= 1, and
/// the configured collateral floor. Debt-free accounts skip all three checks.
pub(crate) fn require_post_pool_risk_gates(env: &Env, cache: &mut Context, account: &Account) {
    if account.debt_free() {
        return;
    }

    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    assert_with_error!(
        env,
        totals.ltv_collateral >= totals.total_debt,
        CollateralError::InsufficientCollateral
    );

    spec_hooks::solvency_gate_checked(account);

    assert_with_error!(
        env,
        totals.health_factor >= Wad::ONE,
        CollateralError::InsufficientCollateral
    );

    let floor = storage::get_min_borrow_collateral_usd_wad(env);
    if floor != 0 && totals.ltv_collateral.raw() < floor {
        panic_with_error!(env, CollateralError::MinBorrowCollateralNotMet);
    }

    require_whole_unit_collateral_floor(env, cache, account);
```

**File:** contracts/controller/src/config/asset.rs (L79-92)
```rust
    let config = SpokeAssetConfig {
        is_collateralizable: args.can_collateral,
        is_borrowable: args.can_borrow,
        paused: args.paused,
        frozen: args.frozen,
        no_seize: args.no_seize,
        loan_to_value: args.ltv,
        liquidation_threshold: args.threshold,
        liquidation_bonus: args.bonus,
        liquidation_fees: args.liquidation_fees,
        supply_cap: args.supply_cap,
        borrow_cap: args.borrow_cap,
    };
    storage::set_spoke_asset(env, args.spoke_id, &hub_asset, &config);
```
