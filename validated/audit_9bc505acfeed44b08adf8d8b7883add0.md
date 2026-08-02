## Finding: Unbounded ownership‑chain traversal in `object::root_owner` permits an ownership‑cycle DoS that permanently locks object‑hosted custody logic

### Title
Missing nesting-depth bound in `object::root_owner` allows a self-inflicted ownership cycle to permanently brick lazy module self-initialization and code republishing on an object - ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
Every other ownership-chain walker in the object model caps traversal at `MAXIMUM_OBJECT_NESTING` (8) to defend against cyclic ownership graphs: `object::owns` and `object::verify_ungated_and_descendant` both increment a counter and `assert!(count < MAXIMUM_OBJECT_NESTING, ...)`. [1](#0-0) [2](#0-1) 

`object::root_owner`, however, walks the same owner chain with **no depth bound at all**:

```
public fun root_owner<T: key>(self: Object<T>): address {
    let obj_owner = self.owner();
    while (is_object(obj_owner)) {
        obj_owner = address_to_object<ObjectCore>(obj_owner).owner();
    };
    obj_owner
}
``` [3](#0-2) 

`root_owner` is used for custody-relevant authorization decisions, not just display: `code::publish_package` records it as the "deploy owner" for lazily-initializing modules hosted on objects, and `init::assert_may_self_initialize` re-derives it to gate whether a module hosted at an object address may mint its own signer via `init::internal_maybe_initialize`. [4](#0-3) [5](#0-4) 

### Finding Description
`verify_ungated_and_descendant` (used by `object::transfer`/`transfer_raw`) only proves that the *transferring signer* appears in the owner chain of the object being moved within 8 hops; it does not prevent the *destination* side of the chain from looping back on itself. Because of this, a user who already owns two objects `A` and `B` outright can:

1. `transfer_raw(U, A, B)` — legal, since `U` directly owns `A` (`verify_ungated_and_descendant` succeeds trivially, count = 0).
2. `transfer_raw(U, B, A)` — legal, since `U` still directly owns `B` at that point (the check only requires that `U` appears within 8 hops starting from `B`, which is true since `B`'s owner is still `U`).

After step 2, `A.owner == B` and `B.owner == A`: a closed 2-cycle with no plain-account root. Because `owns`/`verify_ungated_and_descendant` are correctly bounded, subsequent `transfer`/`transfer_raw` calls on `A` or `B` will *fail* (abort with `EMAXIMUM_NESTING` after 8 hops) rather than hang — the objects are now permanently un-transferable by the normal transfer path. But any call path that reaches `root_owner` on `A` or `B` (or the deterministic address family walking through them) hits the unbounded `while (is_object(obj_owner))` loop and enters an infinite `A → B → A → B …` cycle, which can only terminate by exhausting the transaction's gas.

The exact corrupted state: the `InitializationState.modules[...].deploy_owner` recorded at `code::publish_package` time for a code/object module hosted at `A` (or `B`) can never again be validated by `assert_may_self_initialize`, because the validation step itself (`object::address_to_object<ObjectCore>(addr).root_owner()`) never returns — it always runs out of gas. Likewise, republishing/upgrading a package at that object address (`code::publish_package`, gated by `features::is_lazy_module_initialization_enabled() && object::is_object(addr)` → `root_owner()`) becomes permanently impossible once the object's owner or ancestor object is folded into such a cycle.

### Impact Explanation
Any custody logic that depends on lazy self-initialization at an object address (e.g., a vault/treasury module that mints a `MintRef`/`BurnRef`/`ExtendRef` into itself the first time it is called, or re-initializes state on upgrade) becomes **permanently unreachable** for that object once its owner chain is folded into a cycle: `internal_maybe_initialize` will always abort (out of gas) inside `assert_may_self_initialize`, so the signer needed to complete initialization or move required custody refs into place can never be minted again. Likewise, code owners lose the ability to upgrade or freeze a code object (`code::publish_package`) hosted at such an address, because `publish_package` itself calls `root_owner()` under the lazy-initialization feature flag. This is a non-recoverable, permanent lock of object-held control/value with no admin escape hatch in the module itself — matching the "permanent lock or non-recoverable loss of object-held value" custody category.

### Likelihood Explanation
Likelihood is **Low-to-Medium**: the attacker must already hold direct transfer authority over both objects being folded into the cycle (only the account/objects that legitimately own `A` and `B` can execute the two `transfer_raw` calls that create the cycle), so this is primarily a "shoot yourself in the foot" or targeted griefing vector rather than an outright unauthorized takeover. It becomes a real custody risk in any protocol pattern where a user, a delegated operator, or an untrusted composability partner is given transfer authority over objects that later host (or ancestor-own) an object with a lazily-initializing module or an upgradeable code object — a fairly common pattern given `object_code_deployment.move`'s code-object model and `init.move`'s lazy self-init feature. It is independent of privileged/governance behavior and requires no leaked keys, node misbehavior, or social engineering — purely a missing bound check reachable by any regular signer.

### Recommendation
Bound `object::root_owner`'s traversal identically to `owns`/`verify_ungated_and_descendant` (cap at `MAXIMUM_OBJECT_NESTING` and abort with `EMAXIMUM_NESTING` on overflow instead of looping unboundedly). Additionally, consider rejecting `transfer_raw`/`transfer` calls that would create a cycle in the destination's owner chain (not just verifying the signer's ancestry), since a bounded-but-cyclic ownership graph still permanently strands any code path (current or future) that walks "up" the chain to a root.

### Proof of Concept
```move
// Setup: signer U creates two plain objects it owns directly.
let cref_a = object::create_object(signer::address_of(u));
let cref_b = object::create_object(signer::address_of(u));
let obj_a = object::object_from_constructor_ref<object::ObjectCore>(&cref_a);
let obj_b = object::object_from_constructor_ref<object::ObjectCore>(&cref_b);

// Publish a lazily-self-initializing module to object A's address (feature-gated),
// so code::publish_package records deploy_owner = root_owner(A) = U at this point.
code::publish_package_txn(&create_signer(obj_a.object_address()), ...);

// Step 1: transfer A -> B. Legal: U directly owns A.
object::transfer_raw(u, obj_a.object_address(), obj_b.object_address());

// Step 2: transfer B -> A. Legal: U still directly owns B at this point.
object::transfer_raw(u, obj_b.object_address(), obj_a.object_address());

// Now A.owner == B and B.owner == A: a closed cycle.
// Any subsequent call that invokes root_owner on A or B, e.g.:
//   code::publish_package(...) to upgrade the module at A (gated by
//   features::is_lazy_module_initialization_enabled() && object::is_object(addr))
// or
//   init::internal_maybe_initialize(...) inside the deployed module,
//   which calls init::assert_may_self_initialize -> root_owner(A)
// will loop forever between A and B until the transaction runs out of gas,
// permanently preventing upgrade/self-init for that object.
``` [6](#0-5) [7](#0-6) 

**Note on verification limits**: I traced this purely through static reading of `object.move`, `code.move`, and `init.move`; I was not able to execute the Move VM to empirically confirm gas exhaustion behavior for the cyclic `root_owner` call (no test/execution tooling available in this ask-only session). The existing unit tests in `init.move` (`self_init_blocked_when_owner_transferred`, `self_init_blocked_when_ancestor_transferred`, etc.) confirm the intended non-cyclic transfer-then-block semantics but do not cover the cyclic-ownership case, which is consistent with this being an untested edge case rather than a deliberately accepted risk.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L739-748)
```text
    #[view]
    /// Returns the root owner of an object. As objects support nested ownership, it can be useful
    /// to determine the identity of the starting point of ownership.
    public fun root_owner<T: key>(self: Object<T>): address {
        let obj_owner = self.owner();
        while (is_object(obj_owner)) {
            obj_owner = address_to_object<ObjectCore>(obj_owner).owner();
        };
        obj_owner
    }
```

**File:** aptos-move/framework/aptos-framework/sources/code.move (L179-187)
```text
        // Record, per module in this package, the object's transitive root owner at (re)publish, so
        // lazy self-init can detect a later transfer of the object or an ancestor since that module
        // was published (see `init::internal_maybe_initialize`). Objects only; feature-gated.
        if (features::is_lazy_module_initialization_enabled() && object::is_object(addr)) {
            let owner = object::address_to_object<object::ObjectCore>(addr).root_owner();
            module_names.for_each_ref(|name| {
                init::record_deploy_owner(addr, *name.bytes(), owner);
            });
        };
```

**File:** aptos-move/framework/aptos-framework/sources/init.move (L54-68)
```text
    public fun internal_maybe_initialize(only_once: bool): Option<signer> {
        assert!(
            features::is_lazy_module_initialization_enabled(),
            error::invalid_state(ELAZY_MODULE_INITIALIZATION_NOT_ENABLED),
        );
        let (addr, module_id) = get_caller_address_and_module_id();
        if (check_and_set_initialized(addr, module_id, only_once)) {
            option::none()
        } else {
            // Guard only when actually minting: a legitimate transfer after initialization must not
            // brick ordinary calls. An abort here rolls back the mark set above.
            assert_may_self_initialize(addr, module_id);
            option::some(create_signer::create_signer(addr))
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/init.move (L70-83)
```text
    /// Aborts unless the module at `addr` may self-initialize now. Only object-hosted modules are
    /// gated: an object must still have the transitive root owner recorded for this module at
    /// publish, so a transfer of the object or an ancestor, or its deletion, blocks self-init; an
    /// object with no record is fail-closed. Account addresses authorize their own code by publishing.
    fun assert_may_self_initialize(addr: address, module_id: ModuleId) {
        let recorded = recorded_deploy_owner(addr, module_id);
        let ok = if (recorded.is_some()) {
            object::is_object(addr)
                && recorded.destroy_some() == object::address_to_object<ObjectCore>(addr).root_owner()
        } else {
            !object::is_object(addr)
        };
        assert!(ok, error::permission_denied(EOWNER_CHANGED_SINCE_DEPLOY));
    }
```
