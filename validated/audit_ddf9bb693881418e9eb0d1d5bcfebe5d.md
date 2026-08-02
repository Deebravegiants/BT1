## Custody Invariant Reduction

The RedStone bug's root cause is that a *stale piece of state* (an old signed price) can be re-accepted as valid because the validity check compares it against the wrong reference (`block.timestamp`) instead of the actual state it's supposed to supersede (the previously cached price/timestamp). Generalized invariant: **any cached "point-in-time" metadata that grants a privileged action must be invalidated whenever the underlying custody state it refers to changes; otherwise stale metadata can be replayed against a newer state to break custody.**

## Candidate Paths Considered

1. `code.move` upgrade-policy/upgrade-number monotonicity — solid, upgrade_number is strictly derived from stored registry, no stale-vs-live mismatch.
2. `multisig_account.move` timelock (`can_execute_with_timelock`) — timestamp is compared against the transaction's own immutable `creation_time_secs`, not a mutable substitute; no rollback possible.
3. `account.move` rotation/signer-capability proof challenges — sequence numbers are always read fresh from the live `Account` resource at verification time; no caching issue.
4. **`object.move` `TombStone`/`burn`/`unburn` reclaim mechanism** — a cached `original_owner` field is checked against live ownership state, but is not invalidated on all paths that change that live state. This is the strongest match.

## Title
Stale `TombStone.original_owner` allows a former object owner to steal an object back after it is legitimately transferred and later burned - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

## Summary
`object::burn` records the calling owner's address in a `TombStone` without disabling ungated transfers or otherwise binding the tombstone to the current ownership state. Only the `TransferRef`-based transfer path (`transfer_with_ref`) clears a stale `TombStone` before granting the LinearTransferRef holder's move — plain/ungated transfers (`transfer`, `transfer_call`, `transfer_raw`) never touch it. If an object is tombstoned by owner A, later legitimately transferred to B via an ordinary (non-`TransferRef`) transfer, and B (or anyone downstream) subsequently sends the object to the well-known `BURN_ADDRESS`, the leftover `TombStone{original_owner: A}` still satisfies `unburn`'s reclaim check, letting A — who no longer owns the object — pull it back to themselves instead of it staying burned or going to B.

## Finding Description
`burn` only tombstones the object; it does not disable transfers: [1](#0-0) 

`unburn`'s reclaim branch trusts the tombstone's recorded `original_owner` field once the current owner equals `BURN_ADDRESS`, without any check that this owner is the account that most recently sent the object to `BURN_ADDRESS`: [2](#0-1) 

Crucially, the developers were aware that a stale `TombStone` is dangerous after an ownership transfer — but the fix was only applied to the `TransferRef`-gated path: [3](#0-2) 

The ordinary/ungated transfer path used for normal peer-to-peer or marketplace transfers does not perform this cleanup: [4](#0-3) 

`create_object`/`create_named_object` default `allow_ungated_transfer` to `true`, and `burn` never flips it to `false`, so an object can be freely re-transferred by ordinary means while still carrying a stale `TombStone`.

**Broken invariant:** `TombStone.original_owner` is treated as authoritative proof of "who is entitled to reclaim this object from the burn address," but it is never invalidated when true custody of the object changes hands through the normal (non-`TransferRef`) transfer path — exactly analogous to the oracle using `block.timestamp` instead of validating against the actually-cached observation.

## Impact Explanation
This is a custody-grade owner-reassignment bug: a previous, no-longer-entitled owner can unilaterally reclaim (steal) an object — including any object-based fungible asset store, token, or other object-held value — away from its legitimate, current owner once that object reaches `BURN_ADDRESS`, regardless of how many legitimate transfers happened in between. This is unauthorized ownership takeover of object-held value with no privileged-caller assumption, satisfying the custody impact gate (owner reassignment / theft of object-held value).

## Likelihood Explanation
The trigger requires: (1) an owner calling the public, permissionless `object::burn` entry function, (2) the object having ungated transfer enabled (the default), (3) a subsequent ordinary transfer to a new owner, and (4) any transfer of the object to the well-known, hardcoded `BURN_ADDRESS` constant (a public constant in `object.move`, plausible as a generic "discard" convention reused by other contracts, marketplaces, or accidental sends). No privileged role, governance, or admin capability is required — only standard entry functions (`burn`, `transfer`/`transfer_call`, and `unburn`), making this practically reachable by any user who wants to weaponize it against a future buyer of an object they previously "soft-burned."

## Recommendation
Invalidate the `TombStone` (or otherwise disassociate `original_owner` from reclaim rights) on every path that changes `ObjectCore.owner`, not just `transfer_with_ref`. Concretely, add TombStone cleanup logic inside `transfer_raw_inner` (used by both `transfer_raw`/`transfer`/`transfer_call` and `transfer_with_ref`), or alternatively have `burn` disable `allow_ungated_transfer` so a tombstoned object cannot change hands except through the burn/unburn or `TransferRef` lifecycle that properly manages the tombstone.

## Proof of Concept
1. A creates/owns object `O` with default `allow_ungated_transfer = true`.
2. A calls `object::burn(A, O)` → `TombStone{original_owner: A}` is stored; `O.owner` remains `A`.
3. A calls `object::transfer(A, O, B)` (ordinary transfer, not via `TransferRef`) → `O.owner = B`. `TombStone{original_owner: A}` is untouched (confirmed by `transfer_raw_inner` at lines 582-594 having no TombStone-clearing logic).
4. B (unaware of the stale tombstone, or via any app/marketplace flow) later calls `object::transfer(B, O, BURN_ADDRESS)` to genuinely discard/burn `O` → `O.owner = BURN_ADDRESS`.
5. A calls `object::unburn(A, O)`. Since `TombStone` exists, `O.owner == BURN_ADDRESS`, and `TombStone.original_owner == A`, the assert at line 668-671 passes, and `transfer_raw_inner(object_addr, A)` at line 672 sets `O.owner = A` — A has reclaimed the object that B legitimately owned and discarded, instead of it staying at `BURN_ADDRESS` or being reclaimable only by B.

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
