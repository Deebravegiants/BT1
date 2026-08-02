## Finding: Stale TombStone survives ordinary object transfer, letting a former owner reclaim an object a legitimate owner sent to the burn address

- File: `aptos-move/framework/aptos-framework/sources/object.move`

### Summary
`object::burn` attaches a `TombStone{original_owner}` to an object without disabling further transfers. Every ordinary transfer path (`transfer`, `transfer_call`, `transfer_to_object`, `transfer_raw` → `transfer_raw_inner`) changes `ObjectCore.owner` but never inspects or clears an existing `TombStone`. Only the ref-based `transfer_with_ref` (via `LinearTransferRef`) explicitly strips a stale `TombStone` — proving the maintainers recognized this exact reclaim-hijack risk but patched only one of the two transfer paths. This inconsistency lets a *former* owner reclaim an object that a *later, legitimate* owner intentionally sent to the well-known `BURN_ADDRESS`.

### Finding Description
`burn<T>` only checks that the caller currently owns the object and that no `TombStone` already exists; it does not touch `allow_ungated_transfer`: [1](#0-0) 

Because ungated transfer is untouched, the object can still be freely transferred afterward through the plain owner-signed path: [2](#0-1) 

`transfer_raw_inner` only updates `owner` and emits an event — it never checks `exists<TombStone>` and never removes it. Compare this with the ref-based path, which explicitly clears a stale `TombStone` before transferring, with a comment stating the exact rationale: [3](#0-2) 

Finally, `unburn` still keys its "old functionality" reclaim branch off the address currently equal to `BURN_ADDRESS`, together with the (potentially stale) `original_owner` recorded in the `TombStone`: [4](#0-3) 

**Exploit chain:**
1. Alice owns object `X` (an object that can itself carry a primary fungible store, a token, or any other custody-grade value).
2. Alice calls `object::burn(alice, X)`. This attaches `TombStone{original_owner: alice}` but leaves `allow_ungated_transfer` and `owner` unchanged.
3. Alice sells/transfers `X` to Bob via ordinary `object::transfer` (a fully legitimate, indistinguishable-from-normal action — `owner()`/`is_owner()` correctly report Bob as owner; the `TombStone` is invisible except via `exists<TombStone>`, which the module doc says is only used to "hide via indexers"). The stale `TombStone{original_owner: alice}` is never cleared because `transfer_raw_inner` doesn't check for it.
4. Bob, now the legitimate owner, later decides to permanently destroy the object by sending it to the reserved `BURN_ADDRESS` using the standard `object::transfer(bob, X, BURN_ADDRESS)` entry function — this is exactly the "old burn functionality" pattern the module still supports via `unburn`'s second branch.
5. Alice calls `object::unburn(alice, X)`. Since `object_core.owner == BURN_ADDRESS` and the stored `TombStone.original_owner == alice` matches the caller, the second branch fires and `transfer_raw_inner(X, alice)` reassigns ownership of `X` back to Alice — even though Alice's ownership legitimately ended at step 3.

### Impact Explanation
This breaks the object-ownership custody invariant: ownership/reclaim rights end up tracking a stale attribute (`TombStone.original_owner`) rather than the actual chain of legitimate transfers. A party with **no current or recent authority** over an asset (Alice, who sold it away) can reassign ownership of an object — and any fungible-asset store, token, or code-object value nested under it — away from the address the true, current owner (Bob) explicitly and validly chose (the burn address), back to themselves. This is unauthorized owner reassignment / theft of object-held value, meeting the "Unauthorized takeover... owner reassignment" and "Permanent lock or non-recoverable loss...value" custody-impact criteria (from the current owner's perspective, their intended irrecoverable burn is reversed and stolen by a third party).

### Likelihood Explanation
The precondition sequence (burn → sell/transfer → recipient later burns via ordinary transfer to `BURN_ADDRESS`) requires no privileged access and uses only public, unprivileged entry functions (`burn`, `transfer`/`transfer_call`, `unburn`). Sending a token to a burn address is a common, expected user action across chains, and nothing in the object model warns the recipient (Bob) that a hidden `TombStone` exists — the module's own doc states TombStones are meant to be hidden from indexers. The bug is latent until a victim independently chooses to "burn" a purchased object, but this is a realistic and encouraged usage pattern, and the attacker (Alice) needs no cooperation from Bob beyond the ordinary sale.

### Recommendation
Apply the same protection already implemented for `LinearTransferRef::transfer_with_ref` to the address-based transfer path. In `transfer_raw_inner` (or `transfer_raw` before calling it), check `exists<TombStone>(object)` and remove it whenever ownership changes to an address other than `BURN_ADDRESS`, mirroring the "undo soft burn" logic already present in `transfer_with_ref`. Alternatively, clear the `TombStone` any time ownership changes at all (including transfers *to* `BURN_ADDRESS` performed by an owner other than the original burner), so that `unburn`'s legacy branch can only ever reclaim on behalf of the party who most recently performed the actual burn.

### Proof of Concept
```move
// Alice owns hero object X
object::burn(&alice, hero);                      // TombStone{original_owner: alice}, still owned by alice, still transferable
object::transfer(&alice, hero, bob_addr);         // legitimate sale; hero.owner() == bob, TombStone untouched
// ... time passes, Bob is unaware of hidden TombStone ...
object::transfer(&bob, hero, BURN_ADDRESS);       // Bob intentionally "burns" his own object
object::unburn(&alice, hero);                     // succeeds: owner==BURN_ADDRESS && TombStone.original_owner==alice
// hero.owner() == alice again -- Alice reclaimed an object she had already sold to Bob and that Bob explicitly destroyed.
```

Note: I was unable to independently verify at what point (if any) `burn_object_with_transfer` (referenced in `burn`'s doc comment as "test only") is guarded on mainnet code paths beyond the doc-comment reference; this doesn't affect the PoC above, which relies solely on generally-available `transfer`/`burn`/`unburn` entry functions.

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
