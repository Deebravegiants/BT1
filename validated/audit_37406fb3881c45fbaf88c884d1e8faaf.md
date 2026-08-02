I found a genuine custody analog: the object burn/unburn mechanism in `object.move` fails to consistently clear the `TombStone` marker across all ownership-transfer paths, allowing a stale burn record to let a **former owner reclaim an object away from its legitimate current owner** once that asset reaches the burn address.

### Title
Stale `TombStone` allows a former owner to reclaim an object burned by a later legitimate owner - (File: aptos-move/framework/aptos-framework/sources/object.move)

### Summary
`object::burn` marks an object as soft-burnt by attaching a `TombStone{original_owner}` resource, without transferring ownership or disabling transfers [1](#0-0) . The `TombStone` is only cleared inside `transfer_with_ref` (the `LinearTransferRef` path) [2](#0-1) , but ordinary ungated transfers (`transfer`, `transfer_call`, `transfer_to_object`, `transfer_raw`) go through `transfer_raw_inner`, which never inspects or clears `TombStone` [3](#0-2) . `unburn` reassigns ownership back to the recorded `original_owner` whenever the object's current owner equals `BURN_ADDRESS`, regardless of how many intervening legitimate owners the object passed through [4](#0-3) .

### Finding Description
The intended invariant is that once an object is transferred away from the account that soft-burned it, that original owner should no longer be able to reclaim the object via `unburn` — this is explicitly the purpose of clearing `TombStone` in `transfer_with_ref`: "Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later" [5](#0-4) .

However, that safeguard only exists on the `LinearTransferRef` transfer path. The far more common plain-transfer entrypoints (`object::transfer`, `object::transfer_call`, `object::transfer_to_object`) call `transfer_raw` → `transfer_raw_inner`, which simply flips the `owner` field and emits a `Transfer` event, with no `TombStone` handling at all [6](#0-5) .

Exploit path:
1. Alice owns object `O`. She calls `object::burn(alice, O)`, creating `TombStone{original_owner: alice}` while `O` stays owned by Alice and remains fully transferable (ungated transfer is untouched) [1](#0-0) .
2. Alice transfers `O` to Bob using the ordinary `object::transfer` entrypoint. `TombStone{original_owner: alice}` persists because this path never touches it.
3. Bob, believing `O` is his to dispose of, later burns/discards it by sending it to the module's documented `BURN_ADDRESS` ("Address where unwanted objects can be forcefully transferred to") via a plain `transfer` [7](#0-6) .
4. Alice calls `object::unburn(alice, O)`. Since `exists<TombStone>(O)` is true and `object_core.owner == BURN_ADDRESS`, the check `original_owner_addr == signer::address_of(alice)` passes, and `transfer_raw_inner` reassigns ownership of `O` back to Alice [8](#0-7) .

Alice — who no longer had any claim on `O` after step 2 — regains full ownership of an asset that Bob (or any later legitimate holder) intentionally discarded, purely because a `TombStone` she created many transfers earlier was never invalidated by the intermediate ordinary transfers.

### Impact Explanation
This breaks the object-ownership custody invariant: "Object creation, transfer, burn, extensibility, and ownership refs must preserve the intended controller." A former, unprivileged owner can reassign ownership of a live object (which may wrap fungible-asset stores, NFTs, or other value) away from its legitimate current/intended-burnt state back to themselves — effectively theft/unauthorized owner reassignment of object-held value, and it can also grief the current owner's intended (irreversible) burn of an asset.

### Likelihood Explanation
Any account that once briefly owned and soft-burned an object, then transferred it away via a normal `transfer` call (the standard, most-used transfer entrypoint across the framework and ecosystem, e.g. token/NFT modules that don't rely on `TransferRef`), retains the ability to reclaim it forever if the object subsequently reaches `BURN_ADDRESS` through any later owner's ordinary transfer. No special privileges, races, or governance actions are required — only ordinary user-level calls to `burn`, `transfer`, and `unburn`.

### Recommendation
Clear the `TombStone` in `transfer_raw_inner` (or more broadly, whenever `object_core.owner` changes through any transfer path, not just `transfer_with_ref`), so a soft-burn record cannot outlive a change of ownership. Alternatively, tie `TombStone.original_owner` validation to the owner at the time immediately preceding the burn-address transfer rather than to a potentially stale historical value.

### Proof of Concept
```
// Alice owns object O
object::burn(&alice, O);                       // TombStone{original_owner: alice}, owner still alice
object::transfer(&alice, O, bob_addr);          // TombStone persists, owner = bob
// ... time passes, Bob legitimately uses/holds O ...
object::transfer(&bob, O, object::burn_address()); // Bob discards O, owner = BURN_ADDRESS
object::unburn(&alice, O);                      // succeeds: owner reassigned back to alice
assert!(object::owner(O) == alice_addr, 0);     // Alice reclaimed an asset Bob discarded
```

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L97-98)
```text
    /// Address where unwanted objects can be forcefully transferred to.
    const BURN_ADDRESS: address = @0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L526-533)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L654-676)
```text
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
