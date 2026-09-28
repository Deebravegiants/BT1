### Title
Unauthorized third-party supply can downgrade a victim’s stored LTV and temporarily restrict account withdrawals - ([File: contracts/controller/src/positions/supply.rs])

### Summary
The controller intentionally allows any authenticated caller to top up an existing supply position on another account, but that deposit path also rewrites the victim’s stored `loan_to_value` from the current listing. After governance lowers an asset’s LTV, an attacker can spend a nominal amount of the asset to force the downgrade onto a victim without owner or delegate authorization. The lowered LTV is then used by the account’s solvency checks and can block otherwise-expected withdrawals or borrowing.

### Finding Description
`supply(caller, account_id, spoke_id, assets)` authenticates only the supplied `caller` and loads the target account with `AccountGuard::Supply`, which checks the spoke but does not require the caller to own or delegate-manage the account. [1](#0-0) [2](#0-1) 

For a nonzero `account_id`, `require_third_party_existing_supply` only verifies that each supplied `HubAssetKey` already exists in the victim’s `supply_positions`; it does not require consent before applying side effects to that position. [3](#0-2) 

After the pool accepts the measured deposit, `merge_supply_leg` calls `refresh_supply_risk_params` with `RiskRefreshScope::FullTuple`. [4](#0-3)  `refresh_supply_risk_params` unconditionally assigns `effective_config.loan_to_value` to the victim’s stored position before applying the gated liquidation tuple. [5](#0-4) 

The updated stamp is then persisted through `update_or_remove_supply_position`. [6](#0-5)  Subsequent withdrawals load the account and run `enforce_post_pool_solvency`, so the forced lower LTV can make a withdrawal revert even though the attacker’s top-up increased nominal collateral. [7](#0-6) 

### Impact Explanation
An unprivileged address can temporarily reduce the borrowing and withdrawal capacity of another account after an LTV reduction. The attacker only needs the target account id, its spoke id, an existing victim supply leg, and enough tokens to make a nonzero measured deposit.

This can temporarily freeze collateral that the victim expects to withdraw. In a debt-backed account, the forced LTV downgrade can make the post-withdrawal solvency check fail until the victim repays debt or market/risk parameters change. The existing security regression demonstrates the same attack shape: Bob tops up Alice’s existing USDC leg, Alice’s stored LTV changes from the prior listing value to `5_000`, and her attempted ETH borrow then fails with `INSUFFICIENT_COLLATERAL`. [8](#0-7) 

### Likelihood Explanation
Likelihood depends on governance lowering an asset’s LTV while a victim retains a stale higher LTV and an attacker is willing to donate a small amount to that victim’s existing supply leg. No privileged role, victim signature, delegate grant, unhealthy account, oracle manipulation, or special contract callback is required.

The attacker can repeat the action for any account already holding the affected supply asset. The attack is limited to existing supply legs and cannot itself create a new victim asset slot. [9](#0-8) 

### Recommendation
Do not let a third-party supply refresh mutable risk terms on an account it does not control.

One approach is to split supply merging into two modes:

- For owner/delegate supply, preserve `RiskRefreshScope::FullTuple`.
- For third-party top-up, update only the supply-share balance and market index, leaving `loan_to_value`, `liquidation_threshold`, `liquidation_bonus`, and `liquidation_fees` untouched.
- Let the owner/delegate or an explicit permissionless risk-maintenance path apply the current risk tuple under the intended gates.

Alternatively, require owner/delegate authority for all existing-account `supply` calls and keep only `account_id == 0` open for new caller-owned accounts.

### Proof of Concept
1. Alice creates a leveraged account with USDC collateral under the old USDC LTV.
2. Governance lowers USDC’s listed `loan_to_value`, while Alice’s existing supply position retains its stale LTV snapshot.
3. Bob calls:

```text
controller::supply(
    caller = BOB,
    account_id = ALICE_ACCOUNT_ID,
    spoke_id = ALICE_SPOKE_ID,
    assets = [(HubAssetKey { hub_id, asset = USDC }, 1)]
)
```

4. `AccountGuard::Supply` does not require Bob to be Alice’s owner or delegate. [10](#0-9) 
5. The third-party check passes because Alice already has a USDC supply position. [9](#0-8) 
6. `merge_supply_leg` refreshes Alice’s position and `refresh_supply_risk_params` writes the lowered LTV. [11](#0-10) [12](#0-11) 
7. Alice’s reduced LTV is now enforced by later withdrawal/borrow solvency checks, as demonstrated by the repository regression where Bob’s top-up causes Alice’s `3.5 ETH` borrow attempt to revert. [13](#0-12)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L40-62)
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

```

**File:** contracts/controller/src/positions/supply.rs (L76-97)
```rust
/// Restricts third parties to existing supply positions. New accounts are
/// exempt because the caller becomes their owner.
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

**File:** contracts/controller/src/positions/supply.rs (L147-158)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);
```

**File:** contracts/controller/src/positions/supply.rs (L273-296)
```rust
/// Merges a supply result, refreshing risk parameters and updating usage,
/// market index, and event state.
pub(crate) fn merge_supply_leg(
    env: &Env,
    account: &mut Account,
    action: &PoolAction,
    result: &PoolPositionMutation,
    cache: &mut Context,
) {
    let hub_asset = &action.hub_asset;
    let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, hub_asset);

    let mut position = account.get_or_create_supply_position(hub_asset, &asset_config);
    let old_scaled = position.scaled_amount;

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

**File:** contracts/controller/src/positions/supply.rs (L298-324)
```rust
    let outcome = LegOutcome::from(result);
    position.scaled_amount = outcome.new_scaled;

    apply_leg_usage(
        env,
        cache,
        account.spoke_id,
        UsageSide::Supply,
        hub_asset,
        LegDirection::Entry {
            asset_decimals: result.asset_decimals,
        },
        old_scaled,
        &outcome,
    );

    cache.put_market_index(hub_asset, &outcome.market_index);
    cache.record_supply_position_update(
        events::PositionAction::Supply,
        hub_asset,
        outcome.market_index.supply_index,
        action.amount,
        &position,
    );

    update_or_remove_supply_position(account, hub_asset, &position);
}
```

**File:** contracts/controller/src/account.rs (L98-111)
```rust
    let account = storage::get_account(env, account_id);
    match guard {
        AccountGuard::Supply => require_spoke_match(env, &account, spoke_id),
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
        AccountGuard::Multiply => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
            assert_with_error!(env, account.mode == mode, GenericError::AccountModeMismatch);
        }
    }
    (account_id, account)
```

**File:** contracts/controller/src/risk/params.rs (L23-40)
```rust
/// Refreshes LTV; `FullTuple` also applies gated liquidation parameters.
/// Returns whether the in-memory position changed.
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

**File:** tests/test-harness/tests/controller/security_audit.rs (L507-531)
```rust
#[test]
fn poc_third_party_top_up_force_restamps_ltv() {
    let mut t = LendingTest::new().standard_two_asset_dust_disabled();

    t.supply(ALICE, "USDC", 10_000.0);
    let id = t.resolve_account_id(ALICE);

    t.edit_asset_config("USDC", |c| {
        c.loan_to_value = 5_000;
        c.liquidation_threshold = 5_500;
    });

    t.try_supply_to_account(BOB, ALICE, "USDC", 1.0)
        .expect("third-party top-up of existing leg allowed");
    let (ltv, _) = supply_ltv_and_lt(&t, id, "USDC");
    assert_eq!(
        ltv, 5_000,
        "H-RISK-03: third-party top-up force-restamps LTV"
    );

    let blocked = t.try_borrow(ALICE, "ETH", 3.5);
    assert_contract_error(blocked, errors::INSUFFICIENT_COLLATERAL);

    t.borrow(ALICE, "ETH", 2.0);
    t.assert_healthy(ALICE);
```
