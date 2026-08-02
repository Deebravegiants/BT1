### Title
Stale `TombStone` (soft-burn recovery marker) survives ordinary `object::transfer`, letting a former owner reclaim custody from the current owner - ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
`object::burn` marks an object as soft-burnt by attaching a `TombStone { original_owner }` resource, without changing the object's current `owner` field. The framework only strips this `TombStone` inside `transfer_with_ref` (the `TransferRef`/`LinearTransferRef` path). The plain, far more common transfer path — `transfer`, `transfer_call`, `transfer_to_object`, all of which route through `transfer_raw` → `transfer_raw_inner` — never checks for or removes an existing `TombStone`. This is the same bug class as the reported `removeContract`/`policy` issue: a privileged/recovery marker tied to a prior controller is not cleaned up when control changes hands, so it can be reactivated later with stale authority.

### Finding Description
- `burn<T>()` requires the caller to be the current owner, and stores `TombStone{ original_owner: <that owner> }` at the object address; the object's `owner` field is left unchanged: [1](#0-0) 

- `unburn<T>()` allows reclaiming: if the object's *current* owner still equals `original_owner`, the tombstone is simply dropped; but if the current owner is `BURN_ADDRESS`, it transfers the object back to whichever address is recorded as `TombStone.original_owner` (not to whoever most recently sent it to `BURN_ADDRESS`): [2](#0-1) 

- The **only** place that clears a stale `TombStone` on ownership change is `transfer_with_ref` (the capability-gated `LinearTransferRef` path), with an explicit comment acknowledging the exact hazard this finding describes: [3](#0-2) 

- However, the ordinary owner-signed transfer path — `transfer`, `transfer_call`, `transfer_to_object` → `transfer_raw` → `transfer_raw_inner` — does **not** perform this cleanup at all; it only updates the `owner` field and emits an event: [4](#0-3) 

Consequence: an owner `A` can (1) soft-burn an object they own (`TombStone{original_owner: A}` attached, owner still `A`), then (2) transfer it to `B` via the plain `transfer`/`transfer_call` entry function. Ownership legitimately passes to `B`, but the `TombStone` — now stale — is left in place with `original_owner = A`. `B` has no visibility that this marker exists (it's not part of `ObjectCore`, and burn's purpose is explicitly to hide the object from indexers). If `B` later moves the object to the sentinel `BURN_ADDRESS` (a legitimate, unrestricted operation, since `BURN_ADDRESS` is just an address — nothing prevents a plain `transfer` to it, and the module's own doc calls it the place where "unwanted objects can be forcefully transferred"), the `unburn` second branch becomes satisfiable: current owner is `BURN_ADDRESS`, and the stale `original_owner` field still equals `A`. `A` can now call `unburn(A, object)` and successfully reclaim the object — even though `A` had nothing to do with `B`'s decision to send the object to the burn address, and `B` is the party who should hold any recovery right.

This directly parallels the `removeContract` bug: removing/transferring away control (`removeContract` disallowing the contract; here, transferring ownership away from `A`) leaves behind privileged state (`policy[_contract].methods`; here, `TombStone.original_owner`) that can later be "reactivated" (contract re-whitelisted with old policy; here, `A` reclaiming custody) by an unauthorized/former party.

### Impact Explanation
This breaks the custody invariant that object ownership and recovery rights must track the current, legitimate controller. Concretely:
- Object/token/`FungibleStore`-style custody can be reassigned to a stale former owner instead of the legitimate current owner or their intended burn/recovery target — an "owner reassignment... tied to live assets" and "custody accounting corruption that moves value to the wrong holder or destroys recovery rights," both explicitly in-scope custody impacts.
- It also creates a griefing/DoS side-effect: if `B` (the new legitimate owner) ever tries `object::burn` on the object, it aborts with `EOBJECT_ALREADY_BURNT` because the stale `TombStone` from `A` is still present, even though `B` never burned anything.
- Because `Object<T>` genericaly covers value-bearing types, and the codebase itself wires this exact `burn`/`unburn` machinery into `primary_fungible_store.move`'s `may_be_unburn` for `Object<FungibleStore>` [5](#0-4) , the same stale-tombstone mechanics apply to fungible-asset-holding objects, tying this into asset custody rather than a purely cosmetic/indexing feature.

### Likelihood Explanation
No special privilege is required beyond being an object's owner at some point in its history. The sequence (burn while owning it → plain-transfer it away → wait for it to eventually land at `BURN_ADDRESS` via any ordinary transfer) uses only public, unprivileged entry functions (`burn`, `transfer`/`transfer_call`, `unburn`) and no capability refs. The main precondition is that the object is later sent to `BURN_ADDRESS` via a plain transfer rather than through `burn_object_with_transfer`/`transfer_with_ref`; since `BURN_ADDRESS` is a public, well-known constant intended exactly for "forcefully transferring unwanted objects," this is a realistic and even encouraged usage pattern, making exploitation plausible rather than purely theoretical.

### Recommendation
Clear any existing `TombStone` on **every** ownership-changing path, not just `transfer_with_ref`. Specifically, `transfer_raw_inner` (used by `transfer`, `transfer_call`, `transfer_to_object`, and `transfer_raw`) should perform the same cleanup currently done in `transfer_with_ref`:
```move
if (exists<TombStone>(object)) {
    let TombStone { original_owner: _ } = move_from<TombStone>(object);
};
```
Alternatively/additionally, `unburn`'s `BURN_ADDRESS` branch should not trust a `TombStone.original_owner` value that predates a later ownership transfer — e.g., invalidate/overwrite the tombstone whenever ownership changes for any reason, ensuring the recovery right always tracks the most recent legitimate owner rather than a stale historical one.

### Proof of Concept
1. `A` creates object `O` (owns it), calls `object::burn(A, O)` → `TombStone{original_owner: A}` attached to `O`; `O.owner` remains `A`.
2. `A` calls `object::transfer(A, O, B)` (or `transfer_call`) → `O.owner` becomes `B`. `TombStone{original_owner: A}` is **not** removed (unlike the `transfer_with_ref` path).
3. `B`, unaware of the stale tombstone, later sends `O` to the well-known sentinel via `object::transfer(B, O, BURN_ADDRESS)`.
4. `A` calls `object::unburn(A, O)`. Because `O.owner == BURN_ADDRESS` and `TombStone.original_owner == A`, the assertion at line ~668 passes and `transfer_raw_inner(O, A)` executes, returning custody of `O` to `A` — not to `B`, the actual party who sent it to burn, and without any consent from `B`. [2](#0-1)

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

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L282-286)
```text
    fun may_be_unburn(owner: &signer, store: Object<FungibleStore>) {
        if (store.is_burnt()) {
            object::unburn(owner, store);
        };
    }
```
