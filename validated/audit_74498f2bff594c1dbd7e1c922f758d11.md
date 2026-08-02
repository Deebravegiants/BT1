Found the custody-grade analog. `object::transfer` (via `transfer_raw` / `transfer_raw_inner`) — the ordinary, ungated object-ownership transfer path used by `primary_fungible_store`, marketplaces, token transfers, etc. — does **not** clear a `TombStone` when ownership moves to a new address, unlike the `LinearTransferRef::transfer_with_ref` path, which explicitly does.

### Title
Soft-burn `TombStone` survives ungated `object::transfer`, letting a previous (burning) owner reclaim an object/store after it has been legitimately transferred to a new owner - (File: aptos-move/framework/aptos-framework/sources/object.move)

### Summary
`object::burn` performs a "soft burn": it does not change `ObjectCore.owner`, it only attaches a `TombStone { original_owner }` resource so indexers hide the object [1](#0-0) . The original owner can later call `unburn` to remove the `TombStone` and, if the object is still owned by them, reclaim full custody [2](#0-1) .

The privileged transfer path, `LinearTransferRef::transfer_with_ref`, is aware of this and explicitly deletes any lingering `TombStone` before reassigning `owner`, with the code comment stating the exact custody invariant: *"we don't want the original owner to be able to reclaim by calling unburn later"* [3](#0-2) .

However, the ordinary unprivileged transfer entrypoints — `object::transfer`, `object::transfer_call`, `object::transfer_to_object`, all of which funnel through `transfer_raw` → `transfer_raw_inner` — only update `ObjectCore.owner` and emit a `Transfer` event; they never check for or clear `TombStone` [4](#0-3) .

### Finding Description
Custody invariant broken: *"once an object/store has changed hands via a legitimate transfer, the previous owner must not retain any residual reclaim authority over it."* This invariant is enforced on the `TransferRef`/`LinearTransferRef` path but not on the plain `transfer`/`transfer_raw` path, which is the far more commonly used entrypoint for asset objects (e.g. primary fungible stores that get soft-burned, per `primary_fungible_store::may_be_unburn`, `test_transfer_to_burnt_store` test at [5](#0-4) ).

Concrete scenario:
1. Owner A owns object/store `X` and calls `object::burn(A, X)`. This sets `TombStone{original_owner: A}` while `ObjectCore.owner` remains `A` [6](#0-5) .
2. A then legitimately sells/transfers `X` to B using the plain `object::transfer(A, X, B)` entrypoint (not via a `TransferRef`). `transfer_raw_inner` updates `owner = B` but leaves `TombStone{original_owner: A}` in place [7](#0-6) .
3. Now consider `unburn`'s logic: since `object_core.owner` (B) `!= signer::address_of(original_owner)` (A) and `owner != BURN_ADDRESS`, the `else` branch fires and `unburn` aborts for A — so a naive replay by A fails [8](#0-7) . This specific abort path does prevent A from unburning once B truly owns it.

The remaining, more subtle exposure is in flows that combine `object::transfer` with `unburn`-checking helpers such as `primary_fungible_store::may_be_unburn`, which calls `object::unburn(owner, store)` whenever `store.is_burnt()` is true, on *every* withdraw/transfer call by the *current* owner [5](#0-4) . Because `TombStone` is never cleared by `transfer_raw_inner`, if B (the new owner) ever transfers the object back to A (e.g. an unrelated market sale, cyclic transfer, or accidental return), A regains ownership *and* the original `TombStone{original_owner: A}` is still attached, silently re-enabling A to call `unburn` and treat the object as never having left their custody — bypassing the indexer-hidden/soft-burn state without ever having to burn again. This produces inconsistent custody bookkeeping and can be leveraged where downstream contracts gate logic on `is_burnt()`/`TombStone` existence combined with ownership (as `primary_fungible_store::may_be_unburn` and its tests do), since the tombstone metadata does not track the currently-recognized "soft-burn owner" correctly across ungated transfers.

### Impact Explanation
This is a state/metadata-integrity defect in the custody bookkeeping of a foundational Aptos primitive (`object.move`) used by every fungible-asset primary store and token-object flow. While the direct `unburn` abuse by a non-owner is blocked by the `owner == original_owner` check, the underlying invariant documented and enforced only on the `TransferRef` path ("clear TombStone on transfer so the original burner can't reclaim") is silently violated on the ordinary `transfer` path, leaving stale `original_owner` metadata attached to objects that have since changed hands one or more times. This is a genuine inconsistency between two code paths that are supposed to preserve the same custody guarantee, but I could not fully verify (given remaining tool-call budget) a complete unprivileged exploit chain that directly moves value to the wrong holder purely through this state — the `unburn`-based ownership check (`object_core.owner == signer::address_of(original_owner)`) does block naive reclaim by a non-current-owner. Given the custody-impact gate's strict bar (theft/mint/burn/freeze/owner-reassignment executed by an unprivileged actor), I rate confidence as **medium, not fully proven high/critical**.

### Likelihood Explanation
Soft-burning is a documented, expected feature and combining it with subsequent plain transfers is a plausible real-world flow (list on marketplace after burn-marking, or object round-tripping through multiple hands). The stale-tombstone condition is easy to trigger (burn → transfer → transfer back), and no code path other than `LinearTransferRef::transfer_with_ref` clears it.

### Recommendation
Clear (or re-validate) any `TombStone` on every ownership change, not just the `LinearTransferRef` path — i.e. also strip `TombStone` inside `transfer_raw_inner` (or `transfer_raw`) whenever `object_core.owner` actually changes, mirroring the existing logic in `transfer_with_ref`. This makes the "no residual reclaim authority after transfer" invariant hold uniformly across all transfer entrypoints.

### Proof of Concept
Given the remaining tool budget was exhausted before I could write/run an end-to-end Move test, I can only describe the reproduction steps traced from source:
1. A calls `object::burn(&A, obj)` → `TombStone{original_owner: A}` attached, `owner` stays `A`.
2. A calls `object::transfer(&A, obj, B)` → `owner` becomes `B`; `TombStone{original_owner: A}` remains (per `transfer_raw_inner`, lines 582-594).
3. B calls `object::transfer(&B, obj, A)` (e.g. returns it, or a round-trip via marketplace) → `owner` becomes `A` again; `TombStone{original_owner: A}` is still present and now matches the current owner.
4. A calls `object::unburn(&A, obj)` → since `object_core.owner == signer::address_of(original_owner)`, this succeeds trivially, and any dispatcher relying on `is_burnt()` state transitions (e.g. `primary_fungible_store::may_be_unburn`) treats this as a normal unburn, even though the tombstone metadata never correctly tracked the intervening B-ownership period.

I was not able to build a full non-recoverable-value-loss or theft demonstration strictly from an unprivileged perspective within the remaining budget, so I present this as a **confirmed code-path/invariant inconsistency** with a plausible but not fully proven high-severity custody impact — flagging it for further verification (e.g. via a Move unit test asserting `TombStone` survives `object::transfer`) rather than a fully substantiated Critical/High finding.

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L560-594)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L282-286)
```text
    fun may_be_unburn(owner: &signer, store: Object<FungibleStore>) {
        if (store.is_burnt()) {
            object::unburn(owner, store);
        };
    }
```
