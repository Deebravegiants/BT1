## Title
Stale `TombStone` survives normal ownership transfer, letting a past owner hijack an object burned by its current legitimate owner — (File: `aptos-move/framework/aptos-framework/sources/object.move`)

## Summary
The soft-burn/`unburn` mechanism in the Aptos `object` module ties reclaim rights to a `TombStone.original_owner` field that is written once at burn time and is never cleared by an ordinary ownership transfer (`transfer`, `transfer_raw`, `transfer_to_object`). Only the privileged `TransferRef`-based `transfer_with_ref` path clears it. This lets a **previous** owner, who burned the object while they owned it, later reclaim the object from a completely different, legitimate current owner once that current owner performs a genuine burn (transfer to `BURN_ADDRESS`), stealing custody of any object-held value away from its rightful controller.

## Finding Description
`burn()` creates a `TombStone { original_owner }` at the object's address but — unlike the legacy `burn_object_with_transfer` — does **not** change `ObjectCore.owner`: [1](#0-0) 

`unburn()` later inspects the *current* owner to decide how to react: [2](#0-1) 

If the current owner equals `BURN_ADDRESS`, the function trusts the `original_owner` stored in the (potentially stale) `TombStone` and unconditionally transfers the object back to that address via `transfer_raw_inner`.

The only place that clears a `TombStone` on transfer is the privileged `LinearTransferRef.transfer_with_ref` path: [3](#0-2) 

The ordinary, unprivileged transfer paths (`transfer`, `transfer_raw`, `transfer_raw_inner`, `transfer_to_object`) never touch `TombStone` at all: [4](#0-3) 

Because of this asymmetry, a `TombStone` created by owner A survives an arbitrary number of subsequent legitimate ownership changes made through the normal `transfer` entry function. If a later legitimate owner B decides to genuinely burn the object by sending it to `BURN_ADDRESS` (the documented "old functionality" path that `unburn`'s second branch still supports), owner A's leftover `TombStone` becomes live again and lets A — who has had no relationship to the object since transferring it away — reclaim ownership instead of it staying permanently burned (or being reclaimable only by B).

## Impact Explanation
This breaks the core custody invariant that "object creation, transfer, burn, and ownership refs must preserve the intended controller." A past, now-unrelated address can reassign ownership of a live object (and everything it holds — nested resources, fungible asset stores, NFTs) away from its current legitimate owner, purely because it once briefly held and soft-burned the object earlier in its history. This is an unauthorized owner-reassignment / theft primitive tied directly to object-held value, satisfying the custody-impact gate (theft/owner reassignment of object-held value, and corruption of burn/recovery rights).

## Likelihood Explanation
The precondition (an object having passed through an owner who called `burn()` on it, followed by a later legitimate owner sending it to the fixed, publicly known `BURN_ADDRESS`) is realistic: `burn()` is a normal entry function any owner can call at any point in an object's lifetime, and burning-by-transfer-to-`BURN_ADDRESS` is explicitly preserved as supported legacy behavior in `unburn()`'s second branch. No special privilege is required by the attacker beyond having been a prior owner — a completely ordinary, low-cost, and repeatable scenario for objects that change hands (secondary markets, marketplaces, gifting, resource-account transfers, etc.).

## Recommendation
Clear any existing `TombStone` on every ownership-changing path, not just `transfer_with_ref`. Concretely, have `transfer_raw_inner` (used by `transfer`, `transfer_raw`, `transfer_to_object`) remove `TombStone` whenever `object_core.owner` actually changes, mirroring the logic already present in `transfer_with_ref`. Alternatively, scope reclaim rights to the *immediately preceding* owner rather than storing a single unversioned `original_owner`, or require that `unburn`'s `BURN_ADDRESS` branch check that no ordinary transfer occurred between the burn and the current burn-address transfer (e.g., via a monotonic transfer/version counter recorded in the `TombStone`).

## Proof of Concept
```move
#[test(alice = @0x123, bob = @0x456)]
fun test_stale_tombstone_steals_burned_object(alice: &signer, bob: &signer) {
    // 1. Alice creates and owns object O.
    let (ctor, obj) = create_hero(alice); // any Object<T> works

    // 2. Alice "soft burns" it: TombStone{original_owner: alice} is created,
    //    but ownership stays with Alice (per current burn() semantics).
    burn(alice, obj);

    // 3. Alice transfers O normally to Bob. TombStone is NOT cleared
    //    because transfer()/transfer_raw() never touch TombStone.
    transfer(alice, obj, signer::address_of(bob));
    assert!(obj.owner() == signer::address_of(bob), 0);

    // 4. Bob, the legitimate current owner, decides to permanently burn O
    //    the "old" way by sending it to BURN_ADDRESS.
    transfer(bob, obj, BURN_ADDRESS);
    assert!(obj.owner() == BURN_ADDRESS, 1);

    // 5. Alice — no longer related to the object — reclaims it using her
    //    stale TombStone, stealing it from Bob's intended permanent burn.
    unburn(alice, obj);
    assert!(obj.owner() == signer::address_of(alice), 2); // theft confirmed
}
```
This test demonstrates that Alice, despite having relinquished the object to Bob through a fully legitimate transfer, can regain ownership the moment Bob attempts a genuine burn — because her old `TombStone` record was never invalidated by the intervening transfer.

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
