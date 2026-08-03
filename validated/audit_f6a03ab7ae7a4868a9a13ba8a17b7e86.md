No vulnerability found for this question.

**Reasoning:**

`verify_ungated_and_descendant` in `aptos-move/framework/aptos-framework/sources/object.move` walks the ownership chain from the destination object upward, checking `allow_ungated_transfer` at each hop, and succeeds as soon as it finds `current_address == owner` anywhere in that chain (bounded by `MAXIMUM_OBJECT_NESTING = 8`), or aborts with `EMAXIMUM_NESTING`/`ENOT_OBJECT_OWNER`/`ENO_UNGATED_TRANSFERS` otherwise. [1](#0-0) 

The premise of the question — that transfer authority must chain to the "real terminal owner" — misreads the intended semantics. The function's doc comment explicitly states this is by design: an owner of *any* intermediate object in the ownership hierarchy is authorized to move descendants of that object, not just the ultimate root owner: [2](#0-1) 

So matching `owner` at any point in the chain — not just at the root — is the intended, documented behavior, not a bypass.

There is also no room for a "transient" match. Move transactions execute atomically: every `borrow_global<ObjectCore>` read inside the `while` loop happens sequentially within the same transaction execution against consistent global state, so there is no TOCTOU window where an attacker's address could appear in the chain only momentarily. For the loop to match `owner == current_address` at some hop, the attacker's address must genuinely be the `owner` field of some `ObjectCore` in that real on-chain chain at the time of the check — i.e., the attacker must already legitimately own that intermediate object. This requires pre-existing ownership/permission, which the review's decision standard explicitly excludes ("Reject anything that needs pre-existing permissions").

A cyclic ownership chain (e.g., attacker inserts an object that points back into a cycle before reaching the signer) does not bypass the check either: the `count` bound strictly limits iterations to `MAXIMUM_OBJECT_NESTING` regardless of cycles, so the loop will correctly abort with `EMAXIMUM_NESTING` rather than falsely succeed — at worst this is a denial-of-transfer for that specific caller, not an unauthorized transfer to an attacker. [3](#0-2) 

Since no unprivileged, attacker-controlled path can inject a false match into `current_address == owner` without already possessing legitimate on-chain ownership of an ancestor object, and since the loop bound correctly prevents unbounded/incorrect traversal even with cycles, there is no custody boundary violation here.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L568-580)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L605-639)
```text
    /// This checks that the destination address is eventually owned by the owner and that each
    /// object between the two allows for ungated transfers. Note, this is limited to a depth of 8
    /// objects may have cyclic dependencies.
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
