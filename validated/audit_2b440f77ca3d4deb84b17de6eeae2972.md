### Title

Dust supply position indefinitely blocks owner removal of a spoke asset - ([File: contracts/controller/src/config/asset.rs])

### Summary

An unprivileged user can prevent `remove_asset_from_spoke` by leaving the smallest position that mints a nonzero RAY supply share in the targeted `(spoke_id, hub_asset)`. The owner-only removal path requires both `supplied_scaled_ray` and `borrowed_scaled_ray` to equal zero, so one dust position makes the operation revert with `SpokeAssetInUse` until every holder exits. [1](#0-0) 

### Finding Description

`Controller::supply` is reachable by an ordinary authenticated caller, and `account_id = 0` creates a new account owned by that caller. [2](#0-1) [3](#0-2) 

The supplied amount is converted into a supply position through `process_deposit`, `pool_supply_call`, and `merge_supply_leg`; the finalization path persists the corresponding spoke usage. [4](#0-3) [5](#0-4) 

`remove_asset_from_spoke` is owner-only and unconditionally rejects removal when either side of the aggregated spoke-usage row is nonzero. [6](#0-5) [7](#0-6) 

There is no dust threshold or owner override in this check; the existing test confirms that live supply usage causes `SPOKE_ASSET_IN_USE` and that removal succeeds only after the position is fully withdrawn. [8](#0-7) 

### Impact Explanation

A malicious user can indefinitely keep a listed asset non-removable by maintaining a dust supply position, or by re-entering with dust whenever the listing remains open. [7](#0-6) 

This denies governance a state-changing administrative operation and can prevent retirement of an unused or undesirable market listing. Because usage is tracked in RAY shares rather than token value, the attacker’s cost can be limited to the smallest amount that produces nonzero shares. [9](#0-8) 

The issue does not require a token donation to the pool or controller: the blocking state is created through the normal `supply` entrypoint and persists as an account position. [10](#0-9) 

### Likelihood Explanation

The attacker needs only an address, authorization for `caller`, and enough of the listed asset to mint nonzero supply shares. [11](#0-10) 

The action is not a privileged parameter change, leaked-key scenario, token-behavior assumption, or external-service failure. A dust supply in a normal account directly creates the nonzero `supplied_scaled_ray` precondition that makes the owner call fail. [1](#0-0) 

Governance cannot clear the blocking supply by changing flags or caps, because those controls restrict future actions and do not delete an existing position or its usage row. Missing listings otherwise remain exitable, so the zero-usage precondition is not needed to make post-removal withdrawal work. [12](#0-11) 

### Recommendation

Allow the owner to remove a spoke listing even when usage is nonzero, or add an explicit forced-removal path that preserves existing-position exit, repayment, and liquidation behavior. Missing listings already remain exitable and seizable, so removal does not have to wait for all usage to reach zero. [12](#0-11) 

If the strict zero-usage invariant must be retained for ordinary removal, add a governance-approved forced path that deletes the listing while leaving positions usable for debt-reducing and exit-only flows. A value-based dust allowance alone should not be the only fix because a nonzero scaled position can still represent live accounting. [13](#0-12) 

### Proof of Concept

1. Assume governance has listed `hub_asset = {hub_id: H, asset: A}` in active spoke `S`. [14](#0-13) 
2. An attacker calls `supply(caller = attacker, account_id = 0, spoke_id = S, assets = [(hub_asset, dust_amount)])`, choosing the smallest `dust_amount` that mints nonzero supply shares. [11](#0-10) 
3. The controller transfers the measured amount to the pool, creates the supply position, merges the supply leg, and persists nonzero `supplied_scaled_ray` for `(S, hub_asset)`. [15](#0-14) [16](#0-15) 
4. The owner calls `remove_asset_from_spoke(hub_asset, S)`. The call reaches the usage assertion and reverts with `SpokeAssetInUse` because `usage.supplied_scaled_ray != 0`. [7](#0-6) 
5. The block persists until the attacker fully withdraws; if removal is attempted while the listing is still usable, another unprivileged account can recreate the dust position before execution. [8](#0-7)

### Citations

**File:** contracts/controller/src/config/asset.rs (L189-203)
```rust
/// Removes and emits a listed asset only when both scaled usage amounts are zero.
pub(crate) fn remove_asset_from_spoke(env: &Env, hub_asset: HubAssetKey, spoke_id: u32) {
    assert_with_error!(
        env,
        storage::get_spoke_asset(env, spoke_id, &hub_asset).is_some(),
        SpokeError::AssetNotInSpoke
    );
    let usage = storage::get_spoke_usage(env, spoke_id, &hub_asset).unwrap_or_default();
    assert_with_error!(
        env,
        usage.supplied_scaled_ray == 0 && usage.borrowed_scaled_ray == 0,
        SpokeError::SpokeAssetInUse
    );

    storage::remove_spoke_asset(env, spoke_id, &hub_asset);
```

**File:** contracts/controller/src/positions/supply.rs (L40-63)
```rust
pub(crate) fn process_supply(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    assets: &Vec<HubPayment>,
) -> u64 {
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);

    process_deposit(env, caller, &mut account, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/supply.rs (L99-135)
```rust
/// Checks supply entry gates and credits measured pool receipts.
pub(crate) fn process_deposit(
    env: &Env,
    caller: &Address,
    account: &mut Account,
    aggregated: &AggregatedPayments,
    cache: &mut Context,
) {
    validate_position_entry_gates(
        env,
        account,
        aggregated,
        cache,
        AccountPositionType::Deposit,
    );
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolSupplyEntry> = Vec::new(env);
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_supply_leg(env, account, &entry.action, &result, cache);
    });
```

**File:** contracts/controller/src/account.rs (L83-97)
```rust
/// Creates an account for `caller` when `account_id` is zero; otherwise loads it.
/// Existing accounts require a matching spoke. `Migrate` also requires an owner
/// or active delegate; `Multiply` additionally requires a matching mode.
pub(crate) fn load_or_create_account(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    mode: PositionMode,
    guard: AccountGuard,
    cache: &mut Context,
) -> (u64, Account) {
    if account_id == 0 {
        return create_account(env, caller, spoke_id, mode, cache);
    }
```

**File:** contracts/controller/src/positions/mod.rs (L172-183)
```rust
/// Persists spoke usage and positions, then emits the position-update batch.
pub(crate) fn finalize_position_flow(
    env: &Env,
    account_id: u64,
    account: &Account,
    cache: &mut Context,
    sides: PositionSides,
    remove_if_empty: bool,
) {
    cache.persist_spoke_usage();
    persist_account_positions(env, account_id, account, sides, remove_if_empty);
    cache.emit_position_batch(account_id, account);
```

**File:** contracts/controller/src/positions/mod.rs (L255-277)
```rust
/// Enforces the leg's halt policy. Missing listings remain exitable and
/// seizable so delisting cannot strand positions or prevent liquidation.
pub(crate) fn enforce_spoke_asset_flags(
    env: &Env,
    cache: &mut Context,
    spoke_id: u32,
    hub_asset: &HubAssetKey,
    freeze: FreezePolicy,
) {
    if let Some(sa) = cache.cached_spoke_asset(spoke_id, hub_asset) {
        match freeze {
            FreezePolicy::BlockOnEntry => {
                assert_with_error!(env, !sa.paused, SpokeError::SpokeAssetPaused);
                assert_with_error!(env, !sa.frozen, SpokeError::SpokeAssetFrozen);
            }
            FreezePolicy::AllowOnExit => {
                assert_with_error!(env, !sa.paused, SpokeError::SpokeAssetPaused);
            }
            FreezePolicy::SeizureLeg => {
                assert_with_error!(env, !sa.no_seize, SpokeError::SpokeAssetSeizureHalted);
            }
        }
    }
```

**File:** contracts/controller/src/lib.rs (L712-718)
```rust
    /// Removes a listed spoke asset with no supply or borrow usage. Owner-only.
    #[only_owner]
    fn remove_asset_from_spoke(env: Env, hub_asset: HubAssetKey, spoke_id: u32) {
        renew_then!(
            env,
            config::asset::remove_asset_from_spoke(&env, hub_asset, spoke_id)
        )
```

**File:** tests/test-harness/tests/controller/spoke.rs (L1133-1152)
```rust
#[test]
fn test_remove_asset_with_live_supply_usage_reverts_until_drained() {
    let mut t = LendingTest::new().stablecoin_spoke_two_asset().build();

    t.create_spoke_account(ALICE, 2);
    t.supply(ALICE, "USDT", 1_000.0);

    let usdt = t.resolve_asset("USDT");
    let result = t
        .ctrl_client()
        .try_remove_asset_from_spoke(&hub_asset(usdt), &2u32);
    let flat: Result<(), soroban_sdk::Error> = match result {
        Ok(Ok(_)) => panic!("expected contract error, got Ok"),
        Ok(Err(err)) => Err(err.into()),
        Err(e) => Err(e.expect("expected contract error, got InvokeError")),
    };
    assert_contract_error(flat, errors::SPOKE_ASSET_IN_USE);

    t.withdraw_all(ALICE, "USDT");
    t.remove_asset_from_spoke("USDT", 2);
```

**File:** contracts/controller/src/storage/spoke.rs (L77-99)
```rust
/// Returns scaled supply and debt usage in RAY, renewing shared TTL if present.
pub(crate) fn get_spoke_usage(
    env: &Env,
    spoke_id: u32,
    hub_asset: &HubAssetKey,
) -> Option<SpokeUsageRaw> {
    get_shared(env, &ControllerKey::SpokeUsage(spoke_id, hub_asset.clone()))
}

/// Stores usage and renews shared TTL; deletes the row when both sides are zero.
pub(crate) fn set_spoke_usage(
    env: &Env,
    spoke_id: u32,
    hub_asset: &HubAssetKey,
    usage: &SpokeUsageRaw,
) {
    let key = ControllerKey::SpokeUsage(spoke_id, hub_asset.clone());

    if usage.supplied_scaled_ray == 0 && usage.borrowed_scaled_ray == 0 {
        env.storage().persistent().remove(&key);
    } else {
        set_shared(env, &key, usage);
    }
```
