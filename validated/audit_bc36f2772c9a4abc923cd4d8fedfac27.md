## Analysis

`object::unburn` does correctly reject a caller who isn't the current owner (in the normal case): if `object_core.owner` is neither `signer::address_of(original_owner)` nor `BURN_ADDRESS`, it aborts with `ENOT_OBJECT_OWNER` [1](#0-0) . So the specific claim "unprivileged caller can unburn an object it does not control while `owner()` still resolves to `original_owner`" is not directly true — `burn()` leaves `owner()` unchanged (equal to the burner) rather than "resolving to original_owner post-burn" while some other party controls it [2](#0-1) , and a genuine subsequent owner-change via `transfer()`/`transfer_raw()` blocks that stale burner from reclaiming, because the `owner==BURN_ADDRESS` branch is the only reclaim path and it is gated by both current owner state and a match against the stored `original_owner`.

However, tracing the code further reveals a real, related custody defect: the `TombStone` left by `burn()` is only cleared when ownership moves via `transfer_with_ref` (capability-based transfer) [3](#0-2) , but **not** when ownership moves via the ordinary signer-authorized `transfer()` / `transfer_raw()` / `transfer_raw_inner()` path [4](#0-3) . This asymmetry produces a stale-`TombStone` custody bug:

1. Owner A calls `burn(A, object)` → `TombStone{original_owner: A}` is attached; `owner()` stays `A` [2](#0-1) .
2. A calls plain `transfer(A, object, B)` → true ownership moves to B, but the stale `TombStone{original_owner: A}` is **not** removed, since `transfer_raw_inner` has no TombStone-clearing logic [5](#0-4) . (`burn()` itself can't be called again by B to refresh the record — it asserts `!exists<TombStone>` [6](#0-5) .)
3. At any later point, B (now the legitimate owner) sends the object to `BURN_ADDRESS` via ordinary `transfer(B, object, BURN_ADDRESS)` — a fully authorized action within B's own custody rights.
4. A (who no longer holds any custody over the object since step 2) calls `unburn(A, object)`. Since `object_core.owner == BURN_ADDRESS`, the second branch fires, and the assertion `original_owner_addr == signer::address_of(original_owner)` passes because the stale record still says `A` [7](#0-6) . Ownership is restored to A, not B, even though A had no relationship to the object at the moment it reached `BURN_ADDRESS`.

This does cross a custody boundary: A regains ownership authority over an object that legitimately belonged to B, purely due to a leftover data artifact from an earlier, unrelated burn cycle that the framework never invalidated on ordinary transfer.

### Title
Stale `TombStone.original_owner` record surviving ordinary `transfer()` lets a past burner reclaim an object it no longer owns - (`aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` records the burner's address in a `TombStone` without clearing ownership, and this record is only invalidated by the capability-based `transfer_with_ref` path, not by the common signer-based `transfer`/`transfer_raw` path. As a result, if an object is burned, then normally transferred to a new owner, and that new owner later sends it to `BURN_ADDRESS` for any reason, the original (and no longer related) burner can call `unburn` and reclaim ownership from the current legitimate custody chain.

### Finding Description
`transfer_with_ref` explicitly documents and implements the fix for this exact hazard ("Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later") [8](#0-7) , proving the risk was recognized for one transfer mechanism but the fix was not applied to the far more commonly used `transfer`/`transfer_raw`/`transfer_to_object` entry points, all of which bottom out in `transfer_raw_inner`, which never touches `TombStone` [5](#0-4) .

### Impact Explanation
An address that has fully and legitimately relinquished custody of an object can regain ownership of it later, without the current owner's consent, provided the object is ever moved to `BURN_ADDRESS` again (a state reachable through ordinary `transfer`). This corrupts the `owner` field of `ObjectCore` and misattributes custody, directly matching the "wrong holder" custody-corruption criteria for object ownership.

### Likelihood Explanation
Requires the object to have been burned at least once historically, transferred normally afterward, and later moved to `BURN_ADDRESS` again by any (legitimate) owner. This is a plausible sequence for any object/NFT-style asset that changes hands multiple times and where an owner sends it to the conventional burn address as their own disposal action — not requiring any privileged access, only ordinary signer-authorized transfers.

### Recommendation
Clear any existing `TombStone` in `transfer_raw_inner` (or in `transfer_raw`/`transfer`) whenever true ownership changes via the ordinary signer-based path, mirroring the protection already implemented in `transfer_with_ref`, so that a `TombStone` can never outlive the ownership epoch in which it was created.

### Proof of Concept
```move
#[test(a = @0xA, b = @0xB)]
fun test_stale_tombstone_reclaim(a: &signer, b: &signer) {
    use aptos_framework::object;

    let (_, hero) = object::create_hero(a);

    // Step 1: A burns (TombStone{original_owner: A}, owner stays A)
    object::burn(a, hero);
    assert!(hero.owner() == signer::address_of(a), 0);

    // Step 2: A legitimately transfers real ownership to B via ordinary transfer.
    // TombStone is NOT cleared by transfer_raw_inner.
    object::transfer(a, hero, signer::address_of(b));
    assert!(hero.owner() == signer::address_of(b), 1);

    // Step 3: B, now the true owner, sends the object to BURN_ADDRESS
    // for its own reasons via ordinary transfer (not object::burn()).
    let burn_address = @0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
    object::transfer(b, hero, burn_address);
    assert!(hero.owner() == burn_address, 2);

    // Step 4: A, who no longer has any custody relationship with the object,
    // reclaims it using the stale TombStone record.
    object::unburn(a, hero);
    assert!(hero.owner() == signer::address_of(a), 3); // A regained ownership, not B
}
``` [9](#0-8)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L525-538)
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L641-676)
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
