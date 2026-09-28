### Title
Stale delegate authorization reactivates after position NFT transfer round-trip - (File: contracts/controller/src/storage/account.rs)

### Summary
Delegate grants are keyed only by `account_id` and stamped with the granting owner's address. An NFT transfer makes the old grant inactive, but does not delete it; if the NFT later returns to that owner, the same delegates regain full borrowing and withdrawal authority without a fresh authorization.

### Finding Description
`get_delegates` loads `ControllerKey::Delegates(account_id)` and returns its list whenever `grant.granted_by` equals the current NFT owner [1](#0-0) . Nothing records an ownership generation or clears the grant when ownership changes. The authorization check accepts a caller when it is an active position manager and appears in that returned list [2](#0-1) .

Consequently, a grant survives an intervening owner unless that owner happens to call `add_delegate` or `remove_delegate`. `add_delegate` overwrites stale grants, but no transfer path performs that write automatically [3](#0-2) . Once the NFT returns to the original owner, `owner == granted_by` again and the stale delegate list is live.

The revived authority is economically significant: `borrow` lets a delegate choose any external `to` recipient [4](#0-3) , and `withdraw` likewise sends collateral to a caller-selected external recipient [5](#0-4) .

### Impact Explanation
Theft of user funds. A formerly appointed position manager can withdraw the account's transferable collateral or borrow up to the account's solvency limit to itself immediately after the NFT returns to the original owner. The delegate does not need the current owner's fresh signature, and the owner may reasonably believe the delegation ended when the position was transferred.

### Likelihood Explanation
The attack requires the account NFT to return to the grantor before an intervening owner changes the delegate list. That can occur through a sale-and-repurchase, temporary custody transfer, marketplace settlement flow, or accidental transfer. The attacker only needs to remain an active registered position manager and invoke `borrow` or `withdraw`.

### Recommendation
Invalidate delegate grants permanently across every ownership change, not merely while another owner holds the NFT. Track an NFT ownership generation/transfer epoch and include it in `DelegateGrant`, or have the position NFT notify the controller on transfer so the controller can clear `Delegates(account_id)`. If neither is feasible, record and update a controller-side last-owner/epoch marker on account access so a grant created before an ownership interval cannot become valid again.

### Proof of Concept
1. Alice creates account `A` and calls `add_delegate(ALICE, A, MANAGER)`.
2. Alice transfers NFT `A` to Bob. `MANAGER` is inactive because `Bob != grant.granted_by`.
3. Bob performs no `add_delegate` or `remove_delegate` call, leaving the stale Alice-stamped grant untouched.
4. Bob transfers NFT `A` back to Alice.
5. `MANAGER` calls `borrow(caller=MANAGER, account_id=A, borrows=[...], to=Some(MANAGER))` or `withdraw(..., to=Some(MANAGER))`.
6. `require_owner_or_delegate` succeeds because the stored grant's `granted_by` again equals Alice, and the pool pays the borrowed or withdrawn assets to `MANAGER`, subject to post-operation solvency checks.

### Citations

**File:** contracts/controller/src/storage/account.rs (L174-180)
```rust
/// Returns grants stamped by `owner`, or an empty list. Ownership changes
/// invalidate a previous owner's grants without deleting them.
pub(crate) fn get_delegates(env: &Env, account_id: u64, owner: &Address) -> Vec<Address> {
    get_user::<DelegateGrant>(env, &ControllerKey::Delegates(account_id))
        .filter(|grant| grant.granted_by == *owner)
        .map(|grant| grant.delegates)
        .unwrap_or_else(|| Vec::new(env))
```

**File:** contracts/controller/src/storage/account.rs (L201-220)
```rust
/// Adds a delegate, enforcing `MAX_DELEGATES`; returns false for duplicates.
/// Overwrites stale grants with a list stamped by the current owner.
pub(crate) fn add_delegate(
    env: &Env,
    account_id: u64,
    owner: &Address,
    delegate: &Address,
) -> bool {
    let mut delegates = get_delegates(env, account_id, owner);
    if delegates.contains(delegate) {
        return false;
    }
    assert_with_error!(
        env,
        delegates.len() < MAX_DELEGATES,
        GenericError::RegistryCapReached
    );
    delegates.push_back(delegate.clone());
    set_delegates(env, account_id, owner, &delegates);
    true
```

**File:** contracts/controller/src/account.rs (L114-127)
```rust
/// Accepts the owner or a registered, active manager delegated by that owner.
pub(crate) fn is_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) -> bool {
    if caller == owner {
        return true;
    }
    let active_manager =
        storage::get_position_manager(env, caller).is_some_and(|config| config.is_active);
    active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
}
```

**File:** contracts/controller/src/positions/debt.rs (L40-57)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/supply.rs (L147-157)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
```
