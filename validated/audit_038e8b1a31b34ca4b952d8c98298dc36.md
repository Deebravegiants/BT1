### Title
Stale `TombStone.original_owner` lets a divested prior owner reclaim an Object sent to `BURN_ADDRESS` after legitimate ownership transfers — `object.move`

### Summary
`aptos_framework::object` supports a "soft burn" (`burn`) that tags an object with a `TombStone{original_owner}` without changing its owner, and an `unburn` that lets the address recorded in `TombStone.original_owner` reclaim the object once its current owner is the reserved `BURN_ADDRESS`. Every ordinary transfer path (`transfer`, `transfer_raw`, `transfer_to_object`) leaves an existing `TombStone` untouched — only the ref-based `transfer_with_ref` clears it. Because `to` in `transfer_raw` is an unchecked plain address, any current owner can legitimately send an object to `BURN_ADDRESS` via a normal transfer. If the object carries a stale `TombStone` from a *previous* owner (created before the object was sold/transferred away), that previous, now-unrelated owner can call `unburn` and reclaim full ownership, hijacking the object from whatever custody chain led it to `BURN_ADDRESS`.

### Finding Description
- `burn` creates a `TombStone{original_owner}` while leaving the object's owner unchanged: [1](#0-0) 

- `unburn` reclaims ownership to `TombStone.original_owner` whenever the object's *current* owner is `BURN_ADDRESS`, regardless of how many legitimate transfers happened in between: [2](#0-1) 

