## Title
Stale `TombStone.original_owner` allows a former object owner to steal objects sent to the burn address by any later, unrelated owner - ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
`object::burn` attaches a `TombStone { original_owner }` marker to an object without ever disabling transfers or clearing that marker on subsequent ownership changes. Because ordinary `object::transfer`/`transfer_raw` never clears an existing `TombStone`, the `original_owner` recorded at the *first* soft-burn persists across any number of later, unrelated transfers. If any later, legitimate owner ever sends that same object to the well-known `BURN_ADDRESS` (a documented, intentional pattern in this codebase for permanently discarding objects), `object::unburn` lets the *original, now-unrelated* burner reclaim the object — not the owner who actually sent it there.

### Finding Description
`burn<T>` only asserts the caller is the *current* owner and then attaches a `TombStone` resource; it does not transfer the object anywhere nor disable `allow_ungated_transfer`: [1](#0-0) 

Because ungated transfer is still enabled, the object (still marked as "burnt" for indexers only) can be freely transferred via the normal, unprivileged entry points: [2](#0-1) 

`transfer_raw_inner`, used by both `transfer_raw`/`transfer`/`transfer_call`, never checks for or clears an existing `TombStone`. Only the privileged `transfer_with_ref` path (which requires a `LinearTransferRef` derived from a `TransferRef`, itself only obtainable from the original `ConstructorRef`) explicitly clears a stale `TombStone`: [3](#0-2) 

So an object that was soft-burned once, then sold/transferred through the ordinary `object::transfer` entry function any number of times, still silently carries the *original* burner's address in `TombStone.original_owner`.

`unburn` then reconciles this stale marker against the *current* owner: [4](#0-3) 

If the current owner ever moves the object to `BURN_ADDRESS` (the documented address "where unwanted objects can be forcefully transferred to"): [5](#0-4) 

then `object_core.owner == BURN_ADDRESS` is true, and `unburn` allows the address recorded in the *stale* `TombStone` (the very first burner, not the account that actually performed this burn) to reclaim full ownership via `transfer_raw_inner(object_addr, original_owner_addr)`.

**Broken custody invariant:** object ownership-reclaim rights (`TombStone.original_owner`) must reflect the party that authorized the *current* burn-to-`BURN_ADDRESS` action, but instead persist from an arbitrary, disconnected, prior soft-burn event, since intermediate ordinary transfers never clear it. This lets a stale, unprivileged former owner reassign ownership of an object that a completely different, legitimate current owner explicitly intended to destroy/relinquish.

### Impact Explanation
This is a direct custody/ownership-reassignment bug: an unprivileged party (the original soft-burner) can regain full ownership of a valuable object (token object, NFT, or any object carrying value/fungible stores) that a later, unrelated owner intentionally discarded by transferring it to `BURN_ADDRESS`. This meets the "Unauthorized takeover... ownership reassignment tied to live assets" and "Theft ... of token objects or other object-held value" custody criteria. Any object type built on `aptos_framework::object` (NFTs, token-objects, or fungible-asset-holding objects) is exposed to this if it ever goes through a burn→transfer→burn(to BURN_ADDRESS) lifecycle across different owners.

### Likelihood Explanation
Exploitation requires the attacker to have been a prior owner of the object who called `burn` at some point, then transferred the object away via a normal transfer, and later the victim (who is unaware of the dormant `TombStone`) sends the same object to the literal `BURN_ADDRESS` — a pattern explicitly documented/enabled by the framework itself as "the way to forcefully discard an object." This is a plausible marketplace/secondary-sale scenario (burn-for-effect, resell, later owner burns for real) rather than a purely theoretical one, though it does depend on victims using the burn-to-address pattern rather than `delete_ref`/other disposal mechanisms.

### Recommendation
Clear any existing `TombStone` whenever ownership changes through the ordinary transfer path (`transfer_raw_inner`), not only in `transfer_with_ref`. Alternatively, disallow soft-burnt objects (`exists<TombStone>`) from being transferred by ungated transfer at all until `unburn`ed by the current owner, and/or bind `TombStone.original_owner` semantics strictly to the *immediately preceding* owner rather than allowing it to persist indefinitely across ownership changes.

### Proof of Concept
1. Attacker owns object `O` (e.g., an NFT/token object). Attacker calls `object::burn(attacker, O)` → `TombStone { original_owner: attacker }` is attached; `O`'s owner field is unchanged (still attacker) and `allow_ungated_transfer` remains `true`.
2. Attacker sells/transfers `O` to Victim via `object::transfer(attacker, O, victim_addr)` (ordinary ungated transfer) — `TombStone` is **not** cleared by `transfer_raw_inner`.
3. Victim, unaware of the lingering `TombStone`, later decides to permanently discard `O` and calls `object::transfer(victim, O, BURN_ADDRESS)`.
4. Attacker calls `object::unburn<T>(attacker, O)`. Since `object_core.owner == BURN_ADDRESS` and `TombStone.original_owner == attacker`, the assert passes and `transfer_raw_inner(object_addr, attacker)` executes, returning ownership of `O` to the Attacker instead of leaving it burnt/inaccessible — effectively stealing the object Victim intended to destroy.

**Note:** I was unable to find an explicit unit test in the indexed portion of the repo that exercises this exact multi-owner burn→transfer→burn(BURN_ADDRESS) sequence, so I cannot fully confirm whether some other prologue/VM-level check outside `object.move` blocks this path; a Devin session with full repo/test access is recommended to validate this end-to-end (including checking `object.spec.move` formal specs and any framework-level tests for `burn`/`unburn`).

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L641-651)
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
