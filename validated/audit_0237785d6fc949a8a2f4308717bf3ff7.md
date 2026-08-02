## Custody Analog Found

### Title
Stale `TombStone.original_owner` lets a former object owner reclaim an object from the burn address after it changes hands - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
The external bug is a class of "stale accumulator/state not cleared on state transition" issue: a per-entity value (`_cumulativeRewardPerLpToken`) survives a removal event and is later misapplied after re-addition, letting the wrong party claim value. The Aptos-native analog is in `object::TombStone`: the `original_owner` field recorded at soft-burn time is only cleared when an object is moved via a `LinearTransferRef` (privileged path), but **not** when it is moved via the ordinary ungated `transfer`/`transfer_call` path. This lets a stale, no-longer-current owner reclaim an object out of the burn address after later, legitimate owners have transferred and genuinely burned it.

### Finding Description
`object::burn` tags an object with a `TombStone{original_owner}` without changing its `owner` field: [1](#0-0) 

`object::unburn` later trusts this `original_owner` field to authorize returning the object from `BURN_ADDRESS` back to a claimant: [2](#0-1) 

The ordinary, unprivileged transfer path (`transfer`, `transfer_call`, `transfer_raw` → `transfer_raw_inner`) changes `ObjectCore.owner` but never touches or clears `TombStone`: [3](#0-2) 

By contrast, the privileged `TransferRef`-based path explicitly clears a lingering `TombStone` "so the original owner can't reclaim by calling unburn later": [4](#0-3) 

This asymmetry means `TombStone.original_owner` is a stale field, exactly analogous to `_cumulativeRewardPerLpToken` not being reset on `addRewardToken`: it is written once, then survives an ownership-changing event it should have been invalidated by (an ungated transfer), and is later consumed to grant value/authority to whoever matches the stale value.

**Attack chain:**
1. Alice owns object `X` and calls `object::burn(alice, X)`. This only moves `TombStone{original_owner: alice}` in; `X.owner` stays `alice` (soft burn) — [1](#0-0) .
2. Alice performs an ordinary ungated transfer of `X` to Bob (`object::transfer_call`). `TombStone` is untouched by `transfer_raw_inner` — [5](#0-4) . Now `X.owner == bob`, but `TombStone.original_owner == alice` (stale).
3. Bob cannot call `object::burn` again to overwrite the record, because it aborts if a `TombStone` already exists (`EOBJECT_ALREADY_BURNT`) — [6](#0-5) . Bob instead performs a plain ungated transfer of `X` to `BURN_ADDRESS` to genuinely dispose of it (a common, supported pattern since `transfer_raw_inner` places no restriction on the destination).
4. Alice calls `object::unburn(alice, X)`. Since `X.owner == BURN_ADDRESS` and the stale `TombStone.original_owner == alice`, the check at line 668-671 passes and `transfer_raw_inner(object_addr, alice_addr)` executes, handing `X` back to Alice — [7](#0-6) .

Alice — who no longer legitimately owned `X` at the time it was burned — recovers custody of an asset that its actual, current (and now former) owner Bob deliberately destroyed.

### Impact Explanation
This breaks the fundamental custody invariant that "burnt" objects can only be reclaimed by whoever actually burned/owned them at burn time, not by an arbitrary earlier owner in the object's history. `TombStone`/`burn`/`unburn` apply generically to any `Object<T>` with `ObjectCore` (token objects, digital assets, and other object-held value), so this is a High-impact unauthorized ownership reassignment / theft of object-held value from its legitimate holder.

### Likelihood Explanation
Likelihood is Low-to-Medium: it requires (a) an object being soft-burn-tagged once, (b) subsequently transferred via the ordinary ungated-transfer path rather than a `TransferRef`, and (c) eventually being sent to `BURN_ADDRESS` by a later owner. This is a plausible sequence for objects that support public `burn`, are freely transferable, and where users manually send objects to `BURN_ADDRESS` (a widely used pattern for disposal) rather than exclusively using an app's `TransferRef`-gated burn flow.

### Recommendation
Clear any existing `TombStone` on every ownership-changing transfer, not just the `TransferRef`/`LinearTransferRef` path — i.e., add the same "undo soft burn" cleanup inside `transfer_raw_inner` (or unconditionally re-tag `TombStone.original_owner` to the new owner) so the field cannot outlive the ownership epoch it was recorded for.

### Proof of Concept
```
// Pseudocode using public/entry functions in object.move
let x = object::create_object(alice_addr);          // Alice owns X
object::burn(&alice, x_obj);                          // TombStone{original_owner: alice}, owner still alice
object::transfer_call(&alice, x_addr, bob_addr);      // owner -> bob, TombStone untouched (stale: alice)
object::transfer_call(&bob, x_addr, BURN_ADDRESS);    // Bob genuinely burns; owner -> BURN_ADDRESS
object::unburn(&alice, x_obj);                        // passes: TombStone.original_owner == alice
// result: owner -> alice; Alice reclaims object Bob legitimately burned
```

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
