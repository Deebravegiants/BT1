### Title
Stale delegate authorization is resurrected when a position NFT returns to a previous owner - (File: contracts/controller/src/storage/account.rs)

### Summary
**Severity: High.** Delegate grants are keyed only by `account_id` and stamped with the granting owner's address, not an ownership epoch or NFT transfer count. If the NFT moves to another owner and later returns to `granted_by` without the intervening owner calling `add_delegate` or `remove_delegate`, the old delegate list becomes live again [1](#0-0) .

### Finding Description
`get_delegates` returns the stored list whenever `DelegateGrant.granted_by` equals the current NFT owner [1](#0-0) . An intervening owner who never mutates delegates leaves that stale grant intact; `add_delegate` overwrites it, and `remove_delegate` purges it, but no ownership transfer automatically does either [2](#0-1) . Authorization then admits the delegate if it is still an active position manager and appears in the resurrected list [3](#0-2) . Once authorized, `withdraw` lets that delegate select an arbitrary external recipient through `to` [4](#0-3) .

### Impact Explanation
A previously trusted delegate can steal collateral after the position changes hands twice. The delegate does not need the current owner's signature for `withdraw`; after `require_owner_or_delegate` accepts the resurrected grant, it can call `withdraw(caller=delegate, account_id, withdrawals, to=Some(delegate))` and take every withdrawable collateral position while preserving the account's risk checks [4](#0-3) . For a debt-free account, zero-valued withdrawal legs withdraw the full position and can close the account, so the impact is theft of user funds up to the account's supplied collateral [5](#0-4) .

### Likelihood Explanation
The attack needs three realistic conditions: the victim previously granted an active position-manager delegate, the position NFT left and later returned to the same victim address, and the intervening owner did not write the delegate list [6](#0-5) . Position NFTs are ordinary transferable tokens whose transfer moves the entire account, so marketplace sales, wallet migration, custodial reassignment, or temporary transfer can produce that round trip [7](#0-6) . The stale authorization needs no oracle movement, bad parameter, privileged call, reentrancy, or leaked key; it survives silently until the manager is globally deactivated, the original owner removes it, or a later owner overwrites/purges it [8](#0-7) .

### Recommendation
Bind delegation to an ownership epoch rather than only `granted_by`. For example, have the position NFT maintain a monotonically increasing transfer epoch per token, expose it with the owner lookup, store `{granted_by, ownership_epoch}` in `DelegateGrant`, and require both the current owner and current epoch in `get_delegates`. Alternatively, add a controller-side purge invoked on every NFT transfer/transfer_from, though this requires a deliberate cross-contract ownership-notification design. Regression coverage should explicitly prove that an A→B→A NFT round trip cannot revive A's old manager grant without a fresh `add_delegate` from A.

### Proof of Concept
1. Alice creates and funds account `A`; governance has activated `manager` as a position manager.
2. Alice calls `add_delegate(caller=alice, account_id=A, delegate=manager)`, storing `DelegateGrant { granted_by: alice, delegates: [manager] }` [9](#0-8) .
3. Alice transfers position NFT `A` to Bob. Under Bob, `get_delegates(A, bob)` filters out Alice's stale grant, so `manager` is temporarily rejected [1](#0-0) .
4. Bob performs neither `add_delegate` nor `remove_delegate`, then transfers NFT `A` back to Alice.
5. `account_owner(A)` again resolves to Alice, and the stored `granted_by == alice` grant is live again [10](#0-9) [1](#0-0) .
6. The still-active `manager` calls `withdraw(caller=manager, account_id=A, withdrawals=[(collateral_market, 0)], to=Some(manager))`; the zero leg means full withdrawal and the arbitrary recipient receives Alice's collateral [4](#0-3) .

### Citations

**File:** contracts/controller/src/storage/account.rs (L35-44)
```rust
pub(crate) fn try_account_owner(env: &Env, account_id: u64) -> Option<Address> {
    let nft = super::protocol::try_get_position_nft(env)?;
    nft_try_owner_of_call(env, &nft, account_id)
}

/// Resolves current NFT ownership or fails with `AccountNotFound`.
pub(crate) fn account_owner(env: &Env, account_id: u64) -> Address {
    try_account_owner(env, account_id)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AccountNotFound))
}
```

**File:** contracts/controller/src/storage/account.rs (L174-181)
```rust
/// Returns grants stamped by `owner`, or an empty list. Ownership changes
/// invalidate a previous owner's grants without deleting them.
pub(crate) fn get_delegates(env: &Env, account_id: u64, owner: &Address) -> Vec<Address> {
    get_user::<DelegateGrant>(env, &ControllerKey::Delegates(account_id))
        .filter(|grant| grant.granted_by == *owner)
        .map(|grant| grant.delegates)
        .unwrap_or_else(|| Vec::new(env))
}
```

**File:** contracts/controller/src/storage/account.rs (L201-247)
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
}

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
}
```

**File:** contracts/controller/src/account.rs (L114-140)
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

/// Requires the owner or a registered, active manager delegated by that owner.
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
}
```

**File:** contracts/controller/src/account.rs (L228-264)
```rust
/// Requires the NFT owner to grant an active manager access; renews instance TTL.
pub(crate) fn add_delegate(env: &Env, caller: Address, account_id: u64, delegate: Address) {
    storage::renew_controller_instance(env);
    set_account_delegate(env, &caller, account_id, &delegate, true);
}

/// Requires the NFT owner to revoke manager access; renews instance TTL.
pub(crate) fn remove_delegate(env: &Env, caller: Address, account_id: u64, delegate: Address) {
    storage::renew_controller_instance(env);
    set_account_delegate(env, &caller, account_id, &delegate, false);
}

/// Authenticates the NFT owner and updates delegates; grants require an active
/// manager. Emits an event only when the current owner's delegate list changes.
fn set_account_delegate(
    env: &Env,
    caller: &Address,
    account_id: u64,
    delegate: &Address,
    add: bool,
) {
    caller.require_auth();
    require_account_owner(env, account_id, caller);
    if add {
        // Reject dormant grants that could gain authority on later manager activation.
        assert_with_error!(
            env,
            storage::get_position_manager(env, delegate).is_some_and(|c| c.is_active),
            GenericError::NotAuthorized
        );
    }

    let changed = if add {
        storage::add_delegate(env, account_id, caller, delegate)
    } else {
        storage::remove_delegate(env, account_id, caller, delegate)
    };
```

**File:** contracts/controller/src/positions/supply.rs (L138-168)
```rust
/// Withdraws for an authorized owner/delegate and checks post-pool solvency.
/// Zero requests withdraw all; returns the pool's actual payouts per asset.
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

**File:** contracts/position-nft/README.md (L39-41)
```markdown
Transferring the token transfers the whole position. Nothing in the controller
changes on transfer: the next controller call resolves the new holder and
accepts it. Collateral and debt both move with the token.
```
