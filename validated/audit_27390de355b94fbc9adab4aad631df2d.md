### Title
Permissionless `update_account_threshold` lets any address restamp a foreign account's LTV snapshot and freeze its withdrawals - (File: contracts/controller/src/risk/params.rs)

### Summary
`update_account_threshold` is a permissionless keeper entrypoint: any authenticated caller may pass arbitrary `account_ids` and refresh their cached risk parameters. With `has_risks = false` (`RiskRefreshScope::LtvOnly`), `refresh_supply_risk_params` unconditionally overwrites each listed supply position's `loan_to_value` with the current listed config value, with no health-factor gate and no ownership check on the target account. After governance lowers an asset's LTV, an attacker can force-apply the reduced LTV to any victim account, breaking that account's post-pool solvency check and blocking its `withdraw` calls — a direct-object-reference-style state manipulation on an account the caller does not own.

### Finding Description
The controller stores a per-position LTV snapshot on each `AccountPosition`, restamped lazily rather than read live from the listing. Two properties combine into the bug:

1. `update_account_threshold(caller, has_risks, account_ids)` requires only `caller.require_auth()` and iterates attacker-supplied `account_ids` through `sync_account_thresholds`, which never checks that the caller owns or is delegated on the target account. [1](#0-0) 
2. `refresh_supply_risk_params` sets `position.loan_to_value = effective_config.loan_to_value` unconditionally; only the liquidation tuple is gated by `favors_liquidator` plus the HF ≥ 1.05 floor. So `LtvOnly` restamps always succeed even on deeply indebted accounts. [2](#0-1) 

`sync_account_thresholds` skips missing metadata and unresolved NFT owners but applies the LTV write to any resolvable account with supply positions, persisting via `set_supply_positions`. [3](#0-2) 

On the victim side, `process_withdraw` runs `enforce_post_pool_solvency` after paying out, which requires LTV-weighted collateral to cover outstanding debt (and, with debt remaining, the minimum-borrow floor). A freshly lowered LTV reduces the weighted collateral, so an account that was solvent under its stale higher LTV can now fail the check and revert every withdrawal until the debt is reduced. [4](#0-3) 

The same unconditional restamp is reachable by a third party via `supply` (top-up of an existing supply asset passes `require_third_party_existing_supply`, then `merge_supply_leg` calls `refresh_supply_risk_params` with `RiskRefreshScope::FullTuple`, which still sets LTV unconditionally), but `update_account_threshold` is the cleaner path since it needs no tokens. [5](#0-4) 

### Impact Explanation
Temporary freezing of user funds. After a governance LTV reduction on an asset, any unprivileged address can restamp the lowered LTV onto arbitrary indebted accounts by referencing their `account_id`s, causing those accounts' `withdraw` (and `borrow`) calls to revert on the post-pool solvency check. Victims cannot restore the prior LTV — it is derived from the listing — so collateral remains locked until victims repay debt out of pocket. Only the liquidation-tuple restamp is HF-gated; the LTV leg has no protection despite directly controlling withdrawal solvency.

### Likelihood Explanation
Requires a prior (or future) LTV reduction on a listed spoke asset — a routine risk-parameter change — and a target account holding that asset as supply with outstanding debt. Execution is a single cheap permissionless call over a batch of `account_ids`, so an attacker can freeze many accounts at once. No funding, timing race, or privileged access is needed. Severity is bounded to Medium: funds are locked, not stolen, and liquidation thresholds are separately gated so this cannot force liquidations.

### Recommendation
Gate `LtvOnly` restamps the same way the liquidation tuple is gated: when the listed LTV is lower than the stored snapshot and the account carries debt, require the account to clear a minimum health factor under the new LTV before applying it, or restrict permissionless `update_account_threshold` to owner/delegate-initiated calls and keep permissionless restamping only for LTV increases. Alternatively, apply the reduced LTV only to new borrows and let withdrawals evaluate against the stored snapshot.

### Proof of Concept
1. Governance lists USDC in spoke `S` with LTV 8000 BPS. Alice supplies 100 USDC (account `A`) and borrows 70 USD of ETH — solvent at LTV 0.8.
2. Governance later reduces USDC LTV to 6000 BPS. Stored snapshots are unchanged; Alice can still withdraw down to the old limit.
3. Attacker (any address) calls `update_account_threshold(attacker, false, [A])`. `sync_account_thresholds` resolves `A`, writes `loan_to_value = 6000` into Alice's USDC supply position via `refresh_supply_risk_params`, and persists it with `set_supply_positions`. No auth or HF check applies to the LTV leg.
4. Alice calls `withdraw(A, [(USDC, x)])` for any `x` that kept LTV-weighted collateral ≥ debt under 8000 BPS but not under 6000 BPS; `enforce_post_pool_solvency` reverts. Alice's collateral is frozen until she repays enough debt to satisfy the lower LTV — a state change on her account that she never authorized.

### Citations

**File:** contracts/controller/src/risk/params.rs (L25-40)
```rust
pub(crate) fn refresh_supply_risk_params(
    env: &Env,
    cache: &mut Context,
    account: &Account,
    hub_asset: &HubAssetKey,
    position: &mut AccountPosition,
    effective_config: &AssetConfig,
    scope: RiskRefreshScope,
) -> bool {
    let before = *position;
    position.loan_to_value = effective_config.loan_to_value;
    if scope == RiskRefreshScope::FullTuple {
        apply_gated_liquidation_params(env, cache, account, hub_asset, position, effective_config);
    }
    *position != before
}
```

**File:** contracts/controller/src/risk/params.rs (L124-144)
```rust
pub(crate) fn update_account_threshold(
    env: &Env,
    caller: Address,
    has_risks: bool,
    account_ids: Vec<u64>,
) {
    validation::require_authorized_caller(env, &caller);

    let scope = if has_risks {
        RiskRefreshScope::FullTuple
    } else {
        RiskRefreshScope::LtvOnly
    };

    let mut cache = Context::new(env);

    for account_id in account_ids {
        cache.reset_spoke_context();
        sync_account_thresholds(env, account_id, scope, &mut cache);
    }
}
```

**File:** contracts/controller/src/risk/params.rs (L149-219)
```rust
fn sync_account_thresholds(
    env: &Env,
    account_id: u64,
    scope: RiskRefreshScope,
    cache: &mut Context,
) {
    let Some(meta) = storage::try_get_account_meta(env, account_id) else {
        return;
    };

    let supply_positions = storage::get_supply_positions(env, account_id);
    if supply_positions.is_empty() {
        return;
    }

    // Fail closed: never update an account whose NFT owner cannot be resolved.
    let Some(owner) = storage::try_account_owner(env, account_id) else {
        return;
    };

    let full_tuple = scope == RiskRefreshScope::FullTuple;
    let borrow_positions = if full_tuple {
        storage::get_debt_positions(env, account_id)
    } else {
        Map::new(env)
    };

    storage::renew_user_account(env, account_id);

    let mut account = storage::account_from_parts(owner, meta, supply_positions, borrow_positions);
    let assets = account.supply_positions.keys();

    let mut any_changed = false;
    for hub_asset in assets.iter() {
        let Some(spoke_config) = cache.cached_spoke_asset(account.spoke_id, &hub_asset) else {
            continue;
        };
        let asset_config = AssetConfig::from(&spoke_config);

        let raw = expect_invariant(env, account.supply_positions.get(hub_asset.clone()));
        let mut updated = AccountPosition::from(&raw);

        let changed = refresh_supply_risk_params(
            env,
            cache,
            &account,
            &hub_asset,
            &mut updated,
            &asset_config,
            scope,
        );
        if !changed {
            continue;
        }

        any_changed = true;
        update_or_remove_supply_position(&mut account, &hub_asset, &updated);

        let market_index = cache.cached_market_index(&hub_asset);
        cache.record_supply_position_update(
            events::PositionAction::ParamUpd,
            &hub_asset,
            market_index.supply_index.raw(),
            0,
            &updated,
        );
    }

    if any_changed {
        storage::set_supply_positions(env, account_id, &account.supply_positions);
    }
```

**File:** contracts/controller/src/positions/supply.rs (L78-97)
```rust
fn require_third_party_existing_supply(
    env: &Env,
    account_id: u64,
    resolved_account_id: u64,
    caller: &Address,
    account: &Account,
    aggregated: &AggregatedPayments,
) {
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
}
```

**File:** contracts/controller/src/positions/supply.rs (L140-168)
```rust
pub(crate) fn process_withdraw(
    env: &Env,
    caller: &Address,
    account_id: u64,
    withdrawals: &Vec<HubPayment>,
    to: Option<Address>,
) -> Vec<HubPayment> {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);

    finalize_position_flow(
        env,
        account_id,
        &account,
        &mut cache,
        PositionSides::Supply,
        true,
    );
    paid
```
