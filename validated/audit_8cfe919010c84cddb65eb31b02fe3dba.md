### Title
Stale delegate authorization reactivates after position NFT returns to former owner - (File: contracts/controller/src/storage/account.rs)

### Summary
Delegate grants are keyed by `account_id` and stamped only with the granting owner's address, not with an ownership epoch or NFT transfer sequence. [1](#0-0)  Consequently, a grant becomes inactive while another address owns the NFT but becomes valid again if that NFT is later transferred back to the original owner without an intervening delegate-list update. [2](#0-1) 

### Finding Description
`storage::get_delegates` accepts a persisted grant whenever `grant.granted_by` equals the account's current NFT owner. [3](#0-2)  `is_owner_or_delegate` then authorizes any listed delegate that also has active position-manager registration. [4](#0-3) 

The position NFT is the live ownership authority for the account, and its transfer moves control of all collateral and debt. [5](#0-4)  A transfer makes the former owner's delegate grant inactive, but does not delete it; because the stored discriminator is only the owner address, returning the NFT to that owner restores the old grant. [6](#0-5) 

An attacker who was delegated while Alice owned the account can therefore wait for the position to pass through a custodian or buyer and return to Alice, then invoke `withdraw` or `borrow` as Alice's supposed former delegate. [7](#0-6)  `withdraw` permits the caller to select an external `to` recipient, while `borrow` likewise permits the caller to select `to`; both authorize the reactivated delegate before moving value. [8](#0-7) 

### Impact Explanation
A stale delegate can transfer withdrawable collateral to itself after Alice regains ownership, causing theft of user funds. [8](#0-7)  For collateral still locked by debt, the delegate can borrow the maximum amount permitted by the account's risk checks to itself and leave the debt attached to Alice's account. [9](#0-8) 

### Likelihood Explanation
The exploit requires Alice to grant an active position manager, transfer the NFT to another holder, and receive it back without that holder calling `add_delegate` or `remove_delegate`. [10](#0-9)  This can occur during legitimate marketplace custody, temporary transfer, collateral management, or return of an erroneously transferred NFT. [11](#0-10)  Once those conditions hold, no new signature from Alice is needed beyond the persisted grant because `require_owner_or_delegate` accepts the reactivated delegate directly. [12](#0-11) 

### Recommendation
Bind each delegate grant to an ownership epoch rather than only `granted_by`. [3](#0-2)  For example, persist an `ownership_nonce` in controller storage, increment it whenever ownership resolution changes or expose a controller callback that the position NFT invokes on transfer, and store that nonce in `DelegateGrant`; `get_delegates` should return the list only when both `granted_by` and the nonce match the current owner and epoch. [13](#0-12)  If a notification hook is not feasible, permanently clear `ControllerKey::Delegates(account_id)` through a permissionless `invalidate_delegates(account_id)` path after an observed owner change instead of allowing stale grants to re-arm. [14](#0-13) 

### Proof of Concept
Assume `MANAGER` is an active governance-approved position manager, Alice owns account `id`, and the account has withdrawable `USDC` collateral. [15](#0-14) 

1. Alice calls `add_delegate(alice, id, MANAGER)`, storing `DelegateGrant { granted_by: alice, delegates: [MANAGER] }` under `Delegates(id)`. [16](#0-15) 
2. Alice transfers NFT `id` to Bob. While Bob owns it, `get_delegates(id, bob)` returns empty because `granted_by != bob`. [3](#0-2) 
3. Bob transfers NFT `id` back to Alice without modifying delegates. `get_delegates(id, alice)` again returns `[MANAGER]`. [2](#0-1) 
4. `MANAGER` calls `withdraw(MANAGER, id, [(usdc_hub_asset, 0)], Some(MANAGER))`; `require_owner_or_delegate` loads owner Alice, sees the reactivated grant, and authorizes the withdrawal. [12](#0-11) 
5. The zero withdrawal amount selects the full position, and the optional `to` argument directs the collateral to `MANAGER`. [8](#0-7)

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

**File:** contracts/controller/src/storage/account.rs (L203-220)
```rust
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

**File:** contracts/controller/src/storage/account.rs (L223-245)
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
```

**File:** contracts/controller/src/storage/account.rs (L249-255)
```rust
/// Deletes metadata, both position maps, and delegates. Does not burn the NFT.
pub(crate) fn remove_account_entry(env: &Env, account_id: u64) {
    let persistent = env.storage().persistent();
    persistent.remove(&ControllerKey::AccountMeta(account_id));
    persistent.remove(&ControllerKey::SupplyPositions(account_id));
    persistent.remove(&ControllerKey::BorrowPositions(account_id));
    persistent.remove(&ControllerKey::Delegates(account_id));
```

**File:** common/src/types/controller.rs (L63-72)
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
```

**File:** contracts/controller/src/account.rs (L121-127)
```rust
    if caller == owner {
        return true;
    }
    let active_manager =
        storage::get_position_manager(env, caller).is_some_and(|config| config.is_active);
    active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
}
```

**File:** contracts/controller/src/account.rs (L130-139)
```rust
pub(crate) fn require_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) {
    if is_owner_or_delegate(env, account_id, caller, owner) {
        return;
    }
    panic_with_error!(env, GenericError::NotAuthorized);
```

**File:** contracts/position-nft/README.md (L162-166)
```markdown
**Transfer cannot be used to escape debt.** The token carries the account, and
the account carries both collateral and debt. The controller keys every
solvency check on `account_id`, not on holder identity, so an underwater
position stays liquidatable after transfer, and the new holder can withdraw only
what leaves the debt covered by LTV-weighted collateral.
```

**File:** contracts/position-nft/README.md (L174-179)
```markdown
**Delegates lapse on transfer.** The controller stores a `DelegateGrant`
stamped with the `granted_by` address. `get_delegates` returns an empty list
unless `granted_by` equals the current NFT owner, so a transfer disables the
old holder's delegates immediately. The stale grant stays in storage and
re-arms if the token returns to `granted_by`. The next holder's `add_delegate`
overwrites it and `remove_delegate` deletes it.
```

**File:** contracts/controller/src/lib.rs (L104-114)
```rust
    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
```

**File:** contracts/controller/src/lib.rs (L117-127)
```rust
    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
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

**File:** docs/reference/endpoints.md (L47-50)
```markdown
Account id `0` creates an account on `supply`, `multiply`, `flash_position`, `migrate_from_blend`, and liquidation with `Credit(0)`. An account's spoke binding is permanent. `multiply` and `flash_position` require Multiply, Long or Short mode, and an existing account must match the requested mode. Blend migration creates a Normal account; an existing destination need not be Normal.

Delegates belong to the granting owner. An NFT transfer disables that owner's grants; a transfer back can reactivate them unless a later owner has replaced or deleted the list. NFT ownership, including control of collateral and the debt obligation, transfers atomically.

```
