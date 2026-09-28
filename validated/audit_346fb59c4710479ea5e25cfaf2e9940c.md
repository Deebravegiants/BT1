### Title
Stale account delegates regain control when a position NFT returns to its former owner - ([File: contracts/controller/src/storage/account.rs])

### Summary
Controller account delegates are stored as one `DelegateGrant` per account and are validated by comparing `grant.granted_by` with the account's **current** NFT owner, rather than by an ownership epoch or nonce. Transferring the position NFT makes the old owner's grant inactive, but it remains stored. If the NFT is subsequently transferred back to that former owner, the stale grant becomes valid again, allowing a previously delegated position manager to withdraw collateral or borrow against the account without renewed authorization.

### Finding Description
`storage::account_owner` resolves account ownership dynamically from the position NFT's `owner_of`. Delegate authorization then calls `get_delegates(account_id, owner)`, which accepts a stored grant whenever `grant.granted_by == current_owner`. [1](#0-0) [2](#0-1) 

An owner-authorized call to `add_delegate` stores `DelegateGrant { granted_by: caller, delegates }`. [3](#0-2) [4](#0-3)  An NFT transfer does not notify the controller and does not delete `ControllerKey::Delegates(account_id)`. Consequently, the grant is only dormant while another address owns the NFT; it is not permanently invalidated.

The code explicitly recognizes this resurrection condition: `remove_delegate` removes a grant stamped by a different owner precisely to prevent it from reactivating if the NFT returns to the original owner. [5](#0-4)  However, this cleanup is optional. If the intermediate owner never calls `remove_delegate` or `add_delegate`, the original grant survives intact.

Once the NFT returns to Alice, `is_owner_or_delegate` treats the old manager as authorized because Alice is again the owner and her old delegate list again matches `granted_by`. [6](#0-5)  The manager can then invoke owner/delegate-gated entry points such as `withdraw` or `borrow`, both of which support directing proceeds to a supplied `to` address. [7](#0-6) 

### Impact Explanation
This enables theft of user funds. A previously delegated position manager can wait until the account NFT returns to the former owner and then withdraw all transferable collateral to itself, subject to post-withdrawal solvency checks, or borrow up to the account's borrowing limit and direct the borrowed assets to itself.

The prior delegation was authorized for the earlier ownership tenure, not for a future reacquisition of the account. Reauthentication should therefore be required before the manager regains spending authority.

### Likelihood Explanation
The attack requires three reachable conditions:

1. Alice grants an active position manager access to `account_id`.
2. Alice transfers the account NFT to another address.
3. The NFT later returns to Alice while the original `Delegates` entry still exists.

NFT sale, temporary custody, wallet migration, collateralized transfer, or repurchase can satisfy the ownership round trip. No malicious privileged action is required after the grant is created. The intermediate owner can remove the stale grant, but the protocol does not require or automatically perform that cleanup.

### Recommendation
Bind each delegate grant to a non-reusable ownership generation or transfer epoch rather than only `granted_by`. For example:

- store an `ownership_epoch` in `AccountMeta` and increment it on every observed NFT owner change, then include it in `DelegateGrant`; or
- emit an ownership-change notification from a controller-managed wrapper and clear `Delegates(account_id)` atomically on transfer; or
- make every delegate authorization require both `granted_by == current_owner` and a grant version matching the current ownership generation.

Because the stock NFT contract cannot call back into the controller, an ownership-generation check is likely the least invasive fix if the controller can reliably observe owner changes; otherwise, require delegates to be re-registered after any detected owner transition and store enough transition state to make old grants permanently invalid.

### Proof of Concept
Conceptual transaction sequence:

1. Alice creates or funds an account through:
   ```text
   controller.supply(
       caller = Alice,
       account_id = 0,
       spoke_id = SPOKE,
       assets = [(USDC_KEY, collateral)]
   )
   ```
   This mints `account_id` and its position NFT to Alice.

2. Governance marks `Manager` as an active position manager, and Alice grants it access:
   ```text
   controller.add_delegate(
       caller = Alice,
       account_id = account_id,
       delegate = Manager
   )
   ```
   This stores `DelegateGrant { granted_by: Alice, delegates: [Manager] }`.

3. Alice transfers `token_id = account_id` to Bob:
   ```text
   position_nft.transfer(
       from = Alice,
       to = Bob,
       token_id = account_id
   )
   ```
   The grant reads as inactive while Bob owns the NFT, but remains stored.

4. Bob does not call `remove_delegate` and later transfers the NFT back:
   ```text
   position_nft.transfer(
       from = Bob,
       to = Alice,
       token_id = account_id
   )
   ```

5. `get_delegates(account_id, Alice)` again returns `[Manager]` because the stored `granted_by` still equals the current owner.

6. Manager calls:
   ```text
   controller.withdraw(
       caller = Manager,
       account_id = account_id,
       withdrawals = [(USDC_KEY, collateral)],
       to = Some(Manager)
   )
   ```
   The owner-or-delegate check passes using the stale grant, and Manager receives Alice's collateral, subject to the account's normal withdrawal constraints.

### Citations

**File:** contracts/controller/src/storage/account.rs (L33-44)
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

**File:** contracts/controller/src/storage/account.rs (L183-199)
```rust
/// Stores delegates stamped by the granting owner and renews user TTL;
/// deletes the entry when the list is empty.
fn set_delegates(env: &Env, account_id: u64, owner: &Address, delegates: &Vec<Address>) {
    let key = ControllerKey::Delegates(account_id);
    if delegates.is_empty() {
        env.storage().persistent().remove(&key);
    } else {
        set_user(
            env,
            &key,
            &DelegateGrant {
                granted_by: owner.clone(),
                delegates: delegates.clone(),
            },
        );
    }
}
```

**File:** contracts/controller/src/storage/account.rs (L223-247)
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

**File:** contracts/controller/src/account.rs (L240-250)
```rust
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
```

**File:** contracts/controller/src/lib.rs (L104-128)
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
    }

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
    }
```
