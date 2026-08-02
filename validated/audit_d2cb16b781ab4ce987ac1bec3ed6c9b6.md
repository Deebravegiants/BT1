## Title
Stale `TombStone.original_owner` allows a historical, unprivileged former owner to reclaim an object after it has been legitimately transferred away and later sent to `BURN_ADDRESS` - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

## Summary
`object::burn` records the *current* owner into a `TombStone` resource but does not restrict further transfers of the object, and the ordinary transfer path (`object::transfer` / `transfer_raw`) never clears or updates that `TombStone`. Only the `TransferRef`-based path (`transfer_with_ref`) clears it. Consequently, once an object has ever been soft-burnt, its `TombStone.original_owner` field becomes a **stale** authority record that survives arbitrary subsequent ordinary ownership changes. If the object is later moved to the well-known `BURN_ADDRESS` by any current, legitimate owner (a documented, valid operation), `unburn` will let the *original, no-longer-privileged* burner reclaim the object — bypassing every owner who legitimately held it in between.

## Finding Description
`object::burn` (aptos-move/framework/aptos-framework/sources/object.move:645-651) stores the caller's address as `original_owner` in a `TombStone`, but does not disable `allow_ungated_transfer` or otherwise gate the object: [1](#0-0) 

Ordinary transfers go through `transfer` → `transfer_raw` → `transfer_raw_inner`, none of which inspect or clear `TombStone`: [2](#0-1) 

Only the `LinearTransferRef` path explicitly clears a stale `TombStone` before allowing transfer, precisely because the authors recognized the object could otherwise be reclaimed by a party no longer entitled to it: [3](#0-2) 

`unburn` uses the (potentially stale) `TombStone.original_owner` as the authority to reassign ownership whenever the object's current owner happens to equal `BURN_ADDRESS`: [4](#0-3) 

`BURN_ADDRESS` is a fixed, publicly known constant address, and objects can be moved there through the completely ordinary, ungated `object::transfer` entry function (it is just another address; the framework doc even calls it "the address where unwanted objects can be forcefully transferred to"): [5](#0-4) 

**Attack path:**
1. Attacker (owner1) owns object `O` (e.g., a token/NFT wrapped as an `Object<T>`).
2. Attacker calls `object::burn(owner1, O)`. This only creates `TombStone{ original_owner: owner1 }`; `O` remains fully owned and transferable by owner1 (`allow_ungated_transfer` untouched).
3. Attacker transfers `O` normally (sale, gift, marketplace listing) to victim (owner2) via `object::transfer`. `ObjectCore.owner` becomes owner2. `TombStone{ original_owner: owner1 }` is **not** cleared because `transfer_raw_inner` never touches it.
4. Owner2 (or any later legitimate holder) at some point transfers `O` to `BURN_ADDRESS` via an ordinary `object::transfer` call — a perfectly valid operation for any current owner, and one implied as a supported pattern by the `BURN_ADDRESS` constant's own doc comment.
5. Attacker (owner1) — who has had zero ownership claim on `O` since step 3 — calls `object::unburn(owner1, O)`. Because `ObjectCore.owner == BURN_ADDRESS`, the second branch fires: `TombStone.original_owner (owner1) == signer::address_of(original_owner) (owner1)` passes, and `transfer_raw_inner(object_addr, owner1)` reassigns `O` back to the attacker.

The attacker recovers full ownership of an object that legitimately passed through one or more other owners, entirely bypassing their custody rights.

## Impact Explanation
This is a direct custody violation: unauthorized owner reassignment of an object-held asset (token object/NFT) by a party with no current ownership claim, root-caused entirely in `aptos_framework::object` (no admin/governance assumption, no leaked keys, no social engineering — purely a stale-state bug). Any dApp that lets users soft-burn objects and later resells/gifts them (a normal, encouraged use of `burn`/`unburn` per the module's own doc: "Original owners can reclaim burnt objects any time in the future by calling unburn") is exposed. Since `object::burn`/`unburn`/`transfer` are all public entry functions usable directly by any unprivileged account, this is a high-severity, mainnet-relevant custody bug affecting object-based value.

## Likelihood Explanation
The trigger requires only ordinary, permissionless operations (`burn`, `transfer`, `unburn`) — no privileged role, no race condition, no consensus timing dependency. The only additional condition is that some legitimate holder in the ownership chain sends the object to `BURN_ADDRESS` via a normal transfer, which the framework's own naming/documentation of `BURN_ADDRESS` as a place to "forcefully transfer unwanted objects" makes a realistic, even encouraged, action for asset cleanup/destruction flows outside the `burn()`/`unburn()` API.

## Recommendation
- Have `object::burn` disable ungated transfers on the object (or otherwise gate subsequent transfers) so a soft-burnt object cannot silently change hands while a `TombStone` is attached, OR
- Have `transfer_raw_inner` (or all normal transfer paths) clear any existing `TombStone` whenever ownership actually changes to a party other than the recorded `original_owner`, mirroring the behavior already implemented in `transfer_with_ref`, OR
- In `unburn`'s `BURN_ADDRESS` branch, additionally verify that no intervening ordinary transfer occurred since the `TombStone` was created (e.g., by tracking the owner at burn time versus the owner immediately preceding the `BURN_ADDRESS` transfer), rather than trusting the potentially stale `original_owner` field as sole authority.

## Proof of Concept
1. `owner1` creates object `O` and calls `object::burn(owner1, O)` → `TombStone{original_owner: owner1}` created; `O` still owned by `owner1`.
2. `owner1` calls `object::transfer(owner1, O, owner2)` → `ObjectCore.owner = owner2`; `TombStone` unchanged.
3. `owner2` (unaware of prior soft-burn) later calls `object::transfer(owner2, O, BURN_ADDRESS)` to discard the object.
4. `owner1` calls `object::unburn(owner1, O)`.
   - `exists<TombStone>(O)` → true.
   - `object_core.owner (BURN_ADDRESS) == signer::address_of(owner1)`? false → falls to `else if`.
   - `object_core.owner == BURN_ADDRESS` → true; `original_owner_addr (owner1) == signer::address_of(owner1)` → true.
   - `transfer_raw_inner(O, owner1)` executes → `ObjectCore.owner = owner1`.
5. `owner1` now owns `O` again, despite having relinquished it to `owner2` in step 2 through a fully legitimate transfer. [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L97-98)
```text
    /// Address where unwanted objects can be forcefully transferred to.
    const BURN_ADDRESS: address = @0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
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
