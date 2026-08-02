## Custody Analog Found: `object::delete()` can orphan a live `FungibleStore` balance, bypassing the balance-zero invariant enforced by `fungible_asset::remove_store()`

### Title
Object deletion via `object::delete()` does not enforce the "store must be empty" invariant, permanently locking fungible-asset balances - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
The external report's root custody invariant is: **a container that still holds value must not be destroyed/orphaned without first requiring the value to be zero.** Aptos's `fungible_asset` module enforces exactly this invariant for its own deletion path, `remove_store()`, which asserts `balance == 0` before removing the `FungibleStore` resource. However, `object::delete()` — the lower-level primitive that destroys the `ObjectCore` behind *any* object, including one carrying a `FungibleStore` — has no such check. Anyone holding a `DeleteRef` for an object can call `object::delete()` directly instead of the safe `fungible_asset::remove_store()`, destroying the object's identity while its `FungibleStore` (and its non-zero balance) remains orphaned in global storage, permanently unreachable.

### Finding Description
`fungible_asset::remove_store()` explicitly enforces the "stores must be empty before deletion" invariant, which is even documented as a formally verified high-level requirement: [1](#0-0) [2](#0-1) 

But `DeleteRef` is not specific to `FungibleStore` — `object_from_delete_ref<T>()` can convert it to any resource type, and the *same* `DeleteRef` value can instead be passed straight to the generic `object::delete()`: [3](#0-2) 

`object::delete()` only removes the `ObjectCore` (and an `Untransferable` marker if present). It has **no knowledge of, and performs no check against**, a co-located `FungibleStore` resource or its balance. Once `ObjectCore` is removed:
- `object::owns()`, `object::owner()`, `object::is_owner()`, and `object::address_to_object()`-based lookups all assert `exists<ObjectCore>(addr)` and will abort.
- Consequently `fungible_asset::withdraw_sanity_check_impl()` (which calls `object::owns`) can never succeed for that address again. [4](#0-3) 

The `FungibleStore` resource (with its `balance` field) still physically exists at that address in global storage — it was never `move_from`'d — but there is no longer any `Object<T>` handle that can be constructed to reference it for withdrawal, since object accessors require a live `ObjectCore`. The funds become permanently unreachable/unrecoverable, exactly mirroring the external report's "position burned while still holding collateral" pattern, except here it's the fungible-asset custody primitive (`ObjectCore` + `FungibleStore`) instead of an ERC721 short position.

The test suite confirms `remove_store` is the intended/only sanctioned deletion path for a store-bearing object (`test_create_and_remove_store` calls `remove_store(&delete_ref)`), but nothing in the type system or the `object` module prevents a store-bearing object's `DeleteRef` from instead being routed to `object::delete()`: [5](#0-4) 

### Impact Explanation
Any code path (module logic, composability bug, or a custom deletion/cleanup routine) that holds a `DeleteRef` for an object which also carries a `FungibleStore` can call `object::delete()` instead of `fungible_asset::remove_store()` — accidentally or by exploiting an ordering/composability gap — and destroy the object's custody identity while a non-zero balance is still deposited in it. This is a permanent, non-recoverable loss of fungible-asset value (APT or any FA token), since:
- The balance is not burned from supply (supply accounting becomes inconsistent with reachable balances), and
- No signer, `Object<T>` handle, `TransferRef`, or `BurnRef` can ever again reference the orphaned `FungibleStore` to withdraw, freeze, or burn it, because every accessor requires `exists<ObjectCore>`.

This satisfies the custody gate's "permanent lock or non-recoverable loss of object-held … value" and "supply or custody accounting corruption that … destroys recovery rights" criteria.

### Likelihood Explanation
The likelihood hinges on some caller actually invoking `object::delete()` on a store-bearing object instead of `remove_store()`. `DeleteRef` is a plain, non-type-parameterized value (only holds an address), so nothing at the type level prevents this misuse; it can happen via a composability bug in third-party or even first-party code built on top of the `object`/`fungible_asset` primitives (e.g., a generic "vault"/escrow abstraction that generates one `DeleteRef` per object and has a single generic cleanup function that calls `object::delete()` for all its objects regardless of whether some of them also hold `FungibleStore`s). Because the framework itself provides no defense-in-depth (e.g., `object::delete()` does not check `!exists<FungibleStore>(self.self) || balance == 0`), this is a systemic gap rather than a one-off application bug, and the "safe" `remove_store` path exists precisely because the framework authors recognized the invariant needed enforcing — just only in one of the two possible destruction entry points.

### Recommendation
Add a defense-in-depth check in `object::delete()` (or in the deletion machinery of `ObjectCore`) that rejects deletion if a `FungibleStore` (or other framework-registered "value-holding" resource) exists at the same address with a non-zero balance, mirroring the check already present in `fungible_asset::remove_store()`. At minimum, `object::delete()` should assert `!exists<FungibleStore>(self.self) || fungible_asset::balance-is-zero(self.self)` before removing `ObjectCore`, so the "must be empty to delete" invariant is enforced regardless of which deletion entry point is used.

### Proof of Concept
Conceptually (pseudo-Move), given a constructor_ref used to both create a `FungibleStore` and generate a `DeleteRef`:
```move
let constructor_ref = object::create_object_from_account(user);
let store = fungible_asset::create_store(&constructor_ref, metadata);
let delete_ref = object::generate_delete_ref(&constructor_ref);

// deposit funds into `store` (balance > 0)
fungible_asset::deposit(store, fa);

// instead of fungible_asset::remove_store(&delete_ref) which would abort
// (EBALANCE_IS_NOT_ZERO), call the generic primitive directly:
object::delete(delete_ref);

// store's FungibleStore resource (with its balance) is now orphaned:
// object::owns(store, user) / object::owner(store) abort with
// EOBJECT_DOES_NOT_EXIST, so the balance can never be withdrawn again.
```
This can be verified against the existing test pattern in `fungible_asset.move`'s `test_create_and_remove_store` [5](#0-4)  by substituting `object::delete(delete_ref)` for `remove_store(&delete_ref)` after depositing a non-zero balance — the deposit call would succeed and then `object::delete` would succeed unlike the guarded `remove_store`, orphaning the funds.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L919-933)
```text
    /// Used to delete a store.  Requires the store to be completely empty prior to removing it
    public fun remove_store(
        delete_ref: &DeleteRef
    ) acquires FungibleStore, FungibleAssetEvents, ConcurrentFungibleBalance {
        let store = delete_ref.object_from_delete_ref<FungibleStore>();
        let addr = store.object_address();
        let FungibleStore { metadata, balance, frozen: _ } =
            move_from<FungibleStore>(addr);
        assert!(balance == 0, error::permission_denied(EBALANCE_IS_NOT_ZERO));

        if (concurrent_fungible_balance_exists_inline(addr)) {
            let ConcurrentFungibleBalance { balance } =
                move_from<ConcurrentFungibleBalance>(addr);
            assert!(balance.read() == 0, error::permission_denied(EBALANCE_IS_NOT_ZERO));
        };
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L974-987)
```text
    inline fun withdraw_sanity_check_impl<T: key>(
        owner_address: address, store: Object<T>, abort_on_dispatch: bool
    ) {
        assert!(
            object::owns(store, owner_address),
            error::permission_denied(ENOT_STORE_OWNER)
        );
        let fa_store = borrow_store_resource(&store);
        assert!(
            !abort_on_dispatch || !has_withdraw_dispatch_function(fa_store.metadata),
            error::invalid_argument(EINVALID_DISPATCHABLE_OPERATIONS)
        );
        assert!(!fa_store.frozen, error::permission_denied(ESTORE_IS_FROZEN));
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1562-1571)
```text
    #[test(creator = @0xcafe)]
    fun test_create_and_remove_store(
        creator: &signer
    ) acquires FungibleStore, FungibleAssetEvents, ConcurrentFungibleBalance {
        let (_, _, _, _, metadata) = create_fungible_asset(creator);
        let creator_ref = object::create_object_from_account(creator);
        create_store(&creator_ref, metadata);
        let delete_ref = creator_ref.generate_delete_ref();
        remove_store(&delete_ref);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.spec.move (L211-221)
```text
    spec remove_store(delete_ref: &DeleteRef) {
        pragma aborts_if_is_partial;
        let addr = delete_ref.self;
        aborts_if !exists<FungibleStore>(addr);
        /// [high-level-req-10]
        aborts_if global<FungibleStore>(addr).balance != 0;
        /// [high-level-req-10]
        aborts_if exists<ConcurrentFungibleBalance>(addr)
            && aggregator_v2::spec_get_value(global<ConcurrentFungibleBalance>(addr).balance) != 0;
        ensures !exists<FungibleStore>(addr);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L462-477)
```text
    /// Removes from the specified Object from global storage.
    public fun delete(self: DeleteRef) {
        let object_core = move_from<ObjectCore>(self.self);
        let ObjectCore {
            guid_creation_num: _,
            owner: _,
            allow_ungated_transfer: _,
            transfer_events,
        } = object_core;

        if (exists<Untransferable>(self.self)) {
            let Untransferable {} = move_from<Untransferable>(self.self);
        };

        event::destroy_handle(transfer_events);
    }
```
