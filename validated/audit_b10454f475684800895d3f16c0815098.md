### Title
Stale `TombStone` lets a past owner reclaim an object after a legitimate owner sends it to `BURN_ADDRESS` via plain `transfer`/`transfer_call` - ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
`object::transfer_with_ref()` explicitly strips a `TombStone` when ownership changes through a `LinearTransferRef`, but the ordinary owner-signed transfer path (`transfer`, `transfer_call`, `transfer_to_object` → `transfer_raw` → `transfer_raw_inner`) never does. Because `TombStone.original_owner` is never invalidated on a normal transfer, a party that once called `object::burn()` on an object it owned can later reclaim that same object from `BURN_ADDRESS` via `unburn()` even after having legitimately transferred it away to someone else, and even after that new owner independently sent it to `BURN_ADDRESS` intending permanent destruction.

### Finding Description
`burn()` only tags the object with a `TombStone{original_owner}`; it does not change `ObjectCore.owner` nor disable `allow_ungated_transfer`: [1](#0-0) 

The object therefore remains fully transferable through the standard entry points, which route through `transfer_raw_inner`: [2](#0-1) 

`transfer_raw_inner` only updates `ObjectCore.owner`/emits an event — it never checks for or clears an existing `TombStone`. Compare this to `transfer_with_ref`, which is explicitly written to prevent stale-tombstone reclaim: [3](#0-2) 

`unburn()` grants recovery rights based solely on the stale `TombStone.original_owner` field and the current `ObjectCore.owner`: [4](#0-3) 

Root cause: the invariant "only the account that most recently and rightfully sent an object to `BURN_ADDRESS` may reclaim it" is enforced only on the `TransferRef`/`LinearTransferRef` path, not on the plain owner-signed transfer path. `BURN_ADDRESS` is a normal, transferable address, reachable by any owner via ordinary `transfer`/`transfer_call`, so the asymmetry is directly exploitable without any privileged capability.

### Impact Explanation
This breaks the custody invariant that ownership/recovery rights over an object must track its actual current legitimate owner. A previous owner (Alice) can:
1. Own object `X` and call `object::burn(X)` (TombStone{owner: Alice} set, `X` still owned by Alice).
2. Sell/transfer `X` to Bob via the normal `object::transfer`/`transfer_call` path (TombStone is not cleared, silently carried over).
3. At any later time, when Bob (the legitimate, current owner, unaware the object still carries Alice's stale tombstone) sends `X` to `BURN_ADDRESS` for real destruction (a common blockchain "burn" pattern), Alice can call `unburn(X)` and reclaim ownership of `X` for herself, taking the asset that rightfully belonged to Bob.

This is unauthorized owner reassignment / theft of object-held value with no privileged assumption — any account can plant this trap on any object it owns before selling it. It applies to any object type (NFTs, wrapped tokens, resource-account-controlling objects, code objects) built on top of `aptos_framework::object`, making it a broad, mainnet-relevant custody-corruption bug.

### Likelihood Explanation
The precondition (calling public `burn()` before transferring an owned object away) is trivial and requires no special privilege — any user can pre-plant the tombstone on an asset before selling/transferring it. The trigger (the new owner sending the object to the well-known `BURN_ADDRESS` constant, a common intended-destruction action) is a realistic and expected user action, not an edge case. No governance or admin assumption is needed, and the exploit is fully within an ordinary user's capability set, making likelihood high.

### Recommendation
Make `transfer_raw_inner` (or `transfer_raw`) clear any existing `TombStone` on ownership change, mirroring the logic already present in `transfer_with_ref`:
```move
inline fun transfer_raw_inner(object: address, to: address) {
    let object_core = borrow_global_mut<ObjectCore>(object);
    if (object_core.owner != to) {
        if (exists<TombStone>(object)) {
            let TombStone { original_owner: _ } = move_from<TombStone>(object);
        };
        event::emit(Transfer { object, from: object_core.owner, to });
        object_core.owner = to;
    };
}
```
Add regression tests covering: burn → plain transfer to a third party → transfer to `BURN_ADDRESS` by the new owner → attempted `unburn` by the original burner (should fail), to prevent silent reintroduction of this asymmetry.

### Proof of Concept
```move
// Alice owns object X (ObjectCore.owner == @alice)
object::burn<T>(&alice, x);                       // TombStone{original_owner: @alice} added; owner still @alice

// Alice sells/transfers X to Bob via the normal path (TombStone NOT cleared)
object::transfer_call(&alice, x_addr, @bob);       // owner becomes @bob; TombStone{@alice} persists

// Bob, believing X carries no special state, burns it "for real"
object::transfer_call(&bob, x_addr, BURN_ADDRESS); // owner becomes BURN_ADDRESS; TombStone{@alice} still present

// Alice reclaims Bob's asset
object::unburn<T>(&alice, x);
// object_core.owner == BURN_ADDRESS -> branch 2
// original_owner_addr (@alice) == signer::address_of(@alice) -> true
// transfer_raw_inner(x_addr, @alice) executes: Alice now owns X again, stolen from Bob.
```

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
