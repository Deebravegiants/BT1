### Title
Stale `TombStone.original_owner` lets a former owner reclaim an object sent to `BURN_ADDRESS` by a later legitimate owner — ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
`object::burn()` performs a "soft burn" that leaves the object's ownership unchanged and only attaches a `TombStone { original_owner }` resource. Only the `TransferRef`-based transfer path (`transfer_with_ref`) clears a pre-existing `TombStone` on ownership change; the ungated/raw transfer path (`transfer`, `transfer_raw`, `transfer_to_object`, `transfer_call`) does not. If a new owner later moves the same object to the legacy `BURN_ADDRESS`, `unburn()` will return the object to the address recorded in the stale `TombStone` — the *original* (no-longer-legitimate) owner — instead of the account that actually sent it there.

### Finding Description
`burn<T>` does not transfer the object anywhere; it only asserts current ownership and attaches a `TombStone`: [1](#0-0) 

`unburn<T>` branches on the *current* owner of the object: [2](#0-1) 
- If current owner == caller → tombstone is simply dropped (safe).
- If current owner == `BURN_ADDRESS` → the object is transferred to `TombStone.original_owner`, gated only by the caller matching that stored address (the legacy `burn_object_with_transfer` flow, kept for backward compatibility).

The only transfer path that clears a stale `TombStone` is the `LinearTransferRef`-based one: [3](#0-2) 

The plain ungated transfer path used by `object::transfer` / `transfer_raw` / `transfer_to_object` does **not** touch `TombStone` at all: [4](#0-3) 

Because `BURN_ADDRESS` (`0xff…ff`) is a public, ordinary address, any owner can send an object there with the standard `object::transfer` entry function as a common "burn" idiom — there is nothing that forbids using this path, and there is no check in `transfer_raw_inner`/`verify_ungated_and_descendant` for `is_burnt()`.

**Exploit invariant break:** the custody invariant is that `TombStone.original_owner` should always reflect the party entitled to reclaim the object at `BURN_ADDRESS`. This invariant is violated whenever an object with a leftover `TombStone` (from a previous soft-burn by a *former* owner) changes hands via the raw/ungated transfer path and is subsequently sent to `BURN_ADDRESS` by the *new* owner. The recorded `original_owner` field is stale and points to the wrong account.

### Impact Explanation
This is a custody/ownership-control bug: it allows a party with no current rights over the object (a past owner, `A`) to reclaim (steal) an object that a legitimate, unrelated current owner (`B`) intentionally sent to the burn address, believing it was permanently discarded/destroyed. This is a direct "moves value to the wrong holder" / "destroys recovery rights of the rightful holder" scenario for any object-held asset (NFTs, token objects, or any object wrapping value), satisfying the custody impact gate ("Theft … or owner reassignment of … token objects, or other object-held value").

### Likelihood Explanation
Likelihood is realistic though it requires a specific sequence:
1. `A` owns an object and calls `object::burn` (soft burn — ownership unchanged, `TombStone{original_owner: A}` attached).
2. `A` transfers the object to `B` using any ungated-transfer entry point (`object::transfer`, `transfer_raw`, marketplace/dApp flows built on top of these) — a completely normal, unprivileged action that does not require any special capability and does not clear the tombstone.
3. `B`, unaware of the leftover `TombStone`, later disposes of/"burns" the object by sending it to `BURN_ADDRESS` via the same ordinary `object::transfer` entry function (a widely used convention on Aptos for permanently discarding objects since `BURN_ADDRESS` is a normal, public address).
4. `A` calls `object::unburn(A, object)`; because current owner is `BURN_ADDRESS` and the stale tombstone's `original_owner == A`, the object is transferred back to `A` for free.

No governance, admin, or privileged assumptions are required at any step — every action is a standard, publicly callable entry function.

### Recommendation
Clear (or otherwise invalidate) any existing `TombStone` whenever ownership changes via the raw/ungated transfer path (`transfer_raw_inner`), mirroring the behavior already implemented in `transfer_with_ref`. Alternatively, disallow raw/ungated transfers of an object while `is_burnt(object)` is true, forcing all transfers of burnt objects through a path that resolves/clears the tombstone first.

### Proof of Concept
```
// Move pseudo-sequence using public entry points only
1. A calls object::create_named_object / creates Object<T> "obj", owner = A.
2. A calls object::burn(A, obj);
   // TombStone{original_owner: A} attached; obj.owner is still A.
3. A calls object::transfer(A, obj, B);
   // transfer_raw_inner: obj.owner = B. TombStone is left untouched (still original_owner = A).
4. B, wanting to discard obj, calls object::transfer(B, obj, BURN_ADDRESS);
   // transfer_raw_inner: obj.owner = BURN_ADDRESS. TombStone still original_owner = A.
5. A calls object::unburn(A, obj);
   // object_core.owner == BURN_ADDRESS branch taken;
   // asserts TombStone.original_owner (A) == signer::address_of(A) -> passes
   // transfer_raw_inner(obj, A) -> obj.owner = A
   // A has reclaimed an object that B, the legitimate owner, sent to the burn address.
``` [2](#0-1)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L525-547)
```text
    /// Transfer to the destination address using a LinearTransferRef.
    public fun transfer_with_ref(self: LinearTransferRef, to: address) {
        assert!(!exists<Untransferable>(self.self), error::permission_denied(EOBJECT_NOT_TRANSFERRABLE));

        // Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later.
        if (exists<TombStone>(self.self)) {
            let TombStone { original_owner: _ } = move_from<TombStone>(self.self);
        };

        let object = borrow_global_mut<ObjectCore>(self.self);
        assert!(
            object.owner == self.owner,
            error::permission_denied(ENOT_OBJECT_OWNER),
        );
        event::emit(
            Transfer {
                object: self.self,
                from: object.owner,
                to,
            },
        );
        object.owner = to;
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L558-594)
```text
    /// Transfers ownership of the object (and all associated resources) at the specified address
    /// for Object<T> to the "to" address.
    public entry fun transfer<T: key>(
        owner: &signer,
        object: Object<T>,
        to: address,
    ) {
        transfer_raw(owner, object.inner, to)
    }

    /// Attempts to transfer using addresses only. Transfers the given object if
    /// allow_ungated_transfer is set true. Note, that this allows the owner of a nested object to
    /// transfer that object, so long as allow_ungated_transfer is enabled at each stage in the
    /// hierarchy.
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
