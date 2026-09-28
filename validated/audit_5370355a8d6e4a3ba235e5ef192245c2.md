### Title
Stale delegate grants regain account-spending authority after an NFT ownership round-trip - (File: contracts/controller/src/storage/account.rs)

### Summary
A delegate authorization granted by one NFT owner is not permanently invalidated by transfer; it is keyed only to `granted_by`, so it becomes active again if the position NFT later returns to that owner. [1](#0-0) 

### Finding Description
`ControllerKey::Delegates(account_id)` stores one `DelegateGrant` containing the granting address and delegate list. [2](#0-1)  `get_delegates` returns the stored list whenever `grant.granted_by == current_owner`; it neither records an ownership generation nor deletes the grant when the owner differs. [1](#0-0) 

A position transfer changes the account owner through the NFT without touching the controller's delegate entry. [3](#0-2)  While another owner holds the NFT, the stale grant reads as empty, but if the NFT returns to the original owner before the intervening owner calls `add_delegate` or `remove_delegate`, equality succeeds again and every stale delegate regains authority. [4](#0-3) 

`require_owner_or_delegate` accepts such a caller when the address is still an active position manager and appears in the reactivated list. [5](#0-4)  `withdraw` then permits the delegate to select an external `to` recipient, while `borrow` likewise permits an arbitrary recipient subject to the post-operation solvency gates. [6](#0-5) [7](#0-6) 

### Impact Explanation
For a debt-free account, a reactivated delegate can call `withdraw` with a zero amount to withdraw the entire collateral position directly to itself. [8](#0-7)  For an account with collateral capacity, it can instead call `borrow` and direct the borrowed assets to itself, leaving the resulting debt on the victim's account. [7](#0-6)  This is theft of user collateral or borrowed protocol assets through authority that was inactive at the time the intervening owner held the NFT. [5](#0-4) 

### Likelihood Explanation
The attack requires the original owner to have granted an active position manager, the NFT to move to another holder, and the NFT to return before that holder replaces or purges the stale grant. [9](#0-8)  Those conditions can occur in marketplace, custody, temporary-transfer, or failed-sale flows where the NFT eventually settles back to the original address. [10](#0-9)  The stale delegate cannot force the NFT transfer itself, and governance deactivation of the manager prevents the final spending call, so the exposure is conditional rather than universally exploitable. [11](#0-10) 

### Recommendation
Bind each grant to an ownership epoch rather than only the owner's address, or purge the grant whenever the controller observes a mismatched `granted_by` during a mutable authorization path. [1](#0-0)  A robust fix should also update tests and documentation so that returning an NFT to a former owner can never resurrect delegates without a new `add_delegate` call. [12](#0-11) 

### Proof of Concept
1. Alice supplies collateral and obtains account `A`; `account_id == token_id == A`. [13](#0-12) 
2. Alice authorizes `add_delegate(caller=alice, account_id=A, delegate=mallory)`, while `mallory` is an active position manager. [14](#0-13) 
3. Alice transfers NFT `A` to Bob; `mallory` is rejected while `owner_of(A) == bob`. [15](#0-14) 
4. Bob does not call `add_delegate` or `remove_delegate`, then transfers NFT `A` back to Alice. [12](#0-11) 
5. `owner_of(A) == alice` makes `grant.granted_by == owner` true again, so the stale list containing `mallory` is returned. [1](#0-0) 
6. Mallory authorizes `withdraw(caller=mallory, account_id=A, withdrawals=[(collateral_hub_asset, 0)], to=Some(mallory))`; the zero amount selects the full position and the external recipient check does not redirect it to Alice. [6](#0-5) [8](#0-7)

### Citations

**File:** contracts/controller/src/storage/account.rs (L174-199)
```rust
/// Returns grants stamped by `owner`, or an empty list. Ownership changes
/// invalidate a previous owner's grants without deleting them.
pub(crate) fn get_delegates(env: &Env, account_id: u64, owner: &Address) -> Vec<Address> {
    get_user::<DelegateGrant>(env, &ControllerKey::Delegates(account_id))
        .filter(|grant| grant.granted_by == *owner)
        .map(|grant| grant.delegates)
        .unwrap_or_else(|| Vec::new(env))
}

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

**File:** contracts/position-nft/README.md (L25-37)
```markdown
| Controller action | NFT call | Effect |
| --- | --- | --- |
| `create_account` | `mint(owner)` | The returned `u32` token id becomes the `u64` account id |
| account deletion (`remove_account_and_burn_nft`) | `burn(token_id)` | Runs on every account deletion, including liquidation cleanup and bad-debt socialization |
| any owner check (`try_account_owner`) | `owner_of(token_id)` | Live lookup; the owner is never cached in controller storage |
| `renew_account` | `renew(token_id)` | Lifts the token's `Owner` entry and its holder's `Balance` entry to the protocol's per-user window |
| `upgrade_position_nft` | `upgrade(hash)` | Owner-gated Wasm upgrade |

`account_id == token_id`. The controller widens `u32` to `u64` on mint and
narrows back with `u32::try_from` on every other call; an id above `u32::MAX`
can never have been minted, so it resolves to `AccountNotFound`. Account id `0`
is the controller's "create a new account" sentinel, so the constructor
consumes token id 0 and the first real position is id 1.
```

**File:** contracts/position-nft/README.md (L39-41)
```markdown
Transferring the token transfers the whole position. Nothing in the controller
changes on transfer: the next controller call resolves the new holder and
accepts it. Collateral and debt both move with the token.
```

**File:** contracts/position-nft/README.md (L56-65)
```markdown
Inherited from the OpenZeppelin `NonFungibleToken` trait, exported unchanged:

| Call | Signature | Caller | Does |
| --- | --- | --- | --- |
| `balance` | `fn balance(e: &Env, account: Address) -> u32` | Anyone | Number of positions held by `account` |
| `owner_of` | `fn owner_of(e: &Env, token_id: u32) -> Address` | Anyone | Current holder; panics `NonExistentToken` if never minted or burned |
| `transfer` | `fn transfer(e: &Env, from: Address, to: Address, token_id: u32)` | `from` must authorize | Moves the position to `to` |
| `transfer_from` | `fn transfer_from(e: &Env, spender: Address, from: Address, to: Address, token_id: u32)` | `spender` must authorize and be `from`, approved for the token, or an operator for `from` | Moves the position to `to` |
| `approve` | `fn approve(e: &Env, approver: Address, approved: Address, token_id: u32, live_until_ledger: u32)` | `approver` must authorize and be the owner or an operator | Grants `approved` the right to move that one position until `live_until_ledger` |
| `approve_for_all` | `fn approve_for_all(e: &Env, owner: Address, operator: Address, live_until_ledger: u32)` | `owner` must authorize | Makes `operator` able to move every position `owner` holds until `live_until_ledger`; `0` revokes |
```

**File:** contracts/controller/src/account.rs (L114-139)
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
```

**File:** contracts/controller/src/account.rs (L240-264)
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

**File:** contracts/controller/src/positions/supply.rs (L145-157)
```rust
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
```

**File:** contracts/controller/src/positions/supply.rs (L180-199)
```rust
    let mut entries: Vec<PoolWithdrawEntry> = Vec::new(env);
    for (hub_asset, amount) in aggregated.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &hub_asset,
            FreezePolicy::AllowOnExit,
        );
        let position = get_supply_position_or_panic(env, account, &hub_asset);
        let requested = if amount == 0 {
            WITHDRAW_ALL_SENTINEL
        } else {
            amount
        };
        entries.push_back(PoolWithdrawEntry {
            action: make_pool_action(&position, requested, hub_asset.clone()),
            protocol_fee: 0,
        });
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

**File:** contracts/controller/tests/storage/account.rs (L140-174)
```rust
/// A previous owner's grant reads as empty after the NFT transfers. The new owner's next
/// write replaces it; it does not merge with it.
#[test]
fn delegates_of_previous_owner_read_as_empty() {
    let env = Env::default();
    env.mock_all_auths();
    let admin = Address::generate(&env);
    let contract_id = env.register(Controller, (admin,));
    let nft = setup_position_nft(&env, &contract_id);

    let alice = Address::generate(&env);
    let bob = Address::generate(&env);
    let delegate = Address::generate(&env);
    let account_id = u64::from(position_nft::PositionNftClient::new(&env, &nft).mint(&alice));

    env.as_contract(&contract_id, || {
        assert!(add_delegate(&env, account_id, &alice, &delegate));
        assert_eq!(get_delegates(&env, account_id, &alice).len(), 1);
    });

    position_nft::PositionNftClient::new(&env, &nft).transfer(
        &alice,
        &bob,
        &u32::try_from(account_id).unwrap(),
    );

    env.as_contract(&contract_id, || {
        assert_eq!(
            get_delegates(&env, account_id, &bob).len(),
            0,
            "a grant stamped by the previous owner must read as empty for the new owner"
        );
        assert!(add_delegate(&env, account_id, &bob, &delegate));
        assert_eq!(get_delegates(&env, account_id, &bob).len(), 1);
    });
```
