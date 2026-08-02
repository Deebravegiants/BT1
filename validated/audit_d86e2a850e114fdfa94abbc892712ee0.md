# Stale `TombStone` lets a former owner reclaim an object after it changes hands and is later sent to the burn address

### Title
Unauthorized object reclamation via stale `TombStone.original_owner` surviving ungated ownership transfers - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` does not actually move the object to `BURN_ADDRESS` — it only attaches a `TombStone{original_owner}` resource while leaving the current owner unchanged. Only the `TransferRef`-based path (`transfer_with_ref`) explicitly strips a stale `TombStone` before honoring a transfer. The ordinary ungated transfer path (`object::transfer` / `transfer_raw` / `transfer_to_object`, all routed through `transfer_raw_inner`) never checks for or removes an existing `TombStone`. Combined with `unburn`'s logic that trusts `TombStone.original_owner` whenever the object's current owner is `BURN_ADDRESS`, a party who once owned the object and called `burn()` on it can reclaim the object out of a later owner's custody, even after the object has legitimately changed hands one or more times.

### Finding Description
Relevant code in `aptos-move/framework/aptos-framework/sources/object.move`: [1](#0-0) 

`burn()` records `original_owner` in a `TombStone` but does **not** change `ObjectCore.owner`. The object keeps its current owner; the `TombStone` is purely a marker. [2](#0-1) 

`transfer_raw_inner`, used by `transfer_raw`, `transfer`, and `transfer_to_object`, only updates `ObjectCore.owner` and emits an event — it never inspects or clears `TombStone`.

By contrast, the `LinearTransferRef` path explicitly guards against this: [3](#0-2) 

The comment makes the intent explicit: *"Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later."* This guarantee is only enforced on the `TransferRef` transfer path, not on the plain ungated `object::transfer` path.

Finally, `unburn()` trusts the stale `TombStone` whenever the object is currently owned by `BURN_ADDRESS`: [4](#0-3) 

Attack sequence:
1. Alice owns object `X` (no `TransferRef`-based lockup). She calls `object::burn(alice, X)`. This adds `TombStone{original_owner: alice}` to `X`; `ObjectCore.owner` for `X` is still `alice`.
2. Alice transfers `X` to Bob using the ordinary ungated `object::transfer(alice, X, bob)` (e.g., as part of a sale). `transfer_raw_inner` sets `owner = bob` but leaves the stale `TombStone{original_owner: alice}` in place. Bob only observes that he is now the owner; nothing on-chain flags that a tombstone exists (and if Bob later tries the "official" `object::burn`, it will abort with `EOBJECT_ALREADY_BURNT`, nudging an unaware caller toward a manual transfer instead).
3. At some later point Bob wants to discard/burn `X` and does so the "naive" way — a plain `object::transfer(bob, X, BURN_ADDRESS)` — rather than calling `object::burn` (which would abort due to the pre-existing tombstone). `ObjectCore.owner` becomes `BURN_ADDRESS`; the stale `TombStone{original_owner: alice}` is still attached, untouched.
4. Alice calls `object::unburn(alice, X)`. Since `object_core.owner == BURN_ADDRESS` and `TombStone.original_owner == alice`, the check at line 668-671 passes and `transfer_raw_inner(object_addr, alice)` executes, reassigning ownership of `X` back to Alice — a party with no legitimate claim at the time of the burn.

### Impact Explanation
This breaks the object-ownership custody invariant that only the rightful/current owner may control the disposition of an object once ownership has legitimately transferred. It allows a prior owner to plant a "sleeper" claim on any object they once owned and later silently reclaim it — including fungible-asset/token-object stores or any object holding value — from a subsequent legitimate owner, effectively stealing the object (and any resources it carries) once that owner sends it to the well-known burn address through the standard, framework-provided `object::transfer` entry function rather than the (blocked) `object::burn`. Given objects are the base primitive underlying NFTs, fungible asset stores, and custom asset-bearing resources on Aptos, this is a custody-grade theft/owner-reassignment bug with mainnet relevance.

### Likelihood Explanation
Likelihood is moderate-to-high: it requires no special privilege — any object owner can pre-plant a tombstone before transferring/selling the object, and it only requires a subsequent owner to later send the object to the canonical burn address via the standard `object::transfer` function (a natural pattern to "destroy" an asset, especially since calling the framework's own `burn()` will unexpectedly abort with `EOBJECT_ALREADY_BURNT` due to the attacker's leftover tombstone, which can push unaware developers/users toward the vulnerable manual-transfer-to-burn-address workaround).

### Recommendation
Make `TombStone` clearing consistent across all ownership-changing paths, not just `transfer_with_ref`. Concretely, `transfer_raw_inner` (or its callers `transfer_raw`/`transfer`/`transfer_to_object`) should remove any existing `TombStone` on the object whenever ownership changes, mirroring the logic already present in `transfer_with_ref`:
```move
inline fun transfer_raw_inner(object: address, to: address) {
    if (exists<TombStone>(object)) {
        let TombStone { original_owner: _ } = move_from<TombStone>(object);
    };
    ...
}
```
Alternatively, `unburn`'s `BURN_ADDRESS` branch should additionally verify that no intervening legitimate transfer happened after the tombstone was created (e.g., by tracking a transfer sequence/version number and requiring it be unchanged from when the tombstone was recorded).

### Proof of Concept
```move
// Alice owns object X.
object::burn(&alice, x);                       // TombStone{original_owner: alice}; owner still alice
object::transfer(&alice, x, signer::address_of(&bob)); // owner -> bob; stale TombStone remains

// Bob later tries the "proper" burn and it fails:
// object::burn(&bob, x) -> aborts EOBJECT_ALREADY_BURNT

// Bob instead discards it the naive way:
object::transfer(&bob, x, BURN_ADDRESS);        // owner -> BURN_ADDRESS

// Alice reclaims Bob's discarded object using her stale tombstone:
object::unburn(&alice, x);                      // owner -> alice (theft)
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L582-594)
```text
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
