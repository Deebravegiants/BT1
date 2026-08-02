Based on the investigation, a genuine custody analog exists in `aptos_framework::object`'s soft-burn / `TombStone` reclaim mechanism.

### Title
Stale `TombStone.original_owner` survives ordinary object transfers, letting a previous owner reclaim an object away from its legitimate current owner - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn()` performs a "soft burn": it does not move the object, it merely records the caller as `TombStone.original_owner` while leaving `ObjectCore.owner` unchanged, explicitly so "Original owners can reclaim burnt objects any time in the future by calling `unburn`" [1](#0-0) . The only code path that clears a stale `TombStone` on transfer is `transfer_with_ref` (the `LinearTransferRef` path), which explicitly removes it "so we don't want the original owner to be able to reclaim by calling unburn later" [2](#0-1) . Ordinary ungated transfers (`object::transfer`, `object::transfer_call`, `object::transfer_to_object`, all routed through `transfer_raw` → `transfer_raw_inner`) never touch `TombStone` at all [3](#0-2) .

### Finding Description
The custody invariant broken here is: *only the entity with a currently valid, unrevoked claim should be able to reassign ownership of an object*. `unburn()`'s reclaim logic is: [4](#0-3) 

If the object's current owner equals `BURN_ADDRESS`, `unburn()` trusts whatever address is stored in the (possibly very old) `TombStone.original_owner` field and reassigns ownership to it via `transfer_raw_inner`, with no check that this address had any legitimate relationship to the object at the time it reached `BURN_ADDRESS`.

Because ordinary transfers (`transfer_raw_inner`) never clear or update `TombStone`, the following sequence is possible entirely with unprivileged, legitimate-looking transactions:
1. Alice owns object `O` (with `allow_ungated_transfer = true`, the default). Alice calls `object::burn(alice, O)`. This creates `TombStone { original_owner: alice }`, but `O.owner` stays `alice` [5](#0-4) .
2. Alice later transfers `O` to Bob via a plain `object::transfer` / `transfer_call` (not a marketplace/TransferRef-based flow). `TombStone { original_owner: alice }` is left in place untouched, since `transfer_raw_inner` never inspects or clears it [6](#0-5) .
3. Bob is now the legitimate owner and has no visibility into the stale tombstone (he cannot call `object::burn()` again on it — it would abort with `EOBJECT_ALREADY_BURNT` — but that's the only signal). If Bob (or any later legitimate owner down the chain) at some point sends `O` to `BURN_ADDRESS` via the standard ungated `transfer_call` (a common "destroy my object" pattern for objects that don't expose a `DeleteRef`), `O.owner` becomes `BURN_ADDRESS`, and the stale tombstone from step 1 is still attached.
4. Alice — who no longer owns or has any right to `O` — calls `object::unburn(alice, O)`. Since `O.owner == BURN_ADDRESS` and `TombStone.original_owner == alice`, the second branch fires and `transfer_raw_inner` reassigns `O.owner` back to Alice [7](#0-6) .

Alice has thus reclaimed ownership of an object she sold/transferred away, purely because she happened to soft-burn it once before transferring it, and the eventual (unrelated) burn-to-null-address by a later legitimate owner reactivated her stale claim.

### Impact Explanation
This is a custody-grade unauthorized owner reassignment of object-held value: any fungible/non-fungible token object, code object, or any resource stored under an `Object<T>` can be silently reclaimed by a past owner who is no longer part of the legitimate ownership chain. It also inverts the expected "burn to `BURN_ADDRESS` == permanent" semantics that many downstream contracts and users rely on for destroying an object, turning what looks like an irreversible burn into a reversible one — but reversible in favor of the wrong party (a stale prior owner instead of the current holder). This directly maps to the required impact "Theft ... or owner reassignment of ... token objects, or other object-held value."

### Likelihood Explanation
The precondition set is realistic and requires no special privilege: `allow_ungated_transfer` is the default `true` for freshly created objects [8](#0-7) , `object::burn`/`object::unburn`/`object::transfer_call` are all public entry functions callable by any address, and many collections/objects never transfer through the `TransferRef`/`LinearTransferRef` path at all (only marketplace-style flows do, per `transfer_with_constructor_ref` and `listing.move` usage patterns seen in the codebase) [9](#0-8) . Any object that is ever soft-burned once, then later ordinarily transferred and eventually sent to `BURN_ADDRESS` by any subsequent holder, is exploitable — this is a plausible, unprivileged sequence rather than a contrived edge case.

### Recommendation
`transfer_raw_inner` (or `transfer_raw`) should invalidate/clear any existing `TombStone` on the object whenever ownership changes through the ungated path, mirroring the cleanup already done in `transfer_with_ref`. Alternatively, `unburn()`'s `BURN_ADDRESS` branch should require that the tombstoned original owner was the most recent owner immediately prior to reaching `BURN_ADDRESS` (e.g., track "owner immediately before burn" freshly rather than trusting an unbounded-lifetime `TombStone` value), or disallow soft-burnt objects from being further transferred without first clearing the tombstone.

### Proof of Concept
```move
// Alice owns object O (ungated transfer allowed by default).
object::burn(&alice, o);                  // TombStone{original_owner: alice}, O.owner still alice
object::transfer(&alice, o, bob_addr);    // ordinary transfer: O.owner = bob, TombStone untouched
// ... time passes, Bob legitimately owns O ...
object::transfer_call(&bob, o_addr, BURN_ADDRESS); // Bob "destroys" O, expecting permanence
object::unburn(&alice, o);                // succeeds: O.owner reassigned back to alice,
                                           // even though alice sold/transferred O to bob long ago
