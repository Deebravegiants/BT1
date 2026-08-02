### Title
Stale `TombStone.original_owner` lets a former owner reclaim an object a *later* legitimate owner sent to `BURN_ADDRESS` - ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
`object::burn` (soft burn) attaches a `TombStone{original_owner}` to an object **without changing its owner**. If the object is subsequently transferred through the *ordinary* ungated-transfer path (`transfer`/`transfer_raw`/`transfer_call`) — which never inspects or clears `TombStone` — the tombstone becomes stale. When a later, legitimate owner eventually moves the object to `BURN_ADDRESS` via the same ordinary transfer path, `unburn` will restore ownership to the *original* (stale) `original_owner` rather than to the owner who actually sent it to `BURN_ADDRESS`, letting a past owner seize an object away from its rightful current lineage.

### Finding Description
`ObjectCore.owner` and the `TombStone` resource are meant to move in lock-step for the "burn/unburn" custody model. Two disjoint code paths interact with `TombStone`:

- `object::burn` (soft burn) only asserts current ownership and moves a `TombStone{ original_owner }` into the object, but does **not** transfer ownership and does **not** disable ungated transfer: [1](#0-0) 

- `object::transfer` / `transfer_raw` / `transfer_call` (the ordinary owner-signed transfer path) mutate `ObjectCore.owner` directly and never look at `TombStone` at all: [2](#0-1) 

- Only the *other* transfer path, `transfer_with_ref` (which requires a `LinearTransferRef`, generated from a `TransferRef`), explicitly clears a stale `TombStone` before changing owner: [3](#0-2) 

- `unburn` trusts `TombStone.original_owner` whenever the current owner is `BURN_ADDRESS`, and hands ownership straight back to that recorded address: [4](#0-3) 

Because ordinary ungated transfer (the common, capability-free transfer path most objects/NFTs use) is completely blind to `TombStone`, the following sequence produces a corrupted custody record:

1. Alice owns object `O`. Alice calls `object::burn(alice, O)`. This creates `TombStone{original_owner: alice}`; `O.owner` remains `alice` (ungated transfer is still enabled — `burn` never calls `disable_ungated_transfer`).
2. Alice legitimately transfers `O` to Bob via the ordinary path: `object::transfer(alice, O, bob)`. `O.owner` becomes `bob`. `TombStone{original_owner: alice}` is **untouched** — it is still present and still says `alice`.
3. Bob, the new rightful owner, later decides to discard/burn `O` and sends it to the well-known `BURN_ADDRESS` using the same ordinary transfer function: `object::transfer(bob, O, BURN_ADDRESS)`. `O.owner` becomes `BURN_ADDRESS`. `TombStone` is still `{original_owner: alice}` — stale, because only `transfer_with_ref` clears it, and that path was never used.
4. Alice — who sold `O` away in step 2 and has no current claim on it — calls `object::unburn(alice, O)`. `unburn` sees `object_core.owner == BURN_ADDRESS`, extracts the tombstone, checks `original_owner_addr (alice) == signer::address_of(alice)` (trivially true), and calls `transfer_raw_inner(object_addr, alice)`.

Result: ownership of `O` reverts to Alice, not to Bob (the actual owner who sent it to `BURN_ADDRESS`), and not to a "cannot be reclaimed" state that Bob intended by burning it. Alice has recovered custody of an object she previously and legitimately relinquished.

The root cause is a broken invariant: `TombStone.original_owner` is only guaranteed accurate immediately after `burn()` is called; it is never re-validated or updated across subsequent ordinary ownership transfers, yet `unburn()` treats it as an unconditionally trustworthy record of "who is entitled to reclaim this object."

### Impact Explanation
This breaks the fundamental custody invariant that object ownership control (and any value/rights tied to that object, e.g., digital-asset/token-object NFTs, or any resource whose access is gated by `object::owner`/`object::owns`) must track the true chain of legitimate owners. A previous owner can use a stale soft-burn record to reclaim an object out of `BURN_ADDRESS` that a *later* legitimate owner deliberately discarded, effectively expropriating ownership/value from the rightful current owner's lineage without their consent. This is a custody/ownership-reassignment bug with mainnet-relevant impact on any object (including Digital Asset / Token Objects) that passes through this soft-burn → transfer → real-burn sequence.

### Likelihood Explanation
Likelihood is high: `object::burn`/`unburn` are public entry functions usable by any address with no privileged setup, `allow_ungated_transfer` is enabled by default and is not disabled by `burn()`, and the sequence (burn → normal transfer → normal transfer to `BURN_ADDRESS` → unburn) uses only standard, commonly used object APIs (`object::burn`, `object::transfer`, `object::unburn`). No special permissions, races, or edge-case gas/rounding conditions are required — only that the object pass through a soft "burn" once before later being genuinely discarded to `BURN_ADDRESS` by a different owner.

### Recommendation
Enforce that `TombStone.original_owner` can only ever be treated as valid if it matches the *most recent* owner at each subsequent transfer, or simply clear/invalidate `TombStone` on every ordinary ownership transfer (`transfer_raw_inner`), just as `transfer_with_ref` already does. Alternatively, disallow soft `burn()` from coexisting with further ungated transfers (e.g., call `disable_ungated_transfer` inside `burn()`), or record/refresh `original_owner` to the current owner whenever a transfer occurs while a `TombStone` is present.

### Proof of Concept
```
// Alice owns O
object::burn(alice, O);                       // TombStone{original_owner: alice}, O.owner = alice
object::transfer(alice, O, bob_addr);         // O.owner = bob; TombStone untouched (still alice)
object::transfer(bob, O, BURN_ADDRESS);       // O.owner = BURN_ADDRESS; TombStone still {alice}
object::unburn(alice, O);                     // passes: TombStone.original_owner == alice
                                               // => O.owner reverts to alice, not bob
```
Note: I could not execute this in a live Move test environment as part of this analysis; the trace above is derived directly from reading the cited source and confirming (via the full grep of `TombStone`/burn/unburn/transfer occurrences in `object.move`) that no other code path clears or revalidates the tombstone record on ordinary transfers.

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
