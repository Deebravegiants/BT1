This is a promising custody lead. Let me examine the full `burn`/`unburn`/`transfer` logic in `object.move` to confirm the exact mechanics of the tombstone staleness across regular vs. ref-based transfers.## Finding: Stale `TombStone` Enables a Former Owner to Reclaim (Steal) an Object After It Has Passed Through Other Owners and Been Sent to `BURN_ADDRESS`

### Summary
Aptos' object model implements a "soft burn" via `object::burn`, which attaches a `TombStone { original_owner }` marker to an object without transferring ownership or disabling transfers. Regular ownership-transfer entry points (`transfer`, `transfer_raw`, `transfer_call`, `transfer_to_object`) never clear this marker, while only the `TransferRef`-based path (`transfer_with_ref`) does. This inconsistency lets a `TombStone` written by an old owner survive one or more subsequent ordinary transfers. If the object is later moved to `BURN_ADDRESS` (a plain address reachable by any ordinary `transfer` call), `unburn` will honor the stale `TombStone` and return the object to the old, no-longer-relevant owner — not to the party who actually burned it.

### Finding Description
`object::burn` only checks current ownership and stamps a tombstone; it does not disable ungated transfers: [1](#0-0) 

The regular transfer path used by `transfer`, `transfer_raw`, `transfer_call`, and `transfer_to_object` only updates the `owner` field and emits an event — it never inspects or clears any existing `TombStone`: [2](#0-1) 

By contrast, the `TransferRef`-based path explicitly removes a stale tombstone before transferring, precisely to prevent the "original owner reclaims later" scenario: [3](#0-2) 

`unburn` trusts the `TombStone.original_owner` recorded at burn time whenever the *current* owner is `BURN_ADDRESS`, regardless of how many times the object changed hands (via ordinary transfer) between the tombstone being written and the object eventually landing at `BURN_ADDRESS`: [4](#0-3) 

Because plain transfers never clear the tombstone, and because `BURN_ADDRESS` is simply a fixed constant address that any owner can send an object to via an ordinary `transfer` call (not only through the dedicated burn helper), the invariant "only the party who actually sent the object to `BURN_ADDRESS` (or the current owner) may reclaim it" is broken.

### Impact Explanation
This is a custody/ownership-control break on object-held value (NFTs, token objects, or any object-based asset):
- A stale, unrelated former owner can reclaim (steal) an object away from `BURN_ADDRESS` after a completely different, legitimate current owner intentionally burned it, subverting both the current owner's intent and the resulting expected value destruction.
- It corrupts custody accounting by redirecting a burnt object's ownership to the wrong holder — the party recorded in the stale tombstone, not the party that actually performed the burn.
- Object-based assets (fungible-asset backed objects, token/NFT objects, DA/creator royalty-bearing objects, etc.) are all subject to `object::transfer`/`object::burn`/`object::unburn`, so this affects any live mainnet object.

### Likelihood Explanation
- No special privilege is required: `burn`, `transfer`/`transfer_raw`/`transfer_call`, and `unburn` are all `public entry` functions callable by any account that legitimately owns (or once owned) an object.
- The exploit only requires: (1) briefly owning/creating an object and calling `burn` on it, (2) transferring it away normally (sale, gift, marketplace listing, etc. — `burn()` never disables ungated transfer so this is always possible), and (3) waiting for any subsequent holder to send the object to `BURN_ADDRESS` via an ordinary transfer (a common, low-friction pattern many apps/users use to "burn" an object without knowing about the dedicated `TombStone`/`unburn` machinery).
- It requires no error in gas estimation, no race condition, and no admin/governance privilege — purely relies on state left behind by a public function that neighboring public functions fail to account for.

### Recommendation
Enforce tombstone consistency across every ownership-transfer path, not just `transfer_with_ref`:
- In `transfer_raw_inner` (or in each entry point that calls it), clear any existing `TombStone` on the object whenever ownership changes to any address other than `BURN_ADDRESS`, mirroring the logic already present in `transfer_with_ref`.
- Alternatively, prevent an object carrying a `TombStone` from being transferred via the ordinary paths at all (require going through `unburn` first), or disable ungated transfer as part of `burn()` so a soft-burnt object cannot silently change hands while its tombstone stays stale.
- Additionally, `unburn`'s `BURN_ADDRESS` branch should validate that the `TombStone.original_owner` corresponds to the address that most recently transferred the object *to* `BURN_ADDRESS`, not merely whichever address the object was tombstoned under arbitrarily far in the past.

### Proof of Concept
1. Alice creates/owns object `X`. Calls `object::burn(&alice, X)` → `TombStone{original_owner: Alice}` is stored; `X.owner` remains Alice; ungated transfer stays enabled (per `object.move:645-651`).
2. Alice calls `object::transfer(&alice, X, @bob)` (an ordinary entry transfer). `X.owner` becomes Bob; `TombStone{Alice}` persists untouched (per `object.move:558-594`, `582-594`).
3. Bob, unaware of the stale tombstone, later decides to burn `X` the common way many apps do — an ordinary transfer to `BURN_ADDRESS`: `object::transfer(&bob, X, BURN_ADDRESS)`. `X.owner` becomes `BURN_ADDRESS`; tombstone still says `Alice` (ordinary transfer never clears it).
4. Alice calls `object::unburn(&alice, X)`. Since `X.owner == BURN_ADDRESS`, the second branch runs, matches `TombStone.original_owner == Alice == signer`, and executes `transfer_raw_inner(X, Alice)` (per `object.move:653-676`), returning ownership of `X` to Alice — even though Bob was the legitimate owner who burned it, not Alice.

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
