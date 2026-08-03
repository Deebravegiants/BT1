No vulnerability found for this question.

**Reasoning:** The premise misattributes an invariant to `object::address_to_object` that the framework never establishes. `address_to_object<T>` merely constructs a `Object<T>` struct wrapping an address after checking `exists_at<T>` [1](#0-0) , and the framework's own doc comment explicitly warns that possessing an `Object<T>` handle carries no ownership guarantee — "these can only provide guarantees based upon the underlying data type, that is the validity of T existing at an address is something that cannot be verified by any other module than the module that defined T" [1](#0-0) .

Ownership authority is derived exclusively from the live `ObjectCore.owner` field, checked at call time via `is_owner`/`owns`, not from anything embedded in the `Object<T>` value itself: `is_owner` computes `object.owner() == owner` by reading `ObjectCore` fresh from global storage [2](#0-1) , and `owns` walks the live ownership chain the same way [3](#0-2) . Since `Object<T>` only has `copy, drop, store` abilities and no privileged fields [4](#0-3) , constructing it via `address_to_object` for a victim's object and then calling `is_owner(object, attacker_address)` will correctly evaluate to `false` because `ObjectCore.owner` still equals the victim's address — the check reads current on-chain state, not attacker-supplied data.

The scenario as framed requires a downstream module to *skip* calling `is_owner`/`owns` against the actual transaction signer and instead treat mere possession of an `Object<T>` value as proof of authority. That would be a bug in that specific downstream module's custody logic, not a defect in `object.move`/`object.rs`. The review question itself concedes this by asking to "assert the function separately validates `is_owner`/`owns` ... and aborts" — which is exactly what correctly-written downstream code (and the framework's own `transfer`, `burn`, `unburn` entrypoints, which all gate on `is_owner`/owner-field comparisons [5](#0-4) [6](#0-5) ) does. No unprivileged input crosses a real custody boundary in `object.move` itself.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L129-135)
```text
    /// A pointer to an object -- these can only provide guarantees based upon the underlying data
    /// type, that is the validity of T existing at an address is something that cannot be verified
    /// by any other module than the module that defined T. Similarly, the module that defines T
    /// can remove it from storage at any point in time.
    struct Object<phantom T> has copy, drop, store {
        inner: address,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L572-580)
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L698-704)
```text
    #[view]
    /// Return true if the provided address is the current owner.
    ///
    /// Note: intentionally not using `self` as first argument, as a.is_owner(b) syntax would be ambiguous.
    public fun is_owner<T: key>(object: Object<T>, owner: address): bool {
        object.owner() == owner
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L706-737)
```text
    #[view]
    /// Return true if the provided address has indirect or direct ownership of the provided object.
    ///
    /// Note: intentionally not using `self` as first argument, as a.owns(b) syntax would be ambiguous.
    public fun owns<T: key>(object: Object<T>, owner: address): bool {
        let current_address = object.object_address();

        assert!(
            exists<ObjectCore>(current_address),
            error::not_found(EOBJECT_DOES_NOT_EXIST),
        );

        if (current_address == owner) {
            return true
        };

        let object = borrow_global<ObjectCore>(current_address);
        let current_address = object.owner;

        let count = 0;
        while (owner != current_address) {
            count += 1;
            assert!(count < MAXIMUM_OBJECT_NESTING, error::out_of_range(EMAXIMUM_NESTING));
            if (!exists<ObjectCore>(current_address)) {
                return false
            };

            let object = borrow_global<ObjectCore>(current_address);
            current_address = object.owner;
        };
        true
    }
```
