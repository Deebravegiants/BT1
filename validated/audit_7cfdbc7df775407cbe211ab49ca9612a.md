### Title
Delegate authorization survives NFT transfer and revives when the account returns - (File: `contracts/controller/src/storage/account.rs`)

### Summary

A delegate grant is keyed by `account_id` and stamped only with `granted_by`; an NFT transfer hides it from the new owner but does not delete it. If the position NFT is transferred back to the original owner, the old grant becomes active again without any fresh `add_delegate` authorization. The previously approved manager can then borrow or withdraw the account’s assets.

### Finding Description

The controller resolves account ownership dynamically through the position NFT and checks whether the caller is either that owner or an active position manager listed in `Delegates(account_id)` for the current owner. [1](#0-0) [2](#0-1) 

`get_delegates` filters the stored `DelegateGrant` by `granted_by == owner`, so transferring the NFT makes the old grant inaccessible to the new owner while leaving the storage entry intact. [3](#0-2)  The stored type explicitly preserves `granted_by` and the delegate list across ownership changes. [4](#0-3) 

Because there is no transfer hook, owner epoch, or grant generation, a later transfer back to `granted_by` makes the same grant satisfy the authorization check again. Delegate authority is economically significant: `withdraw` permits the delegate to choose an external recipient, and `borrow` likewise permits an arbitrary recipient subject to solvency checks. [5](#0-4) [6](#0-5) 

The only purge paths require the intervening owner to call `remove_delegate` or overwrite the list through `add_delegate`; an ordinary transfer does not purge it. [7](#0-6) 

### Impact Explanation

The dormant manager regains account control if the NFT ever returns to the granting address. It can withdraw collateral to itself, or borrow up to the account’s LTV limit to itself and leave the victim with the debt. This is theft of user funds and can make the position insolvent.

### Likelihood Explanation

A victim must first grant an approved position manager and the NFT must later pass through another owner before returning to the victim. Such round trips can occur through custody changes, marketplace purchases, account recovery, or temporary transfers. No attacker needs administrator access during the exploit: once the dormant grant reactivates, the manager itself can invoke `borrow` or `withdraw` with its own authorization.

### Recommendation

Invalidate grants permanently on NFT ownership changes or version them.

Preferred options:

- Store a monotonically increasing ownership epoch or NFT transfer counter in `AccountMeta`/`DelegateGrant`, and require the grant’s epoch to match the current epoch.
- Alternatively, have the controller expose a transfer-aware lifecycle operation that clears `Delegates(account_id)` whenever ownership changes.
- At minimum, make `PositionNft` invoke a controller callback on successful transfer so `Delegates(account_id)` is deleted atomically with the ownership change.

The invariant should become: a grant is valid only for the continuous ownership period in which `add_delegate` was authorized, never for a later return of the same token.

### Proof of Concept

Assume `MANAGER` is already an approved active position manager and `ALICE` owns account NFT `ID` with collateral:

1. `Controller.supply(ALICE, 0, SPOKE, [(USDC, 1_000)])` creates `ID`.
2. `Controller.add_delegate(ALICE, ID, MANAGER)` stores `DelegateGrant { granted_by: ALICE, delegates: [MANAGER] }`.
3. `PositionNft.transfer(ALICE, BOB, ID)` transfers the account. `MANAGER` is currently rejected because `granted_by != BOB`.
4. `PositionNft.transfer(BOB, ALICE, ID)` returns the account to `ALICE`.
5. Without any new grant, `Controller.withdraw(MANAGER, ID, [(USDC, 0)], Some(MANAGER))` reaches `require_owner_or_delegate`, finds the stale `ALICE`-stamped grant, and withdraws the collateral to `MANAGER`.

Equivalently, `MANAGER` can call `borrow(MANAGER, ID, [(BORROW_ASSET, amount)], Some(MANAGER))` and leave `ID` encumbered by the new debt.

### Citations

**File:** contracts/controller/src/storage/account.rs (L33-43)
```rust
/// Resolves current NFT ownership; returns `None` for an unconfigured NFT,
/// unmintable ID, missing token, or failed lookup. Ownership fails closed.
pub(crate) fn try_account_owner(env: &Env, account_id: u64) -> Option<Address> {
    let nft = super::protocol::try_get_position_nft(env)?;
    nft_try_owner_of_call(env, &nft, account_id)
}

/// Resolves current NFT ownership or fails with `AccountNotFound`.
pub(crate) fn account_owner(env: &Env, account_id: u64) -> Address {
    try_account_owner(env, account_id)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AccountNotFound))
```

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

**File:** contracts/controller/src/storage/account.rs (L223-246)
```rust
/// Removes a live delegate and reports whether it changed the list.
/// Deletes stale grants but returns false, preventing those grants from
/// reactivating if the NFT returns to their original owner.
pub(crate) fn remove_delegate(
    env: &Env,
    account_id: u64,
    owner: &Address,
    delegate: &Address,
) -> bool {
    let key = ControllerKey::Delegates(account_id);
    let Some(grant) = get_user::<DelegateGrant>(env, &key) else {
        return false;
    };
    if grant.granted_by != *owner {
        env.storage().persistent().remove(&key);
        return false;
    }
    let mut delegates = grant.delegates;
    let Some(index) = delegates.first_index_of(delegate) else {
        return false;
    };
    delegates.remove(index);
    set_delegates(env, account_id, owner, &delegates);
    true
```

**File:** contracts/controller/src/account.rs (L115-127)
```rust
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

**File:** common/src/types/controller.rs (L63-73)
```rust
/// A delegate list stamped with the owner who granted it. The grant is live only while
/// `granted_by` owns the account's NFT: after an NFT transfer, `get_delegates` reads it as
/// empty for the new owner. The new owner's next `add_delegate` or `remove_delegate`
/// overwrites or deletes the stale entry. If the NFT returns to `granted_by` before such a
/// write, the original delegate list is live again.
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DelegateGrant {
    pub granted_by: Address,
    pub delegates: Vec<Address>,
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

**File:** contracts/controller/src/positions/debt.rs (L40-47)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
```
