### Title
Third-party `supply` restamps a victim account's cached LTV/liquidation-threshold without ownership check, enabling forced liquidation - (File: contracts/controller/src/positions/supply.rs)

### Summary
`process_supply` deliberately lets any unprivileged caller add funds to another account's *existing* supply position (`AccountGuard::Supply` + `require_third_party_existing_supply`). The check that stands in for ownership only restricts *which* assets may be supplied — it does not prevent the side effect of the deposit: `merge_supply_leg` calls `refresh_supply_risk_params` with `RiskRefreshScope::FullTuple`, which restamps the victim's cached per-position `loan_to_value`/`liquidation_threshold` from the *current* `SpokeAssetConfig`. When governance has tightened risk parameters since the victim entered, a dust third-party supply silently applies the worse parameters to the victim's position, dropping its health factor below 1 and exposing it to liquidation — the same shape as the Octavia bug: an authentication gate that exists but is configured so weakly (`spoke match + position exists` instead of `owner`) that a security-sensitive action runs without the account holder's authorization.

### Finding Description
In `load_or_create_account`, the `Supply` guard performs only `require_spoke_match` — no owner/delegate check [1](#0-0) . The compensating check `require_third_party_existing_supply` merely asserts each supplied `hub_asset` already exists in `account.supply_positions` [2](#0-1) . It does not constrain *amount* or the downstream effect. Inside `process_deposit`/`merge_supply_leg`, every leg unconditionally runs `refresh_supply_risk_params(..., RiskRefreshScope::FullTuple)` [3](#0-2) , overwriting the position's cached risk tuple with the live config. The design elsewhere relies on cached thresholds only being restamped on owner-initiated flows (the dedicated `update_account_threshold` entrypoint exists precisely so holders control when new risk parameters are applied to their position). The supply path is an unauthorized equivalent: a stranger can force the restamp by supplying a minimal amount of an asset the victim already holds.

### Impact Explanation
When `edit_asset_in_spoke`/`set_spoke_asset_flags` tightens `ltv`/`threshold` on an asset, existing positions keep their stale, more favorable cached tuple until they are touched — that is the documented cached-risk model. A forced restamp lowers the victim's effective collateral value, which can push `health_factor` under 1. The attacker then calls `liquidate` and seizes collateral with the HF-based bonus — direct theft of user funds the victim would not have lost had the restamp awaited an owner-authorized action. Cost to the attacker is a dust supply of an asset the victim already holds plus the liquidation call.

### Likelihood Explanation
Requires: (a) a risk-parameter tightening on an asset in the victim's spoke after the victim last touched that position, and (b) the victim's HF sitting close enough to 1 that the restamp crosses it. Risk-parameter reductions are a routine governance operation; leveraged positions near their threshold are the norm. The attack is atomic from the attacker's side (supply dust → liquidate), so the window is fully exploitable whenever it opens.

### Recommendation
Extend `require_third_party_existing_supply` so third-party legs do not restamp risk parameters — i.e., in `merge_supply_leg`, skip `refresh_supply_risk_params` (or use a scope that preserves the cached `ltv`/`threshold`) when `caller` is not owner/delegate of the account. Alternatively, restrict third-party top-ups to non-collateralizable assets, or require `is_owner_or_delegate` for any supply that would trigger `FullTuple` restamping.

### Proof of Concept
1. Victim owns `account_id` in `spoke_id` with a supply position in asset `A` and debt near its threshold; cached `liquidation_threshold` on the `A` position is the old, higher value.
2. Governance executes `edit_asset_in_spoke` lowering `A`'s `threshold`/`ltv` in that spoke. Victim does not call `update_account_threshold`.
3. Attacker calls `supply(account_id = victim's, spoke_id, assets = [(hub_asset(A), dust)])` signed only by the attacker.
4. `require_third_party_existing_supply` passes because `A` is already a key in `supply_positions`; `merge_supply_leg` restamps the victim's `A` position to the new lower threshold.
5. Victim's HF computed on the restamped tuple is now `< 1`. Attacker calls `liquidate` on the victim account and captures the liquidation bonus on the seized collateral.

Caveat: this hinges on `update_account_threshold` being owner-gated (so the restamp is otherwise unreachable by strangers); I could not fully verify that entrypoint's auth within this pass — if it is already permissionless to restamp any account, the supply path adds no new capability and the finding reduces to no-impact.

### Citations

**File:** contracts/controller/src/account.rs (L99-104)
```rust
    match guard {
        AccountGuard::Supply => require_spoke_match(env, &account, spoke_id),
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
```

**File:** contracts/controller/src/positions/supply.rs (L86-96)
```rust
    if account_id != 0
        && !account::is_owner_or_delegate(env, resolved_account_id, caller, &account.owner)
    {
        for (hub_asset, _) in aggregated.iter() {
            assert_with_error!(
                env,
                account.supply_positions.contains_key(hub_asset.clone()),
                GenericError::NotAuthorized
            );
        }
    }
```

**File:** contracts/controller/src/positions/supply.rs (L288-296)
```rust
    refresh_supply_risk_params(
        env,
        cache,
        account,
        hub_asset,
        &mut position,
        &asset_config,
        RiskRefreshScope::FullTuple,
    );
```
