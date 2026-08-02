This confirms `burn_object_with_transfer` (which performs the actual transfer to `BURN_ADDRESS` together with the `TombStone`) is `#[test_only]` — it does not exist as a production entry point. In production, the current `burn()` never moves ownership to `BURN_ADDRESS` at all; it only tags a `TombStone` while leaving the owner unchanged. Meanwhile, nothing in `object::transfer`, `transfer_raw`, or `transfer_call` prevents an owner from directly sending an object to the literal `BURN_ADDRESS` constant through the normal (production) transfer path without ever creating a `TombStone`. Since `unburn()` requires `exists<TombStone>(object_addr)` to do anything, an object moved to `BURN_ADDRESS` via ordinary `transfer`/`transfer_raw`/`transfer_call` becomes permanently stuck — `BURN_ADDRESS` (`0xff...ff`) has no discoverable private key, so no signer can ever be produced for it, and the framework's own designed recovery mechanism (`unburn`) refuses to act because the tombstone marker it depends on was never written.

### Title
Objects transferred to the reserved `BURN_ADDRESS` via ordinary `object::transfer`/`transfer_raw` bypass `TombStone` recovery tracking and become permanently unrecoverable - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::BURN_ADDRESS` is a reserved constant (`0xff...ff`) intended as the target for "burning" objects, with `unburn()` provided as the recovery mechanism for objects sent there. However, the only production function that adds recovery bookkeeping (`burn()`) does not transfer ownership to `BURN_ADDRESS` at all — it just tags a `TombStone` in place. The function that actually transfers ownership to `BURN_ADDRESS` together with a `TombStone` (`burn_object_with_transfer`) is `#[test_only]` and not callable in production. Meanwhile, the generic, always-available transfer entry points (`transfer`, `transfer_raw`, `transfer_call`) allow anyone to send an object to `BURN_ADDRESS` as a plain address with no special handling. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
This is the direct Aptos analog of the `ImmutableBundle` bug: a custody/recovery mechanism (`rescueERC721` in the report, `unburn()` here) is designed to reverse an unwanted-but-plausible transfer, but the recovery mechanism only works if the asset was moved through the "correct" code path that records the necessary bookkeeping (`immutableOfBundle` in the report, `TombStone` here). Any transfer that reaches the same destination through a different, equally legitimate function bypasses that bookkeeping and permanently defeats recovery.

