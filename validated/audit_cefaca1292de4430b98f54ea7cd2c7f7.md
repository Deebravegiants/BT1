### Title
Stale `TombStone` allows a previous owner to reclaim an object away from its current legitimate owner via `unburn` - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` marks an object as (soft-)burnt by attaching a `TombStone{original_owner}` resource while leaving the object's `owner` field unchanged, and grants that recorded `original_owner` a standing right to reclaim the object later via `unburn`. However, ordinary ownership-transfer paths (`transfer`, `transfer_call`, `transfer_to_object`, `transfer_raw`) never clear this `TombStone`, unlike the `TransferRef`/`LinearTransferRef` path which explicitly does. If an object that was once soft-burnt is later transferred through the ordinary path to a new legitimate owner, and that object (or any subsequent holder) ever ends up at the canonical `BURN_ADDRESS` (a common, framework-endorsed pattern for intentionally and permanently destroying an object), the stale `TombStone` still lets the original (and now unrelated) owner reclaim the object via `unburn`, hijacking custody away from the current/legitimate holder.

### Finding Description
- `TombStone` is defined at [1](#0-0)  and records `original_owner` at the moment `burn` is called, while the "new-style" `burn` leaves the object's actual `owner` field untouched: [2](#0-1) .
- `unburn` trusts the recorded `TombStone.original_owner` whenever the current on-chain owner equals `BURN_ADDRESS`, and transfers the object back to that recorded address without verifying that no legitimate ownership transfer has happened in between: [3](#0-2) .
- The only code path that clears a stale `TombStone` is `transfer_with_ref` (via `LinearTransferRef`), which explicitly documents this intent ("Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later"): [4](#0-3) .
- The ordinary, far more commonly used transfer entrypoints (`transfer`, `transfer_call`, `transfer_to_object`, `transfer_raw`) all funnel into `transfer_raw_inner`, which only updates the `owner` field and emits an event — it never checks for or clears an existing `TombStone`: [5](#0-4) .

This is the same bug *class* as the external Augur report: a piece of state tied to a previous "dispute"/ownership context (`preemptiveDisputeCrowdsourcer` there, `TombStone.original_owner` here) is reset along one code path but not along a functionally equivalent sibling path, so it silently becomes stale and is later trusted as if it were still consistent with current state — leading to funds/objects being routed to the wrong party.

### Impact Explanation
This is a custody-grade ownership-reassignment bug on live, mainnet-relevant object infrastructure (`aptos_framework::object`), which underlies fungible-asset stores, token objects, and any object-held value. A prior owner who once called `burn` on an object can permanently retain the ability to reclaim that object from *any future legitimate owner*, as soon as the object (through ordinary transfer/marketplace activity, or the owner's own intentional and framework-sanctioned use of `BURN_ADDRESS` to destroy it) ends up at `BURN_ADDRESS`. This breaks the invariant that "object creation, transfer, burn, extensibility, and ownership refs must preserve the intended controller," and results in theft/owner reassignment of object-held value to an unauthorized, unrelated address.

### Likelihood Explanation
Likelihood is high in realistic usage: `burn`/soft-burn is a documented, public entry function usable by any object owner at any time; ordinary `transfer`/`transfer_call` (not `transfer_with_ref`) is the standard path used by wallets, marketplaces, and most application code; and sending objects to `BURN_ADDRESS` via ordinary transfer is the natural/expected mechanism end users and dApps use to permanently destroy an object. No privileged access or unusual conditions are required — only that an object was soft-burnt at some point in its history and later organically transferred and eventually sent to the burn address.

### Recommendation
Clear the `TombStone` (if present) inside `transfer_raw_inner` (or at minimum inside `transfer_raw`) whenever ownership actually changes, mirroring the cleanup already performed in `transfer_with_ref`, so that any ordinary ownership transfer invalidates a prior owner's reclaim rights, not just transfers made via `LinearTransferRef`.

### Proof of Concept
1. `A` creates object `O` (`A` is owner).
2. `A` calls `object::burn(A, O)` → `TombStone{original_owner: A}` is attached; `O.owner` remains `A` (see lines 645-651).
3. `A` sells/transfers `O` to `B` using an ordinary transfer, e.g. `object::transfer(A, O, B)` → `O.owner = B`. The `TombStone{original_owner: A}` is **not** cleared (lines 572-594).
4. `B`, the legitimate new owner, later sends `O` to `BURN_ADDRESS` via an ordinary transfer (e.g. `object::transfer_call(B, O, BURN_ADDRESS)`) intending to permanently destroy it. `O.owner = BURN_ADDRESS`; `TombStone` is still untouched.
5. `A` calls `object::unburn(A, O)`. Since `exists<TombStone>(O)` is true and `O.owner == BURN_ADDRESS`, the second branch fires: `TombStone.original_owner (A) == signer::address_of(A)` passes, and `transfer_raw_inner(O, A)` executes — restoring ownership of `O` to `A`, even though `A` had legitimately sold `O` to `B` in step 3 and `B` intended it destroyed in step 4.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L114-119)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    /// This is added to objects that are burnt (ownership transferred to BURN_ADDRESS).
    struct TombStone has key {
        /// Track the previous owner before the object is burnt so they can reclaim later if so desired.
        original_owner: address,
    }
```

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L549-594)
```text
    /// Entry function that can be used to transfer, if allow_ungated_transfer is set true.
    public entry fun transfer_call(
        owner: &signer,
        object: address,
        to: address,
    ) {
        transfer_raw(owner, object, to)
    }

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
