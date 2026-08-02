## Custody Analog Found: Stale `TombStone.original_owner` Lets a Prior Owner Reclaim an Object from `BURN_ADDRESS` After a Legitimate Ownership Transfer

### Title
Stale soft-burn `TombStone` survives ungated `transfer`, letting a prior owner reclaim an object out from under the current owner via `unburn` - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` performs a "soft burn" that records a `TombStone{original_owner}` without changing `ObjectCore.owner` [1](#0-0) . If the object is subsequently transferred to a new owner through the ordinary ungated path (`transfer`/`transfer_raw`/`transfer_to_object`), that path never clears the `TombStone` [2](#0-1) . Only the `TransferRef`-based `transfer_with_ref` explicitly clears it, and the code comment confirms this was a known concern for exactly one path but not the other [3](#0-2) . As a result, when the new (legitimate) owner later sends the object to `BURN_ADDRESS` via an ordinary transfer, `unburn` still reads the stale `original_owner` field and returns the object to the prior owner instead of the current one [4](#0-3) .

### Finding Description
1. Owner Alice calls `object::burn(alice, object)`. This only asserts she is the current owner and moves a `TombStone{original_owner: alice}` into the object's resources; `ObjectCore.owner` is untouched [1](#0-0) .
2. Alice sells/transfers the object to Bob using the standard, ungated `object::transfer` (or `transfer_to_object`), which resolves to `transfer_raw` → `transfer_raw_inner` [5](#0-4) . This inline function only updates `object_core.owner` and emits a `Transfer` event - it contains **no logic to remove an existing `TombStone`**.
3. Bob is now the on-chain, legitimate owner of the object, unaware that a stale `TombStone{original_owner: alice}` is still attached to it.
4. Bob later moves the object to `BURN_ADDRESS` using the same ordinary transfer path (a common pattern for "burning"/discarding an asset by sending it to the null address), which again goes through `transfer_raw_inner` and again does not touch the `TombStone`.
5. Alice now calls `unburn(alice, object)`. Because `object_core.owner == BURN_ADDRESS`, the second branch executes: it reads `original_owner_addr` from the (stale) `TombStone` - which is still `alice`, not `bob` - checks it against the caller, and calls `transfer_raw_inner(object_addr, alice)`, returning the object to Alice [6](#0-5) .

The broken custody invariant: **only the current, real owner (immediately before an object reaches `BURN_ADDRESS`) should ever be able to reclaim it.** Instead, ownership-reclaim authority is bound to a stale `TombStone.original_owner` field that is only invalidated on one of the two production transfer code paths (`transfer_with_ref`), not the other (`transfer`/`transfer_raw`/`transfer_to_object`). The explicit comment on `transfer_with_ref` - "Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later" [7](#0-6)  - shows the exact same risk was recognized and patched for the ref-based path but left open on the ungated path, which is the analog of the `_executeDeposit` report: a validation/side-effect that is applied inconsistently across equivalent code paths, producing an unintended, exploitable outcome on the path that was missed.

Note: the legacy hard-burn function `burn_object_with_transfer` (which does set `owner = BURN_ADDRESS` directly) is `#[test_only]` [8](#0-7) , so on mainnet the `owner == BURN_ADDRESS` state is reached only by combining `object::burn` (soft burn, tombstone) with an ordinary transfer to `BURN_ADDRESS` by whoever owns the object at that time - exactly the multi-owner sequence described above.

### Impact Explanation
This is a direct custody/ownership-control violation on any object (NFT, token object, resource-holding object) that has ever been soft-burned by a past owner and later legitimately transferred: a stranger with no current relationship to the object (the pre-transfer owner) can reclaim it from `BURN_ADDRESS`, taking it away from the actual current owner's chain of custody. Since token objects and other object-held value follow this `ObjectCore`/`TombStone` model, this breaks "Object creation, transfer, burn, extensibility, and ownership refs must preserve the intended controller" and can result in unauthorized reassignment of ownership of live, object-held assets - a high-severity custody impact.

### Likelihood Explanation
The trigger sequence uses only ordinary, publicly callable entry functions (`object::burn`, `object::transfer`/`transfer_to_object`, `object::unburn`) with no privileged signer, no oracle, and no race condition - any user can execute the full sequence against any object they control at each step. The only precondition is that an object passes through a soft-burn by one owner and is later transferred (not burned again) by a subsequent owner to `BURN_ADDRESS` - a plausible real-world flow, since sending assets to the burn address is a common informal "burn" idiom independent of the framework's dedicated `burn()`/`unburn()` API.

### Recommendation
Clear (`move_from`) any existing `TombStone` on the object inside `transfer_raw_inner` (or at minimum inside `transfer_raw`/`transfer`/`transfer_to_object`) whenever ownership actually changes, mirroring the existing protection already present in `LinearTransferRef::transfer_with_ref` [9](#0-8) . This ensures a `TombStone.original_owner` can never refer to an address that is no longer (or was never) the immediately-preceding owner before the object reached `BURN_ADDRESS`.

### Proof of Concept
```
// Alice owns `object`.
object::burn(&alice, object);                       // soft burn: TombStone{original_owner: alice}; owner stays alice

// Alice sells the object to Bob via the ordinary ungated transfer path.
object::transfer(&alice, object, address_of(&bob)); // owner = bob; TombStone NOT cleared (transfer_raw_inner has no tombstone logic)

// Bob later "burns" (discards) the object by sending it to the well-known burn address,
// using the same ordinary transfer function (no special API needed).
object::transfer(&bob, object, BURN_ADDRESS);        // owner = BURN_ADDRESS; TombStone{original_owner: alice} still present

// Alice reclaims the object that Bob believed was permanently burned / that Alice
// no longer had any claim to.
object::unburn(&alice, object);
// owner == BURN_ADDRESS branch taken; original_owner_addr(alice) == signer(alice) passes;
// transfer_raw_inner(object_addr, alice) executes -> object ownership returns to Alice, bypassing Bob entirely.
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L568-594)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L775-787)
```text
    #[test_only]
    /// For testing the previous behavior of `object::burn()`
    ///
    /// Forcefully transfer an unwanted object to BURN_ADDRESS, ignoring whether ungated_transfer is allowed.
    /// This only works for objects directly owned and for simplicity does not apply to indirectly owned objects.
    /// Original owners can reclaim burnt objects any time in the future by calling unburn.
    public fun burn_object_with_transfer<T: key>(owner: &signer, object: Object<T>) {
        let original_owner = signer::address_of(owner);
        assert!(is_owner(object, original_owner), error::permission_denied(ENOT_OBJECT_OWNER));
        let object_addr = object.inner;
        move_to(&create_signer(object_addr), TombStone { original_owner });
        transfer_raw_inner(object_addr, BURN_ADDRESS);
    }
```
