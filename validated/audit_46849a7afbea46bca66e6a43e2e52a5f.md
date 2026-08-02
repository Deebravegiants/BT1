## Analysis

The Nouns bug is fundamentally about a state (`Expired`) that governance logic treats as **terminal**, but which can silently revert to a live/actionable state (`Queued`) through a code path that doesn't re-validate/clear the stale state, allowing later unauthorized execution against custody value.

Tracing this custody invariant ("a terminal-looking marker must be cleared/re-validated on every path that changes the underlying control state, or it can be replayed by an unprivileged party") into Aptos object custody code reveals the same class of bug in `aptos_framework::object`'s soft-burn/`TombStone` mechanism.

### Title
Stale `TombStone` reclaim rights survive ungated object transfers, allowing a prior owner to hijack burned objects - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` marks an object as "burnt" by attaching a `TombStone{original_owner}` resource **without changing the object's actual owner**. Only one of the two transfer code paths (`transfer_with_ref`, used by `LinearTransferRef`) clears this `TombStone` before completing a transfer. The other path, `transfer_raw_inner` (used by the public `transfer`, `transfer_call`, `transfer_to_object`, and `transfer_raw` entry points, and used internally by real contracts such as the marketplace `Listing::close`), does **not** clear it. Consequently a `TombStone` planted by a prior owner can persist across ordinary transfers and later be exploited via `unburn` to redirect the object away from its legitimate current holder once it reaches `BURN_ADDRESS`.

### Finding Description
- `burn<T>` only requires the caller to currently own the object; it does not move the object to `BURN_ADDRESS`, it just tags it with `TombStone{original_owner}` while `ObjectCore.owner` is unchanged: [1](#0-0) 
- `unburn<T>` allows the caller to reclaim the object either (a) when they are the current owner (simple cleanup), or (b) when the current owner is `BURN_ADDRESS`, in which case the object is sent back to whatever address is recorded as `TombStone.original_owner` — with no check on who actually performed the transfer to `BURN_ADDRESS`: [2](#0-1) 
- `transfer_with_ref` (the `LinearTransferRef` path) explicitly clears any pre-existing `TombStone` before completing a transfer, precisely because "we don't want the original owner to be able to reclaim by calling unburn later": [3](#0-2) 
- However, the ordinary ungated transfer path, `transfer_raw_inner`, used by `transfer_raw`, `transfer`, `transfer_call`, and `transfer_to_object`, performs **no such cleanup** — it only updates `owner` and emits the event: [4](#0-3) 

This asymmetry means the "terminal-looking" burnt marker is not consistently invalidated on every code path that changes custody, exactly mirroring the Nouns issue where an assumed-terminal state (`Expired`) wasn't re-validated against every path that could mutate the underlying condition (`GRACE_PERIOD`).

Concretely, real framework code already uses the un-cleared path: the marketplace example's `Listing::close` transfers the listed object with the plain `object::transfer` function, not `transfer_with_ref`: [5](#0-4) 

### Impact Explanation
An unprivileged former owner can permanently retain a hidden reclaim right on an object they no longer control:
1. Alice owns object `O` and calls `object::burn(alice, O)` — `TombStone{original_owner: alice}` is attached; `O` is still owned by Alice.
2. Alice transfers `O` to Bob via any ordinary transfer path (`object::transfer`, `transfer_call`, or a contract like the marketplace that internally calls plain `transfer`). The stale `TombStone` is **not** cleared.
3. Bob (unaware of the dangling `TombStone`) later sends `O` to `BURN_ADDRESS` via an ordinary transfer, intending a genuine, permanent burn (a common intentional pattern for fee-burn or reward mechanics).
4. Alice calls `object::unburn(alice, O)`. Since `ObjectCore.owner == BURN_ADDRESS` and the recorded `TombStone.original_owner == alice`, `unburn` succeeds and sends `O` back to Alice — not to Bob, and not permanently destroyed as Bob intended.

This corrupts custody: value that should be irrecoverably destroyed (or at minimum controlled by its legitimate final owner) is instead redirected to an unprivileged, unrelated prior owner. This satisfies the custody gate's "theft ... or owner reassignment of ... token objects" and "supply or custody accounting corruption that moves value to the wrong holder or destroys recovery rights."

### Likelihood Explanation
The preconditions are simple and require no privileged action: any account can call `burn` on an object it owns, transfer it away using standard entry functions (which are the default/common transfer path, not the more specialized `TransferRef`), and wait for a subsequent holder to transfer the object to `BURN_ADDRESS` (a normal, expected action for burning). No admin/governance action or race condition is required, only ordinary user transactions — a real code path in this same repository's marketplace example already routes through the vulnerable path.

### Recommendation
Clear any existing `TombStone` on the object inside `transfer_raw_inner` (or more generally, any code path that mutates `ObjectCore.owner`), not just in `transfer_with_ref`, so that reclaim rights cannot outlive a change of custody. Alternatively, bind the reclaim check in `unburn` to the *immediately preceding* owner instead of a persisted `original_owner` field that can be planted long before a later, unrelated burn event.

### Proof of Concept
1. Alice creates/owns object `O`.
2. Alice calls `object::burn<T>(&alice_signer, O)` → `TombStone{original_owner: @alice}` moved to `O`'s address; `O.owner` remains `@alice`.
3. Alice calls `object::transfer<T>(&alice_signer, O, @bob)` (plain ungated transfer) → `O.owner = @bob`; `TombStone` still present (per `transfer_raw_inner`, `aptos-move/framework/aptos-framework/sources/object.move:582-594`, which has no `TombStone` cleanup, unlike `transfer_with_ref` at lines 525-547).
4. Bob, believing the object is unencumbered, calls `object::transfer_call<T>(&bob_signer, O, BURN_ADDRESS)` intending a genuine burn → `O.owner = BURN_ADDRESS`.
5. Alice calls `object::unburn<T>(&alice_signer, O)` → since `O.owner == BURN_ADDRESS` and `TombStone.original_owner == @alice`, the `else if` branch at lines 665-672 succeeds and transfers `O` back to `@alice`, bypassing Bob's intended irrecoverable burn and stealing the object back from the chain of legitimate custody.

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

**File:** aptos-move/move-examples/marketplace/sources/listing.move (L200-205)
```text
        let obj_signer = object::generate_signer_for_extending(&extend_ref);
        if (exists<TokenV1Container>(object::object_address(&object))) {
            extract_or_transfer_tokenv1(closer, recipient, object::convert(object));
        } else {
            object::transfer(&obj_signer, object, recipient);
        };
```
