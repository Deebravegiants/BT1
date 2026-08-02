# Title
Stale `TombStone` Enables Original Owner to Reclaim/Hijack Objects Sent to `BURN_ADDRESS` After Legitimate Resale — ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
`object::burn()` marks an object with a `TombStone` but leaves the `owner` field and `allow_ungated_transfer` untouched, so the object continues to be freely, ungated-transferable through the normal `transfer`/`transfer_raw`/`transfer_call` entrypoints. Those ordinary transfer paths never clear the `TombStone`, unlike `transfer_with_ref`, which explicitly removes it to prevent exactly this class of reclaim. Because the well-known `BURN_ADDRESS` constant is a plain, unrestricted transfer destination, any account that once burned an object can later reclaim it from a completely unrelated future owner who innocently sends that object to `BURN_ADDRESS`.

### Finding Description
`burn()` only attaches a `TombStone{original_owner}` without changing ownership or disabling transfers: [1](#0-0) 

The normal transfer path (`transfer`, `transfer_call`, `transfer_to_object` → `transfer_raw` → `transfer_raw_inner`) only updates the `owner` field and emits an event — it never inspects or removes any existing `TombStone`: [2](#0-1) 

By contrast, the ref-based transfer path explicitly acknowledges and neutralizes this exact risk by clearing any leftover `TombStone` before changing ownership: [3](#0-2) 

`unburn()` allows the caller to reclaim the object whenever the *current* owner is `BURN_ADDRESS` and the stored `TombStone.original_owner` matches the caller — with no requirement that the caller was the party who most recently sent the object to `BURN_ADDRESS`: [4](#0-3) 

`BURN_ADDRESS` is just a fixed, publicly documented address with no special transfer protection: [5](#0-4) 

Combining these facts: once an object has ever been burned by attacker `A` (via the non-deprecated `burn()`), a `TombStone{original_owner: A}` persists on that object forever unless the object is moved via `transfer_with_ref`. If `A` subsequently sells/transfers the object through ordinary `object::transfer` to victim `V` (a completely normal marketplace flow), the `TombStone` silently survives the sale. If `V` (or any later legitimate owner) ever sends that object to `BURN_ADDRESS` through ordinary transfer — a natural action since `BURN_ADDRESS` is documented as "the address where unwanted objects can be forcefully transferred to" — attacker `A` can call `unburn` and have `transfer_raw_inner` reassign ownership of the object back to themselves, without any authorization from `V`.

### Impact Explanation
This breaks the fundamental object custody invariant that "object transfer, burn, and ownership refs must preserve the intended controller." A past owner can plant a dormant claim on any object they ever burned, sell it away normally, and later hijack it (and anything of value stored under that object address, e.g. fungible asset stores, NFTs, or other resources) from whichever legitimate future owner sends it to the canonical burn address — an unauthorized owner reassignment / theft of object-held value. This qualifies as High severity under the custody impact gate ("unauthorized takeover ... owner reassignment of ... token objects").

### Likelihood Explanation
Likelihood is realistic though it requires a specific sequence: (1) attacker burns an object they own, (2) legitimately transfers it away via a normal (non-`TransferRef`) path — the common case for most wallets/marketplaces using `object::transfer`, and (3) a later owner independently transfers the object to `BURN_ADDRESS` using the same ordinary transfer functions, which is a plausible, unrestricted, and even encouraged action (per the address's documented purpose). No privileged access or governance is required — only ordinary signer calls to public entry functions.

### Recommendation
Clear any stale `TombStone` on every ownership change, not just the `TransferRef` path. Move the tombstone-clearing logic from `transfer_with_ref` into `transfer_raw_inner` (or `transfer_raw`) so that any pre-existing `TombStone` at `object` is destroyed whenever `owner` is updated, regardless of which transfer entrypoint is used. Alternatively, disable `allow_ungated_transfer` when `burn()` is called and require `unburn()` before any subsequent transfer, or bind the `unburn`'s `BURN_ADDRESS` branch to the address that most recently executed the transfer to `BURN_ADDRESS` rather than to a persisted historical value.

### Proof of Concept
```
// Step 1: Attacker A owns Object O
object::burn(A, O);
// -> TombStone{original_owner: A} created; O.owner still == A; O.allow_ungated_transfer still true

// Step 2: A sells O normally to V (e.g., marketplace flow uses plain transfer, not TransferRef)
object::transfer(A, O, V);
// -> O.owner = V; TombStone{original_owner: A} still exists at O's address (transfer_raw_inner never clears it)

// Step 3: V (unaware of stale tombstone) later sends O to the documented burn address
object::transfer_call(V, object_address_of(O), BURN_ADDRESS);
// -> O.owner = BURN_ADDRESS

// Step 4: A reclaims O that V just tried to burn
object::unburn(A, O);
// unburn(): object_core.owner == BURN_ADDRESS -> true
//           TombStone.original_owner (A) == signer::address_of(A) -> true
//           transfer_raw_inner(object_addr, A) -> O.owner reassigned back to A
// Result: A now owns O again, stealing it from V's burn intent / any subsequent legitimate custody chain.
```

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