Concretely:
- `object::transfer<T>`, `object::transfer_raw`, and `object::transfer_call` are unrestricted, generic, publicly callable entry points that let an owner move an object to *any* address, including the literal `BURN_ADDRESS` constant, as long as `allow_ungated_transfer` is set (true by default) [4](#0-3) .
- `verify_ungated_and_descendant` performs no destination-address checks (e.g., rejecting `BURN_ADDRESS`) — it only validates ownership chain and the `allow_ungated_transfer` flag [5](#0-4) .
- The production `burn()` function does not perform any transfer to `BURN_ADDRESS`; it only writes a `TombStone{original_owner}` while the object stays with its current owner [1](#0-0) .
- `unburn()`, the only recovery path, unconditionally requires `exists<TombStone>(object_addr)` before it will do anything, and its `BURN_ADDRESS`-specific reclaim branch additionally requires the tombstone's recorded `original_owner` to match [2](#0-1) .
- The function that atomically transfers-to-`BURN_ADDRESS`-plus-writes-`TombStone` (`burn_object_with_transfer`) is explicitly `#[test_only]`, i.e. not part of the live/production module surface [3](#0-2) .

As a result, if any object owner (or any contract/integration built on top of `object`, e.g. copying `0xfff...fff` as a "burn" sentinel by convention, mistakenly reusing the address, or a UI/tooling bug) calls the normal `transfer`/`transfer_raw`/`transfer_call` entry point with `to = BURN_ADDRESS`, the object's `owner` field is silently updated to `BURN_ADDRESS`, no `TombStone` is created, and `unburn()` will subsequently abort with `EOBJECT_NOT_BURNT` for that object forever. Since `BURN_ADDRESS` corresponds to no valid account key, ownership can never be reclaimed through any other channel — this is a corrupted "owner" field (permanently and irrecoverably set to a dead address) with no code path back, exactly mirroring the report's core invariant break: a recovery function exists and is documented, but a different-but-valid transfer route silently routes around the bookkeeping it depends on.

### Impact Explanation
This is a custody-grade impact: any fungible/non-fungible object (and, transitively, all resources nested under it via `ExtendRef`/child objects, since object transfer moves "the object and all associated resources") that ends up at `BURN_ADDRESS` through the ordinary transfer path is permanently and non-recoverably lost, with no path to reassign, extend, or reclaim it — matching "Permanent lock or non-recoverable loss of object-held ... value" and "Supply or custody accounting corruption that moves value to the wrong holder or destroys recovery rights" in the required impact list.

### Likelihood Explanation
The trigger requires only a normal, permissionless call to `object::transfer`/`transfer_raw`/`transfer_call` (or any wrapping module built on top of them, such as generic marketplace/vault code that forwards a user-supplied destination address) with `to = BURN_ADDRESS`. No special privilege or attacker coordination is needed; the only question is how often `BURN_ADDRESS` is actually used as a destination outside the intended `burn()`/`unburn()` flow (e.g., by mistake, copy-paste of the constant, or third-party integrations treating it as a generic "burn sentinel" the way many other chains do). Given the constant is publicly documented in the module and BURN_ADDRESS-style sentinels are a common integration pattern, accidental or naive misuse is plausible, though I could not find any evidence in this repo of an actual mainnet integration exploiting or triggering this path — this remains inferred from the code's own logic rather than confirmed exploitation.

### Recommendation
Add an explicit guard in `transfer_raw_inner` (or in `transfer`/`transfer_raw`/`transfer_call` before calling it) that rejects direct transfers to `BURN_ADDRESS` unless routed through `burn()`/a production-safe equivalent of `burn_object_with_transfer` that also writes the `TombStone`. Alternatively, promote a production (non-test-only) function that atomically transfers to `BURN_ADDRESS` and writes the `TombStone` together, and have all normal transfer entry points special-case `BURN_ADDRESS` to always call that function so bookkeeping can never be bypassed.

### Proof of Concept
1. Owner `A` creates an object `O` with default ungated transfer enabled (`create_named_object`/`create_object`, standard flow).
2. `A` calls the production entry function `object::transfer_call(A, O, BURN_ADDRESS)` (or `object::transfer<T>(A, obj, BURN_ADDRESS)`), which succeeds because `BURN_ADDRESS` is a normal address with `allow_ungated_transfer` semantics unaffected — see `transfer_raw`/`transfer_raw_inner` [6](#0-5) .
3. `object::owner(O)` now returns `BURN_ADDRESS`; no `TombStone` resource exists at `O`'s address (only `burn()`/`burn_object_with_transfer` create one, and neither was called).
4. Any subsequent call to `object::unburn(A, O)` aborts with `EOBJECT_NOT_BURNT` because `exists<TombStone>(object_addr)` is false [7](#0-6) .
5. `O` (and any nested resources/objects under it) is now permanently owned by `BURN_ADDRESS`, an address with no corresponding private key, and no framework function exists to reassign or reclaim it — a permanent, non-recoverable loss of custody.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L550-594)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L608-639)
```text
    fun verify_ungated_and_descendant(owner: address, destination: address) {
        let current_address = destination;
        assert!(
            exists<ObjectCore>(current_address),
            error::not_found(EOBJECT_DOES_NOT_EXIST),
        );

        let object = borrow_global<ObjectCore>(current_address);
        assert!(
            object.allow_ungated_transfer,
            error::permission_denied(ENO_UNGATED_TRANSFERS),
        );

        let current_address = object.owner;
        let count = 0;
        while (owner != current_address) {
            count += 1;
            assert!(count < MAXIMUM_OBJECT_NESTING, error::out_of_range(EMAXIMUM_NESTING));
            // At this point, the first object exists and so the more likely case is that the
            // object's owner is not an object. So we return a more sensible error.
            assert!(
                exists<ObjectCore>(current_address),
                error::permission_denied(ENOT_OBJECT_OWNER),
            );
            let object = borrow_global<ObjectCore>(current_address);
            assert!(
                object.allow_ungated_transfer,
                error::permission_denied(ENO_UNGATED_TRANSFERS),
            );
            current_address = object.owner;
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L775-787)
```text
    #[test_only]
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
