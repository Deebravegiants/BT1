## Title
Stale `TombStone.original_owner` Survives Ungated `object::transfer`, Allowing a Former Owner to Reclaim (Steal) an Object Sent to the Canonical Burn Address - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` records a "soft burn" marker (`TombStone { original_owner }`) without actually moving the object's ownership. `object::unburn` later allows the recorded `original_owner` to reclaim the object once it reaches `BURN_ADDRESS`. The bug is that the only transfer path that clears a stale `TombStone` is `transfer_with_ref` (the `LinearTransferRef` path). The ordinary/ungated transfer path (`object::transfer`, `transfer_call`, `transfer_raw`, `transfer_to_object` → `transfer_raw_inner`) never checks for or clears an existing `TombStone`. This lets a *former* owner who once called `burn()` retain a dormant claim that resurfaces and lets them steal the object away from a legitimate, later owner the moment that later owner sends it to `BURN_ADDRESS` — a widely-understood on-chain "burn" pattern.

### Finding Description
- `burn<T>()` only asserts current ownership and attaches a marker; it does **not** change `ObjectCore.owner`: [1](#0-0) 

- `unburn<T>()` grants reclamation rights back to the address recorded in the (potentially stale) `TombStone` whenever the object's current owner is `BURN_ADDRESS`: [2](#0-1) 

- The generic/ungated transfer path used by `transfer`, `transfer_call`, `transfer_to_object`, and `transfer_raw` goes through `transfer_raw_inner`, which mutates `owner` directly and has **no knowledge of `TombStone`**: [3](#0-2) 

- In contrast, the `TransferRef`/`LinearTransferRef` path explicitly clears a stale `TombStone` to prevent exactly this scenario, proving the framework authors were aware of the risk but did not close the other transfer path: [4](#0-3) 

Because `burn()` leaves `owner` untouched and the "soft burn" marker is only meant to hide the object from indexers, an object can be freely transferred multiple times through normal ownership changes while carrying an invisible, unresolved `TombStone` tied to an old, unrelated owner. This is directly analogous to the Linea bug's root cause: state set by a privileged/one-time action (`addL1L2MessageHashes` / `burn`) is not properly invalidated or reconciled across a later, independent state transition, letting stale authorization be replayed to seize control an actor should no longer have.

### Impact Explanation
Any object (which may wrap a `FungibleStore`, a token, or other value-bearing resources — ownership of the object gates `fungible_asset::withdraw`/`deposit` via `object::owns`/`is_owner`) can be stolen back from `BURN_ADDRESS` by a stale former owner, even though the actual current owner legitimately intended to permanently destroy/relinquish it. This is an unauthorized owner reassignment of object-held value, directly matching the custody-impact gate ("Theft ... or owner reassignment of ... object-held value" and "custody accounting corruption that moves value to the wrong holder").

### Likelihood Explanation
The precondition is simple and requires no special privilege: any account that has ever called `object::burn` on an object it owned, and later transferred that object away via a normal (non-`TransferRef`) transfer, retains a silent, indefinitely-lived claim. `BURN_ADDRESS` (`0xff...ff`) is a well-known "send here to destroy" address pattern that marketplaces, dApps, or users may use directly via `object::transfer`/`transfer_call` without ever calling `object::burn` themselves — they have no way to know or check whether a stale `TombStone` from a prior owner exists, since it is designed to be indexer-hidden. This makes exploitation plausible in ordinary secondary-market object flows (e.g., NFT/token-object resale followed by disposal).

### Recommendation
- Clear any existing `TombStone` on every ownership-changing transfer path, not just `transfer_with_ref`. Add the same "undo soft burn" logic (or an assertion that no `TombStone` exists) inside `transfer_raw_inner`/`transfer_raw`.
- Alternatively, make `unburn` additionally require that no intervening ownership transfer occurred since the `TombStone` was created (e.g., track the owner at burn time separately from `original_owner`, and only allow reclamation from `BURN_ADDRESS` if the immediately preceding owner recorded matches whoever actually sent it to `BURN_ADDRESS`).

### Proof of Concept
1. Owner `A` creates/owns object `O` holding a `FungibleStore` with balance.
2. `A` calls `object::burn(A, O)` → `TombStone { original_owner: A }` is attached; `O.owner` remains `A`.
3. `A` sells/transfers `O` to `B` via `object::transfer(A, O, B)` (ordinary path) → `transfer_raw_inner` only updates `owner`; `TombStone{A}` is left untouched.
4. `B`, now the legitimate owner, later decides to destroy/relinquish `O` by sending it to the canonical burn sink: `object::transfer(B, O, BURN_ADDRESS)`.
5. `A` calls `object::unburn(A, O)`. Since `TombStone` exists and `O.owner == BURN_ADDRESS`, and `TombStone.original_owner == A == signer`, `transfer_raw_inner(O, A)` executes, returning full ownership (and the underlying `FungibleStore`/token value) to `A` — even though `A` had no rights to `O` at the time `B` burned it.

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