assert!(object::owner(o) == alice_addr);  // Alice has reclaimed value she no longer owned
```

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L100-112)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    /// The core of the object model that defines ownership, transferability, and events.
    struct ObjectCore has key {
        /// Used by guid to guarantee globally unique objects and create event streams
        guid_creation_num: u64,
        /// The address (object or account) that owns this object
        owner: address,
        /// Object transferring is a common operation, this allows for disabling and enabling
        /// transfers bypassing the use of a TransferRef.
        allow_ungated_transfer: bool,
        /// Emitted events upon transferring of ownership.
        transfer_events: event::EventHandle<TransferEvent>,
    }
```

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L641-651)
```text
    /// Add a TombStone to the object.  The object will then be interpreted as hidden via indexers.
    /// This only works for objects directly owned and for simplicity does not apply to indirectly owned objects.
    /// Original owners can reclaim burnt objects any time in the future by calling unburn.
    /// Please use the test only [`object::burn_object_with_transfer`] for testing with previously burned objects.
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

**File:** aptos-move/move-examples/marketplace/sources/listing.move (L71-97)
```text
    public(friend) fun init(
        creator: &signer,
        object: Object<ObjectCore>,
        fee_schedule: Object<FeeSchedule>,
        start_time: u64,
    ): (signer, ConstructorRef) {
        let constructor_ref = object::create_object_from_account(creator);
        // Once we construct this, both the listing and its contents are soulbound until the conclusion.
        let transfer_ref = object::generate_transfer_ref(&constructor_ref);
        object::disable_ungated_transfer(&transfer_ref);
        let listing_signer = object::generate_signer(&constructor_ref);

        let listing = Listing {
            object,
            seller: signer::address_of(creator),
            fee_schedule,
            start_time,
            delete_ref: object::generate_delete_ref(&constructor_ref),
            extend_ref: object::generate_extend_ref(&constructor_ref),
        };
        move_to(&listing_signer, listing);

        let listing_addr = object::address_from_constructor_ref(&constructor_ref);
        object::transfer(creator, object, listing_addr);

        (listing_signer, constructor_ref)
    }
```
