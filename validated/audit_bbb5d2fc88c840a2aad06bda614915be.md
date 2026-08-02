### Title
Stale `TombStone.original_owner` survives ordinary object transfers, letting a past owner steal a currently-owned object (including `FungibleStore`/primary-store objects) sent to the burn address - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::burn` marks an object as "soft-burnt" by attaching a `TombStone{original_owner}` resource, without changing the object's owner or disabling `allow_ungated_transfer`. The object can subsequently be transferred normally (via `transfer`, `transfer_raw`, `transfer_call`, `transfer_to_object`) to new legitimate owners, but none of these paths clear the pre-existing `TombStone`. Only `transfer_with_ref` (the `TransferRef`/`LinearTransferRef` path) explicitly strips a stale `TombStone` before moving ownership. As a result, if any later, unrelated, legitimate owner sends the object to `BURN_ADDRESS` via an ordinary transfer (a common "burn my asset" idiom), `unburn` still honors the *original* pre-sale owner's claim and returns the object to them instead of leaving it burnt or letting the actual burner control disposition.

### Finding Description
`burn` only inserts a marker, it does not transfer ownership or gate transferability: [1](#0-0) 

The ungated transfer primitive used by `transfer`, `transfer_call`, `transfer_to_object`, and `transfer_raw` only updates `owner` and emits an event — it never inspects or clears `TombStone`: [2](#0-1) 

Compare this to the `TransferRef`-based path, which explicitly acknowledges the danger and clears any stale `TombStone` before transferring: [3](#0-2) 

`unburn` reclaims the object for `TombStone.original_owner` whenever the current owner equals `BURN_ADDRESS`, with no check on how many legitimate transfers happened in between the original burn and the object's later arrival at `BURN_ADDRESS`: [4](#0-3) 

Exploit chain:
1. Owner A calls `object::burn(A, obj)`. `TombStone{original_owner: A}` is attached; A is still the owner and `allow_ungated_transfer` is unchanged.
2. A sells/transfers `obj` to B using the ordinary `object::transfer` entry function (fully legitimate, ungated). `TombStone{original_owner: A}` is NOT cleared.
3. B, the legitimate new owner, later intentionally "burns"/discards the asset by sending it to `BURN_ADDRESS` via ordinary `object::transfer(B, obj, BURN_ADDRESS)` (B cannot call `object::burn` itself since `TombStone` already exists and that call would abort with `EOBJECT_ALREADY_BURNT`, so a naive "send to burn address" is the only path a dApp/user has).
4. A calls `object::unburn(A, obj)`. Since `owner == BURN_ADDRESS`, the second branch fires and transfers the object back to `original_owner_addr = A` — the stale, no-longer-entitled prior owner — bypassing B's intended and final disposition of the asset.

This same primitive is reused for value-bearing fungible-asset custody: `primary_fungible_store` auto-unburns a sender's store before transfers via `may_be_unburn`, showing `TombStone`/`unburn` are live custody mechanics for `FungibleStore` objects, not just decorative NFT metadata: [5](#0-4) 

### Impact Explanation
This breaks the custody invariant that only the current/entitled owner controls disposition of an object (and any FungibleStore/value it might carry). A stale, arbitrary past owner can reclaim an object away from its legitimate current owner's chosen destination (`BURN_ADDRESS`), effectively stealing the asset or the ability to permanently dispose of it. Because this is reachable purely through public entry functions (`burn`, `transfer`, `unburn`) with no privileged signer required at any step, and it corrupts the owner field of `ObjectCore` (moving custody to the wrong holder), it meets the high/critical custody-impact bar: unauthorized owner reassignment of object-held (and potentially fungible-store-held) value.

### Likelihood Explanation
All four steps use standard, publicly callable entry functions (`burn`, `transfer`, `unburn`) with no special permissions, and require no unusual preconditions besides `allow_ungated_transfer` being enabled, which is the default for objects (burn does not disable it). The pattern of "send an asset to the well-known 0xfff...f burn address to relinquish it" is a common convention users/dApps might implement without realizing `TombStone` semantics persist across ownership changes, making accidental or malicious triggering realistic.

### Recommendation
Clear any existing `TombStone` on the object whenever ownership legitimately changes via the ungated path, mirroring what `transfer_with_ref` already does — e.g., remove `TombStone` inside `transfer_raw_inner` (or reject the transfer if the object is soft-burnt and not being moved by the current owner reclaiming it), so that `original_owner`'s reclaim rights cannot outlive that specific burn/ownership epoch.

### Proof of Concept
Move pseudo-sequence exercising public entry points only:
```
// A owns obj, allow_ungated_transfer == true by default
object::burn(&A, obj);                       // TombStone{original_owner: A} attached, A still owner

object::transfer(&A, obj, addr_of(&B));      // ordinary ungated transfer; TombStone NOT cleared
// B is now the legitimate owner of obj

object::transfer(&B, obj, BURN_ADDRESS);     // B intentionally relinquishes/destroys the asset
// object_core.owner == BURN_ADDRESS, TombStone.original_owner still == A

object::unburn(&A, obj);                     // succeeds: owner == BURN_ADDRESS branch
// object_core.owner is now A again — A stole the object away from B's chosen disposition
```

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

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L282-286)
```text
    fun may_be_unburn(owner: &signer, store: Object<FungibleStore>) {
        if (store.is_burnt()) {
            object::unburn(owner, store);
        };
    }
```
