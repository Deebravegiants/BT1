## Finding: Stale `TombStone.original_owner` in `object::unburn` allows a prior owner to reclaim an object after it has been legitimately transferred and sent to `BURN_ADDRESS` by a later owner

### Title
Stale burn-marker allows unauthorized reclaim of transferred/burned Objects (and any fungible-asset store held as an Object) - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` ("soft burn") attaches a `TombStone{original_owner}` marker to an object **without changing its owner**, while `object::unburn` still supports the legacy "hard burn" path for any object whose current owner is `BURN_ADDRESS`, authorizing the reclaimer solely against the `TombStone.original_owner` field. Because `TombStone` is never invalidated or refreshed when the object is subsequently transferred to a new legitimate owner, a stale marker from an earlier, unrelated soft-burn lets that earlier owner steal the object back from `BURN_ADDRESS` even though a completely different, later owner is the one who actually sent it there.

### Finding Description
`burn()` only records provenance, it does not move the asset: [1](#0-0) 

`unburn()` trusts `TombStone.original_owner` whenever the object's current owner equals `BURN_ADDRESS`, regardless of who actually performed the transfer to `BURN_ADDRESS`: [2](#0-1) 

Ordinary `transfer`/`transfer_call`/`transfer_raw` place no restriction on the destination address — `BURN_ADDRESS` is just a normal address value, and transferring an object there requires only that the *current* owner sign and that `allow_ungated_transfer` is true: [3](#0-2) [4](#0-3) 

Exploit sequence:
1. Alice owns `Object<T>` (a generic object, e.g. a manually created `FungibleStore` via `fungible_asset::create_store`, or an NFT/token object — anything with default `allow_ungated_transfer = true`). Alice calls `burn(alice, object)`. This only adds `TombStone{original_owner: alice}`; `object_core.owner` stays `alice`.
2. Alice legitimately transfers the object to Bob using standard `object::transfer` (allowed — soft burn never disables ungated transfer). `object_core.owner` becomes `bob`. `TombStone.original_owner` is **not** updated/cleared.
3. Bob, the legitimate new owner, later decides to permanently destroy/burn his object by sending it straight to the well-known `BURN_ADDRESS` via ordinary `transfer_call(bob, object, BURN_ADDRESS)`. This succeeds since Bob is the current owner and ungated transfer is enabled — no special handling of `BURN_ADDRESS` is required. Now `object_core.owner == BURN_ADDRESS`.
4. Alice calls `unburn(alice, object)`. The branch `object_core.owner == BURN_ADDRESS` is taken; the assert `TombStone.original_owner == signer::address_of(alice)` passes because the marker is the stale one from step 1. `transfer_raw_inner(object_addr, alice)` executes, returning full ownership to Alice.

Result: Alice, who has no relationship to Bob's decision to send the object to `BURN_ADDRESS`, reclaims custody of an asset she no longer legitimately owns, at Bob's expense. The corrupted state is the `TombStone.original_owner` field: it is bound to whichever address happened to call `burn()` first, not to the address that actually performed the ownership-losing transfer to `BURN_ADDRESS`.

### Impact Explanation
This breaks the custody invariant that "object creation, transfer, burn, extensibility, and ownership refs must preserve the intended controller." Any transferable `Object<T>` that can hold value (a manually-created `fungible_asset::FungibleStore`, an NFT/token object, or any asset-bearing object) is susceptible: a previous owner can silently retain a permanent, dormant claim over the object via a stale `TombStone`, and later "un-burn" it away from whoever currently and legitimately sent it to the conventional burn address, seizing the underlying value (fungible asset balance, token, etc.). This is an unauthorized owner reassignment / theft of object-held value — a High/Critical custody-grade impact.

Note: Deterministic `primary_fungible_store` stores are **not** exploitable this way because `create_primary_store` explicitly calls `disable_ungated_transfer()` at creation, so primary stores can never be moved between owners or sent to `BURN_ADDRESS` via ordinary transfer: [5](#0-4) 
The exposure is limited to manually created (non-primary) `FungibleStore` objects, token objects, and any other user-created transferable `Object<T>`.

### Likelihood Explanation
The attack requires no privileged access and no bug in any other module — only two ordinary, publicly callable operations (`object::burn` and a normal `transfer`) performed at different points in the object's ownership history, followed by the victim (unknowingly) sending the object to `BURN_ADDRESS`. Since `BURN_ADDRESS` is a documented, commonly-used convention for "destroying" objects, and nothing in the transfer path warns or checks for a stale `TombStone`, this is a realistic sequence for any long-lived, transferable, asset-holding object.

### Recommendation
- Clear (`move_from`) any existing `TombStone` whenever the object's ownership changes via `transfer_raw_inner`/`transfer_with_ref`, so a `TombStone` can only ever reflect the *current* owner's own burn action.
- Alternatively, remove/deprecate the legacy `owner == BURN_ADDRESS` reclaim path in `unburn()` entirely, since regular `burn()` no longer transfers to `BURN_ADDRESS`; require that only the immediate, current owner (not a historical `TombStone.original_owner`) can reclaim an object sent to `BURN_ADDRESS`, or disallow reclaiming altogether for objects that were moved to `BURN_ADDRESS` via a normal transfer rather than through `burn()`/`burn_object_with_transfer` in the same transaction.

### Proof of Concept
```move
// Step 1: Alice soft-burns her object (does not change owner).
object::burn(&alice_signer, my_object);              // TombStone{original_owner: alice} attached; owner stays alice

// Step 2: Alice legitimately transfers the (still soft-burnt) object to Bob.
object::transfer(&alice_signer, my_object, bob_addr); // owner becomes bob; TombStone untouched

// Step 3: Bob, the legitimate owner, sends the object to the conventional burn address.
object::transfer_call(&bob_signer, object::object_address(my_object), BURN_ADDRESS); // owner becomes BURN_ADDRESS

// Step 4: Alice reclaims the object from BURN_ADDRESS using the stale TombStone.
object::unburn(&alice_signer, my_object);             // succeeds: owner reassigned back to alice, stealing custody from Bob
```

**Uncertainty note:** I did not find or verify a specific existing mainnet consumer module (beyond `primary_fungible_store`, which is unaffected) that creates transferable, value-bearing `Object<T>` instances via `fungible_asset::create_store` directly with default ungated-transfer enabled and exposes them to end users; confirming a concrete exploitable production instance (vs. a framework-level latent defect) would require checking downstream Move packages/dApps, which is outside the indexed `aptos-core` framework code reviewed here.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L97-98)
```text
    /// Address where unwanted objects can be forcefully transferred to.
    const BURN_ADDRESS: address = @0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L549-580)
```text
    /// Entry function that can be used to transfer, if allow_ungated_transfer is set true.
    public entry fun transfer_call(
        owner: &signer,
        object: address,
        to: address,
    ) {
        transfer_raw(owner, object, to)
    }

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

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L76-89)
```text
    public fun create_primary_store<T: key>(
        owner_addr: address,
        metadata: Object<T>,
    ): Object<FungibleStore> acquires DeriveRefPod {
        let metadata_addr = metadata.object_address();
        object::address_to_object<Metadata>(metadata_addr);
        let derive_ref = &borrow_global<DeriveRefPod>(metadata_addr).metadata_derive_ref;
        let constructor_ref = &object::create_user_derived_object(owner_addr, derive_ref);
        // Disable ungated transfer as deterministic stores shouldn't be transferrable.
        let transfer_ref = &constructor_ref.generate_transfer_ref();
        transfer_ref.disable_ungated_transfer();

        fungible_asset::create_store(constructor_ref, metadata)
    }
```
