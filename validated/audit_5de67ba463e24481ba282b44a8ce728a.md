## Summary

Aptos's Object model (`aptos_framework::object`) implements a "soft burn" mechanism where `burn()` attaches a `TombStone{ original_owner }` resource to an object without changing its actual `owner` field, and `unburn()` lets that recorded `original_owner` reclaim the object once it eventually lands at the well-known `BURN_ADDRESS`. The `TombStone.original_owner` field is *only* cleared on the `TransferRef`-based transfer path (`transfer_with_ref`), but is silently left in place across ordinary ungated `object::transfer` calls. This lets a former owner who pre-poisons an object with a soft burn, then transfers it away, later reclaim the object from a completely different, legitimate current owner the moment that owner sends it to `BURN_ADDRESS` — an officially documented and expected disposal path. This is a direct custody/ownership-reassignment analog to the external report's core lesson: an operation whose safety silently depends on state a different party can manipulate, breaking a custody invariant (here: "whoever burns an object should be the only one who can reclaim it") for value held in Aptos objects (NFTs, token objects, or any object carrying assets/capabilities).

## Finding Description

`object::burn` marks an object as (soft) burnt without transferring it away: [1](#0-0) 

`object::unburn` allows the `original_owner` recorded in the `TombStone` to reclaim the object once it is later actually sent to `BURN_ADDRESS`: [2](#0-1) 

The plain ungated transfer path (`transfer` / `transfer_raw` / `transfer_raw_inner`) never touches or clears an existing `TombStone`: [3](#0-2) 

Only the `TransferRef`-mediated `transfer_with_ref` path explicitly clears a stale `TombStone` before transferring, precisely because the authors recognized the reclaim risk on that path: [4](#0-3) 

This asymmetry is the root cause: the mitigation ("Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later") was applied to the `TransferRef` path only, and was not applied to the far more common ordinary `object::transfer` path.

**Exploit chain (all production, non-test-only entry functions):**
1. Attacker `A` creates or otherwise owns `Object<T>` and calls `object::burn(A, obj)`. This moves `TombStone{ original_owner: A }` to the object's address; `ObjectCore.owner` remains `A`.
2. `A` transfers the object normally to victim `B` via `object::transfer(A, obj, B)` (ungated transfer is enabled by default and unaffected by the `TombStone`). The `TombStone{ original_owner: A }` is **not** cleared.
3. `B`, now the legitimate sole owner, at some later point decides to dispose of/burn the object. Because `object::burn` will abort with `EOBJECT_ALREADY_BURNT` (the stale `TombStone` from step 1 still exists), `B` (or tooling built on top of the documented `BURN_ADDRESS` semantics) instead performs a plain `object::transfer(B, obj, BURN_ADDRESS)`.
4. `A` calls `object::unburn(A, obj)`. Since `ObjectCore.owner == BURN_ADDRESS`, the `else if` branch fires, reads the stale `original_owner_addr == A` from the `TombStone`, and since the caller is `A`, `transfer_raw_inner(object_addr, A)` executes — `A` regains ownership of an object that `B`, not `A`, actually burned.

The custody invariant broken: "recovery rights for a burnt object belong to whoever performed the burn," per the module's own documentation ("Allow origin owners to reclaim any objects they previously burnt"). Because the `original_owner` field is never refreshed across ordinary transfers, `A` — who has no legitimate claim after transferring the object away in step 2 — inherits `B`'s recovery rights.

## Impact Explanation

This is a genuine object-ownership/custody-control violation:
- **Unauthorized owner reassignment**: `A` regains control of an object it no longer legitimately owns, at `B`'s expense.
- **Corrupted recovery rights / wrong-holder redirection**: value that should be irrecoverable by anyone but `B` (or permanently retired) is instead handed back to `A`, matching the gate's "moves value to the wrong holder or destroys recovery rights."
- Any object type is affected — NFTs/collectibles, token objects, or objects that hold `FungibleStore`s, capabilities, or other custody-critical resources via `move_to`. If the object holds a fungible asset store or similar value, this becomes outright theft of that value.
- Any owner in the object's transfer history who has ever called `burn()` on it retains a dormant, indefinite claim that resurfaces whenever the object (however many owners later) is disposed of via `BURN_ADDRESS`.

## Likelihood Explanation

Medium-High. The attack requires no privileged access — only ordinary public entry functions (`burn`, `transfer`, `unburn`) available to any signer. The only behavioral requirement on the victim's side is that they eventually send the object to the well-documented `BURN_ADDRESS` (explicitly described in the module as "Address where unwanted objects can be forcefully transferred to"), which is a normal, expected disposal action for objects a user no longer wants. Because `object::burn()` itself will abort for an already-tombstoned object (poisoned by the attacker beforehand), any wallet/marketplace tooling that falls back to a raw transfer to the burn address for disposal purposes will unknowingly trigger this exact vulnerable path.

## Recommendation

Clear any existing `TombStone` on the object whenever ownership changes via the ordinary ungated transfer path (`transfer_raw_inner`), not only in `transfer_with_ref`. Alternatively, tie `original_owner` validation in `unburn` to the owner immediately preceding the transfer to `BURN_ADDRESS` (e.g., re-stamp/overwrite `TombStone.original_owner` on every ownership change, or disallow `burn`/leave a "soft burn" residue that must be re-established by the current owner immediately before sending to `BURN_ADDRESS`).

## Proof of Concept

```move
// Assume T is any object type, obj is created and owned by A.
// Step 1: A soft-burns while still owner.
object::burn(&A, obj);                       // TombStone{original_owner: A}; owner stays A

// Step 2: A transfers the (stale-tombstoned) object away normally.
object::transfer(&A, obj, signer::address_of(&B));   // owner = B; TombStone untouched

// Step 3: B, unaware of the stale TombStone, disposes of the object
// (object::burn(&B, obj) would abort with EOBJECT_ALREADY_BURNT,
// so B/tooling instead sends it to the documented burn address):
object::transfer(&B, obj, BURN_ADDRESS);     // owner = BURN_ADDRESS

// Step 4: A reclaims the object B just burned.
object::unburn(&A, obj);                     // owner = A  <-- theft: B's burn was hijacked by A
``` [5](#0-4)

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L645-676)
```text
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