- Only `transfer_with_ref` (the `LinearTransferRef`-gated path) explicitly clears a pre-existing `TombStone` before allowing a transfer, "so we don't want the original owner to be able to reclaim by calling unburn later": [3](#0-2) 

- The ordinary transfer paths (`transfer`, `transfer_raw`, `transfer_to_object`) do **not** perform this cleanup. `transfer_raw` only validates that the caller owns the object being moved (via `verify_ungated_and_descendant`); the destination `to` is an arbitrary, unchecked address — it does not need to be, or become, an object: [4](#0-3) 

- The framework itself demonstrates that "owner == `BURN_ADDRESS`" + "TombStone present" is a legitimate, supported on-chain state (the previous `burn` implementation, preserved as `burn_object_with_transfer`, directly transfers to `BURN_ADDRESS`), and the corresponding test confirms `unburn` successfully restores ownership from `BURN_ADDRESS` to `TombStone.original_owner`: [5](#0-4) [6](#0-5) 

Root cause: a `TombStone` written by owner A is never invalidated when the object subsequently changes hands through the standard transfer entry points, so `TombStone.original_owner` can be stale relative to the object's real transfer/ownership history. `unburn`'s only real check for this branch is `original_owner_addr == signer::address_of(original_owner)`, which trivially passes for the party recorded in the stale `TombStone` — not for whoever actually held the object immediately before it reached `BURN_ADDRESS`.

### Impact Explanation
This breaks the object custody invariant that "object creation, transfer, burn, and ownership refs must preserve the intended controller." A party (A) who has already sold/transferred an object away can:
1. Soft-burn it while still the owner (`burn`), leaving a dangling `TombStone{A}`.
2. Transfer the object normally to a buyer/recipient B (TombStone persists, unnoticed by B, since it's not surfaced/cleared).
3. At any later point, when the object (now owned by B or any subsequent holder) is ever sent to `BURN_ADDRESS` — a normal, unrestricted transfer destination, and the framework's documented "address where unwanted objects can be forcefully transferred to" — A can call `unburn` and reclaim full ownership of the object, regardless of how many legitimate transfers occurred and regardless of A having no residual claim.

This is an unauthorized owner reassignment of a live, potentially valuable object (token, NFT, or any object holding fungible-asset stores/capabilities), effectively letting a previous owner "steal back" an asset that changed hands, and undermines the expectation that `BURN_ADDRESS` represents a terminal/irrecoverable custody state for whoever actually sent it there.

### Likelihood Explanation
- `burn`/`unburn`/`transfer`/`transfer_raw` are all public entry functions usable by anyone on any object they currently own; no special privilege is required to set the trap or to trigger it.
- An attacker can deliberately plant the landmine: acquire/mint an object, self-burn it, then sell/transfer it — the buyer has no on-chain signal distinguishing this object from a clean one (TombStone is not cleared or reported by the ordinary transfer flow).
- The trigger condition (object eventually transferred to `BURN_ADDRESS`) is plausible: `BURN_ADDRESS` is a documented, well-known constant, and application/wallet-level "burn" flows may implement burning as a direct transfer to this address rather than via the framework's own `burn`/`unburn` soft-burn API (which itself would be blocked by the pre-existing `TombStone`, per `EOBJECT_ALREADY_BURNT`).

### Recommendation
- Clear any existing `TombStone` on the object whenever ownership changes through the standard transfer paths (`transfer_raw_inner`/`transfer`/`transfer_raw`/`transfer_to_object`), mirroring the cleanup already done in `transfer_with_ref`.
- Alternatively/additionally, bind `unburn`'s `BURN_ADDRESS` branch to the owner recorded immediately prior to the transfer into `BURN_ADDRESS` (e.g., snapshot/refresh `TombStone.original_owner` at the moment of transfer to `BURN_ADDRESS`) rather than trusting an unbounded-age `TombStone` created under a possibly long-superseded owner.
- Consider disallowing arbitrary (non-`burn`/`unburn`-mediated) transfers directly to `BURN_ADDRESS`, or invalidate any stale `TombStone` at the point an object arrives at `BURN_ADDRESS` via `transfer_raw_inner` if the current owner differs from `TombStone.original_owner`.

### Proof of Concept
```move
// A owns object O
object::burn(&A_signer, O);                    // TombStone{original_owner: A} created; O.owner still A
object::transfer(&A_signer, O, B_addr);         // legitimate sale/gift; O.owner = B; TombStone{A} NOT cleared

// ... time passes, B is the sole legitimate owner ...

object::transfer(&B_signer, O, BURN_ADDRESS);   // B intentionally discards O; O.owner = BURN_ADDRESS
                                                 // TombStone{A} still present, untouched by this transfer

// A, who has no remaining claim on O, reclaims it:
object::unburn(&A_signer, O);
// TombStone.original_owner (A) == signer::address_of(A) -> check passes
// transfer_raw_inner(O, A) executes -> O.owner = A
// A has stolen back an object it had already legitimately sold to B.
``` [2](#0-1)

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L776-787)
```text
    /// For testing the previous behavior of `object::burn()`
    ///
    /// Forcefully transfer an unwanted object to BURN_ADDRESS, ignoring whether ungated_transfer is allowed.
    /// This only works for objects directly owned and for simplicity does not apply to indirectly owned objects.
    /// Original owners can reclaim burnt objects any time in the future by calling unburn.
    public fun burn_object_with_transfer<T: key>(owner: &signer, object: Object<T>) {
        let original_owner = signer::address_of(owner);
        assert!(is_owner(object, original_owner), error::permission_denied(ENOT_OBJECT_OWNER));
        let object_addr = object.inner;
        move_to(&create_signer(object_addr), TombStone { original_owner });
        transfer_raw_inner(object_addr, BURN_ADDRESS);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L976-993)
```text
    #[test(creator = @0x123)]
    fun test_burn_and_unburn_old(creator: &signer) {
        let (hero_constructor, hero) = create_hero(creator);
        // Freeze the object.
        let transfer_ref = hero_constructor.generate_transfer_ref();
        transfer_ref.disable_ungated_transfer();

        // Owner should be able to burn, despite ungated transfer disallowed.
        burn_object_with_transfer(creator, hero);
        assert!(hero.owner() == BURN_ADDRESS, 0);
        assert!(!hero.ungated_transfer_allowed(), 0);

        // Owner should be able to reclaim.
        unburn(creator, hero);
        assert!(hero.owner() == signer::address_of(creator), 0);
        // Object still frozen.
        assert!(!hero.ungated_transfer_allowed(), 0);
    }
```
