### Title
Stale `TombStone` records are not cleared on ordinary object transfers, allowing a former owner to reclaim a fungible-asset primary store after it has legitimately changed hands and been sent to the burn address - (File: aptos-move/framework/aptos-framework/sources/object.move)

### Summary
`object::unburn()` grants reclaim rights based on the `TombStone.original_owner` field, but ordinary ownership transfers (`transfer`, `transfer_raw`, `transfer_to_object`) never clear a pre-existing `TombStone`. Only the `LinearTransferRef`-based `transfer_with_ref` path clears it. This creates a path where a party who "soft burned" an object while still owning it, then legitimately transferred that same object away, can later reclaim it from a *new* owner once the object (e.g. a fungible-asset primary store or any object) ends up at `BURN_ADDRESS`, even though the reclaiming party had no involvement in that later burn.

### Finding Description
`burn<T>()` creates a `TombStone{original_owner}` while leaving `ObjectCore.owner` unchanged (the "soft burn" used for e.g. hiding a primary store from indexers): [1](#0-0) 

The only cleanup of a stale `TombStone` happens in the `LinearTransferRef` path: [2](#0-1) 

But ordinary transfers (`transfer`, `transfer_raw`, `transfer_to_object`) go through `transfer_raw_inner`, which only updates `ObjectCore.owner` and emits an event — it never checks for or removes any existing `TombStone`: [3](#0-2) 

`unburn()` then trusts the stored `TombStone.original_owner` to decide who can reclaim an object once it is found at `BURN_ADDRESS`: [4](#0-3) 

Broken invariant: the `TombStone.original_owner` recorded during a *soft* burn (owner unchanged) is supposed to only ever be consumed by the *same* owner clearing their own soft-burn state, or superseded when a `LinearTransferRef` transfer happens. But since a regular `transfer`/`transfer_raw` does not touch `TombStone`, an object that was soft-burned by owner A, then normally transferred (A→B), retains a stale `TombStone{original_owner: A}`. If B (or a later owner) subsequently sends the same object to `BURN_ADDRESS` via any ordinary transfer (not necessarily the intended `burn_object_with_transfer` flow — `BURN_ADDRESS` is just a normal address and ungated transfer to it succeeds like any other transfer), `unburn()`'s second branch (`object_core.owner == BURN_ADDRESS`) fires and authorizes reclaim to `A`, the stale `original_owner`, not to `B` or whoever actually sent it to the burn address.

This directly affects fungible-asset custody because primary stores are `Object<FungibleStore>` and use exactly this burn/unburn mechanism: `primary_fungible_store::may_be_unburn` calls `object::unburn` automatically whenever a withdraw/transfer touches a burnt store: [5](#0-4) 
and the transfer/withdraw functions call it transparently before moving funds: [6](#0-5) 

### Impact Explanation
The bug lets a stale `TombStone.original_owner` be used to hijack ownership recovery rights of an object (including a fungible-asset primary store) that has since passed through a legitimate ownership chain to another party and ended up at `BURN_ADDRESS`. Because `unburn()` transfers the object back to whichever address is recorded in the (potentially stale) `TombStone`, a former owner can regain control of an object/FA store — and the value held in it — that rightfully belongs to a different, later party, without that party's consent. This is a custody-accounting corruption that moves object/asset ownership to the wrong holder, satisfying the "owner reassignment tied to live assets" and "supply/custody accounting corruption that moves value to the wrong holder" impact criteria.

### Likelihood Explanation
Exploitation requires: (1) an object owner to soft-burn an object they still own (`burn()`), (2) transfer it away via a normal (non-`TransferRef`) transfer, and (3) the object to later reach `BURN_ADDRESS` via an ordinary transfer rather than via `burn_object_with_transfer`/`transfer_with_ref`. Step 3 is plausible because `BURN_ADDRESS` is not privileged in any way at the transfer layer — any account can send an ungated-transferable object there directly, and this is a realistic pattern for anyone intentionally "burning" an object without knowing about (or bothering to use) the dedicated `burn_object_with_transfer` API. The condition is specific but requires no special privileges from the attacker (former owner A) beyond having once soft-burned the object before giving it away, which is straightforward to arrange as a self-inflicted setup.

### Recommendation
Clear any existing `TombStone` on every ownership-changing path, not just the `LinearTransferRef` path. Specifically, `transfer_raw_inner` (used by `transfer`, `transfer_raw`, `transfer_to_object`) should remove a stale `TombStone` whenever `object_core.owner` actually changes, mirroring the cleanup already done in `transfer_with_ref`. Alternatively, restrict `unburn()`'s `BURN_ADDRESS` branch to only succeed if the current `TombStone` was created by the same transaction/flow that actually moved the object to `BURN_ADDRESS` (e.g., require that no ordinary transfer occurred since the `TombStone` was written).

### Proof of Concept
Conceptual Move test sequence (based on existing test helpers in `object.move`):
```
// 1. A creates object and soft-burns it (owner stays A)
let (ctor, obj) = create_hero(&a);
object::burn(&a, obj);               // TombStone{original_owner: A}, owner = A

// 2. A normally transfers the object to B (TombStone is NOT cleared)
object::transfer(&a, obj, address_of(&b));
assert!(obj.owner() == address_of(&b), 0);
assert!(exists<TombStone>(obj.object_address()), 0); // still present, stale

// 3. B (unaware of the leftover TombStone) sends the object to BURN_ADDRESS
// via an ordinary transfer, not object::burn_object_with_transfer
object::transfer(&b, obj, BURN_ADDRESS);

// 4. A reclaims the object using the stale TombStone, stealing it from B
object::unburn(&a, obj);
assert!(obj.owner() == address_of(&a), 0); // A regained ownership, not B
```
Note: this analysis is based on static code review; I was not able to run this Move test in this environment to confirm compilation/runtime behavior, so it should be validated with an actual `#[test]` execution before treating it as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L525-533)
```text
    /// Transfer to the destination address using a LinearTransferRef.
    public fun transfer_with_ref(self: LinearTransferRef, to: address) {
        assert!(!exists<Untransferable>(self.self), error::permission_denied(EOBJECT_NOT_TRANSFERRABLE));

        // Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later.
        if (exists<TombStone>(self.self)) {
            let TombStone { original_owner: _ } = move_from<TombStone>(self.self);
        };

```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L572-594)
```text
    public fun transfer_raw(
        owner: &signer,
        object: address,
        to: address,
    ) {
        let owner_address = signer::address_of(owner);
        verify_ungated_and_descendant(owner_address, object);
        transfer_raw_inner(object, to);
    }

    inline fun transfer_raw_inner(object: address, to: address) {
        let object_core = borrow_global_mut<ObjectCore>(object);
        if (object_core.owner != to) {
            event::emit(
                Transfer {
                    object,
                    from: object_core.owner,
                    to,
                },
            );
            object_core.owner = to;
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L645-651)
```text
    public entry fun burn<T: key>(owner: &signer, object: Object<T>) {
        let original_owner = signer::address_of(owner);
        assert!(is_owner(object, original_owner), error::permission_denied(ENOT_OBJECT_OWNER));
        let object_addr = object.inner;
        assert!(!exists<TombStone>(object_addr), EOBJECT_ALREADY_BURNT);
        move_to(&create_signer(object_addr), TombStone { original_owner });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L653-676)
```text
    /// Allow origin owners to reclaim any objects they previous burnt.
    public entry fun unburn<T: key>(
        original_owner: &signer,
        object: Object<T>,
    ) {
        let object_addr = object.inner;
        assert!(exists<TombStone>(object_addr), error::invalid_argument(EOBJECT_NOT_BURNT));

        // The new owner of the object can always unburn it, but if it's the burn address, we go to the old functionality
        let object_core = borrow_global<ObjectCore>(object_addr);
        if (object_core.owner == signer::address_of(original_owner)) {
            let TombStone { original_owner: _ } = move_from<TombStone>(object_addr);
        } else if (object_core.owner == BURN_ADDRESS) {
            // The old functionality
            let TombStone { original_owner: original_owner_addr } = move_from<TombStone>(object_addr);
            assert!(
                original_owner_addr == signer::address_of(original_owner),
                error::permission_denied(ENOT_OBJECT_OWNER)
            );
            transfer_raw_inner(object_addr, original_owner_addr);
        } else {
            abort error::permission_denied(ENOT_OBJECT_OWNER);
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L179-213)
```text
    /// Withdraw `amount` of fungible asset from the given account's primary store.
    public fun withdraw<T: key>(owner: &signer, metadata: Object<T>, amount: u64): FungibleAsset acquires DeriveRefPod {
        let store = ensure_primary_store_exists(signer::address_of(owner), metadata);
        // Check if the store object has been burnt or not. If so, unburn it first.
        may_be_unburn(owner, store);
        dispatchable_fungible_asset::withdraw(owner, store, amount)
    }

    /// Deposit fungible asset `fa` to the given account's primary store.
    public fun deposit(owner: address, fa: FungibleAsset) acquires DeriveRefPod {
        let metadata = fa.asset_metadata();
        let store = ensure_primary_store_exists(owner, metadata);
        dispatchable_fungible_asset::deposit(store, fa);
    }

    /// Deposit fungible asset `fa` to the given account's primary store using signer.
    public fun deposit_with_signer(owner: &signer, fa: FungibleAsset) acquires DeriveRefPod {
        let metadata = fa.asset_metadata();
        let store = ensure_primary_store_exists(signer::address_of(owner), metadata);
        dispatchable_fungible_asset::deposit(store, fa);
    }

    /// Transfer `amount` of fungible asset from sender's primary store to receiver's primary store.
    public entry fun transfer<T: key>(
        sender: &signer,
        metadata: Object<T>,
        recipient: address,
        amount: u64,
    ) acquires DeriveRefPod {
        let sender_store = ensure_primary_store_exists(signer::address_of(sender), metadata);
        // Check if the sender store object has been burnt or not. If so, unburn it first.
        may_be_unburn(sender, sender_store);
        let recipient_store = ensure_primary_store_exists(recipient, metadata);
        dispatchable_fungible_asset::transfer(sender, sender_store, recipient_store, amount);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L282-286)
```text
    fun may_be_unburn(owner: &signer, store: Object<FungibleStore>) {
        if (store.is_burnt()) {
            object::unburn(owner, store);
        };
    }
```
