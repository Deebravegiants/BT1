### Title
Stale delegate grant reactivates when a position NFT returns to its original owner - (File: contracts/controller/src/storage/account.rs)

### Summary
Controller delegate grants are keyed only by `account_id` and stamped with `granted_by`, so transferring the position NFT disables the grant without deleting it. If the same NFT is later transferred back to `granted_by` before an intervening owner overwrites or removes the grant, the old delegate becomes authorized again and can withdraw collateral or borrow to an arbitrary external recipient. This is a lifecycle analog of the reported use-after-free pattern: a stale authorization object remains reachable after ownership moves on and is later reused.

### Finding Description
`DelegateGrant` stores the granting owner and a list of delegates under `ControllerKey::Delegates(account_id)`. [1](#0-0)  `get_delegates` treats the stored list as valid whenever `grant.granted_by == current_owner`; it does not bind the grant to an NFT transfer epoch, ownership nonce, or token-generation counter. [2](#0-1)  The code comments explicitly state that ownership changes invalidate a previous owner's grants “without deleting them,” leaving the stale grant in persistent storage. [3](#0-2) 

Only a subsequent `add_delegate` overwrites the stale grant, while `remove_delegate` deletes a grant stamped by a different owner. [4](#0-3) [5](#0-4)  If neither occurs before the NFT returns to the original owner, `get_delegates` again returns the original list. [6](#0-5) 

The returned delegate is accepted by `is_owner_or_delegate` when it is still an active registered position manager. [7](#0-6)  `process_withdraw` then lets that delegate choose an arbitrary external recipient through `to`, and `process_borrow` does the same for newly borrowed assets. [8](#0-7) [9](#0-8) 

### Impact Explanation
A stale delegate can steal every withdrawable collateral asset in a debt-free account by calling `withdraw` with zero-valued legs, which the controller interprets as full withdrawals, and setting `to` to the delegate's own address. [10](#0-9)  For an account with debt, the delegate can withdraw all collateral that remains within the post-pool solvency gates and borrow up to the account's risk limits to an external recipient. [11](#0-10) [12](#0-11)  This constitutes theft of user funds and can leave the recovered owner with an impaired or liquidatable position.

### Likelihood Explanation
The attack requires the victim to have previously delegated to an active position manager, transfer the NFT to another owner, and later regain the same NFT before the intervening owner writes the delegate entry. Ordinary NFT sales, wallet rotation, escrow flows, and return transfers all satisfy the ownership sequence, and neither NFT transfer clears the controller's persistent `Delegates(account_id)` entry. [13](#0-12)  No privileged protocol operation is needed after the original grant: the attacker only signs as the formerly delegated manager and calls the public `withdraw` or `borrow` entrypoints. [14](#0-13) [15](#0-14)  The requirement that the delegate remain an active position manager reduces but does not eliminate the risk. [16](#0-15) 

### Recommendation
Bind delegate grants to an ownership generation or epoch rather than only the owner's address. Increment an `ownership_epoch` on every NFT transfer detected by the controller, or have the NFT/controller record a monotonically increasing transfer nonce per account and store it inside `DelegateGrant`. Require `grant.owner_epoch == current_owner_epoch` in `get_delegates`, so ownership returning to the same address cannot resurrect an old grant. Alternatively, delete `ControllerKey::Delegates(account_id)` atomically on every position-NFT transfer instead of relying on the intervening owner's `add_delegate` or `remove_delegate` call.

### Proof of Concept
Assume `M` is an active registered position manager.

```text
1. Alice owns account A through position NFT A.
   Controller.add_delegate(
       caller = Alice,
       account_id = A,
       delegate = M
   )

   Storage now contains:
   Delegates(A) = DelegateGrant {
       granted_by: Alice,
       delegates: [M],
   }

2. Alice transfers NFT A to Bob:
   PositionNft.transfer(
       from = Alice,
       to = Bob,
       token_id = A
   )

   The grant remains stored but is inactive because
   granted_by(Alice) != owner(Bob).

3. Bob does not call add_delegate or remove_delegate.
   Bob later transfers NFT A back to Alice:
   PositionNft.transfer(
       from = Bob,
       to = Alice,
       token_id = A
   )

   The same stored grant now matches granted_by(Alice) == owner(Alice),
   so M is live again.

4. M steals all withdrawable collateral:
   Controller.withdraw(
       caller = M,
       account_id = A,
       withdrawals = [
           (HubAssetKey { hub_id, asset: collateral_1 }, 0),
           (HubAssetKey { hub_id, asset: collateral_2 }, 0),
       ],
       to = Some(M)
   )

   Each zero leg withdraws the full corresponding collateral position,
   and the payout recipient is M.

5. Alternatively, on an account that still passes solvency checks, M borrows
   the maximum permitted amount:
   Controller.borrow(
       caller = M,
       account_id = A,
       borrows = [(HubAssetKey { hub_id, asset: debt_asset }, amount)],
       to = Some(M)
   )
```

The decisive state transition is the stale `DelegateGrant` matching again at step 3: `get_delegates` filters solely on the current owner's address, while `process_withdraw` and `process_borrow` rely on that result through `require_owner_or_delegate`. [6](#0-5) [17](#0-16)

### Citations

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

**File:** contracts/controller/src/storage/account.rs (L201-219)
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
```

**File:** contracts/controller/src/storage/account.rs (L223-238)
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

**File:** contracts/controller/src/positions/debt.rs (L40-59)
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

    let restamped = enforce_post_pool_solvency(env, &mut cache, &mut account);
```
