## Title
Stale `TombStone.original_owner` allows a prior owner to reclaim an object after it changes hands and is later sent to `BURN_ADDRESS` via an ordinary transfer - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` performs a "soft burn" that only attaches a `TombStone` marker recording the current owner as `original_owner`; it does not change `ObjectCore.owner` and does not disable transfers. Ordinary ungated transfers (`object::transfer`, `transfer_call`, `transfer_to_object`, all routed through `transfer_raw_inner`) never inspect or clear an existing `TombStone`. Only the capability-gated `TransferRef`-based `transfer_with_ref` path clears a stale `TombStone`. As a result, once an object has ever been soft-burnt, its `TombStone.original_owner` can become stale relative to the object's real ownership history, and `unburn`'s "legacy" branch (triggered when the object's current owner is `BURN_ADDRESS`) will restore ownership to that stale, no-longer-legitimate address instead of the object's true last owner.

### Finding Description
`object::burn` (aptos-move/framework/aptos-framework/sources/object.move:645-651) creates a `TombStone { original_owner }` for the *current* owner without altering `ObjectCore.owner` or `allow_ungated_transfer`: [1](#0-0) 

Ordinary transfers go through `transfer_raw_inner`, which only updates `ObjectCore.owner` and emits an event - it has no knowledge of `TombStone`: [2](#0-1) 

By contrast, the `LinearTransferRef`-based `transfer_with_ref` path *does* explicitly purge a stale `TombStone` before transferring, specifically to prevent a previous owner from reclaiming later: [3](#0-2) 

`unburn` then trusts the (possibly stale) `TombStone.original_owner` when the object's current owner is `BURN_ADDRESS`: [4](#0-3) 

Because `transfer_raw_inner` (used by every plain, capability-free transfer: `transfer`, `transfer_call`, `transfer_to_object`) never clears `TombStone`, the following sequence produces a stale claim:
1. Owner A soft-burns object O via `object::burn`. `TombStone{original_owner: A}` is created; `O.owner` stays `A`.
2. A transfers O normally to B (`object::transfer`/`transfer_call`) - `TombStone` is untouched and still says `original_owner = A`, even though `O.owner` is now `B`.
3. B later wants to genuinely destroy/burn O and does so the "obvious" way - sending it to the well-known `BURN_ADDRESS` constant via a normal ungated transfer (`object::transfer_call(b, O, BURN_ADDRESS)`), since `object::burn` itself does not actually move the object to `BURN_ADDRESS`. `TombStone` is still untouched (`original_owner = A`).
4. A calls `object::unburn(A, O)`. Since `O.owner == BURN_ADDRESS`, the "legacy" branch executes: it checks `TombStone.original_owner (A) == signer (A)` → passes, and calls `transfer_raw_inner(O, A)`, reassigning ownership of O to A - not to B, who was the legitimate final owner before the object was sent to the burn address.

### Impact Explanation
This breaks the custody invariant that object ownership transfers must preserve the intended controller: a stale, no-longer-entitled address (A) can reassign ownership of an object away from its rightful last owner (B) purely because of an earlier, unrelated soft-burn performed while A still owned it. This applies to any `Object<T>`-based asset, including NFTs/token objects and other object-held value, and constitutes unauthorized owner reassignment / theft of object-held value with no privileged action required by the attacker beyond having burnt the object at some earlier point in its ownership history.

### Likelihood Explanation
The precondition (some owner having called `object::burn` at any point in the object's history) is a normal, permissionless, single-signer action, not a privileged or rare one - it is documented as a way to "hide" an object from indexers while it is still fully transferable. Sending an object to the well-known `BURN_ADDRESS` constant via an ordinary transfer is also a natural action for any current owner intending to genuinely destroy an asset, since the soft `burn` function's semantics (keep ownership, just mark tombstoned) are non-obvious and do not match the common intuition of "sending to the burn address." No collusion or privileged capability is required from either A or B for the exploit to trigger.

### Recommendation
`transfer_raw_inner` (or its callers `transfer_raw`/`transfer`/`transfer_call`/`transfer_to_object`) should clear any existing `TombStone` on ordinary ownership transfer, mirroring the behavior already implemented in `transfer_with_ref`, so that a `TombStone.original_owner` can never become stale relative to the object's actual ownership chain. Alternatively, `unburn`'s legacy `BURN_ADDRESS` branch should be removed/deprecated in favor of requiring soft-burnt objects to be un-burnable only by their *current* owner, closing the path that trusts a historical `original_owner` field after untracked ownership changes.

### Proof of Concept
```move
// Assume O is created and owned by A.
object::burn(&a_signer, O);                       // TombStone{original_owner: A}, O.owner == A
object::transfer_call(&a_signer, O_addr, B_addr);  // O.owner == B, TombStone untouched (still A)
object::transfer_call(&b_signer, O_addr, BURN_ADDRESS); // O.owner == BURN_ADDRESS, TombStone untouched (still A)
object::unburn<T>(&a_signer, O);                   // succeeds: O.owner reassigned to A, not B
```
This mirrors the existing test structure in `object.move` (`test_burn_and_unburn_old`, `test_cannot_unburn_after_transfer_with_ref`) but interposes an intermediate ordinary transfer via `transfer_call`/`transfer` between the soft `burn` and the send-to-`BURN_ADDRESS` step, which those tests do not cover. [5](#0-4)

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L976-993)
```text
    #[test(creator = @0x123)]
    fun test_burn_and_unburn_old(creator: &signer) {
        let (hero_constructor, hero) = create_hero(creator);
        // Freeze the object.
        let transfer_ref = hero_constructor.generate_transfer_ref();
        transfer_ref.disable_ungated_transfer();

        // Owner should be able to burn, despite ungated transfer disallowed.
        burn_object_with_transfer(creator, hero);
        assert!(hero.owner() == BURN_ADDRESS, 0);
        assert!(!hero.ungated_transfer_allowed(), 0);

        // Owner should be able to reclaim.
        unburn(creator, hero);
        assert!(hero.owner() == signer::address_of(creator), 0);
        // Object still frozen.
        assert!(!hero.ungated_transfer_allowed(), 0);
    }
```
