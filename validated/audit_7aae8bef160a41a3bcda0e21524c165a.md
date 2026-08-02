### Title
Unbounded ownership-cycle traversal in `object::root_owner` permits permanent custody lock of any object relying on root-owner resolution - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
The external report's root cause is that a custody-dependent operation (opening a leveraged position) trusted a *delegated authority* (`approve`) without verifying *actual custody* (holding the NFT), and the contract had no bound/guard on what could happen if that assumption was wrong. The Aptos-native analog is in the object ownership model itself: `object::transfer_raw` only validates that the **signer** can reach the **destination** through its ownership chain, but never checks that the object being moved is not already an ancestor of that destination. This lets an unprivileged actor legitimately construct a **cyclic ownership graph** between two objects they own. `object::root_owner()` — the function multiple custody-relevant subsystems use to resolve "who ultimately controls this object" — has an **unbounded** `while` loop, unlike the other ownership-chain walkers in the same file (`owns`, `verify_ungated_and_descendant`) which are explicitly capped at `MAXIMUM_OBJECT_NESTING`. Any later attempt to resolve root ownership of an object nested into such a cycle aborts (loops until gas exhaustion) forever.

### Finding Description
`object::transfer_raw` / `verify_ungated_and_descendant` only check that the *destination*'s ownership chain eventually reaches the calling signer: [1](#0-0) 

Nothing in this check inspects whether the *object being moved* is itself already present in the destination's ownership chain. Consequently, a single account fully owning two objects `A` and `B` can:

1. `transfer(you, A, B_addr)` — legal, because `verify_ungated_and_descendant` finds `B.owner == you` immediately.
2. `transfer(you, B, A_addr)` — also legal, because at check time `A.owner == B_addr` and `B.owner == you`, so the chain from `A_addr` still resolves back to `you` (the mutation to `B.owner` hasn't happened yet).

After step 2, `A.owner == B_addr` and `B.owner == A_addr`: a genuine 2-object ownership cycle, created entirely with normal, unprivileged `transfer` calls on objects the caller legitimately owns.

`object::root_owner()` walks the ownership chain with **no depth bound**: [2](#0-1) 

Compare this to `owns()` and `verify_ungated_and_descendant()`, both of which explicitly guard against unbounded traversal: [3](#0-2) 

Once a cycle exists, any call to `root_owner()` on `A` or `B` (or on any object subsequently made a descendant of `A`/`B`, e.g. by a victim depositing an object into what looks like a normal vault/wrapper object) loops indefinitely and the transaction runs out of gas — a permanent, unrecoverable revert.

This directly matters for custody because `object::root_owner()` is the primitive used by the framework's newest ownership-transfer-detection mechanism, `init.move`, to gate object-hosted module self-initialization and to decide whether a code object may mint itself a signer: [4](#0-3) 

and by `code::publish_package`, which records the transitive root owner at every (re)publish specifically so that later custody/ownership changes can be detected: [5](#0-4) 

If a code object (or any future/custom module using `root_owner()` as its "true owner" oracle for authority decisions — the same conceptual role that Uniswap's NFT-ownership check should have played) is ever placed into or beneath an attacker-manufactured cyclic ownership graph, its root-owner resolution becomes permanently unusable. Any custody-relevant object nested (directly or transitively) under an object involved in the cycle inherits the same unbounded-loop failure the moment code calls `root_owner()` on it.

### Impact Explanation
This breaks the custody invariant "object creation, transfer, burn, extensibility, and ownership refs must preserve the intended controller" (Custody Pivot #1). Concretely:
- It is a permanent, non-recoverable denial of a core ownership-resolution primitive (`root_owner`) for any object drawn into a cycle, satisfying "Permanent lock or non-recoverable loss of object-held ... value" whenever value-bearing resources (e.g. `ExtendRef`/`ManagingRefs`-gated fungible-asset custody, or a code object relying on lazy self-init to mint the signer that controls its resources) live at or under an address whose root-owner path is corrupted this way.
- Unlike a generic network DoS, this is a self-contained, root-cause bug in the object ownership model itself (an authority/consistency break: `transfer_raw` fails to preserve the acyclicity invariant that `root_owner`, `owns`, and `verify_ungated_and_descendant` all implicitly assume), reachable by any unprivileged account using only standard `object::transfer` entry functions on objects it owns.

### Likelihood Explanation
Creating the cycle requires no special privilege — only two objects owned by the same account and two ordinary `object::transfer` calls, both of which pass all existing checks as shown above. The harder part for high-impact exploitation is getting a *victim's* custody-relevant object nested under the cyclic structure (e.g., tricking a user into depositing into what looks like a normal vault/object-wrapper), which raises likelihood from "trivial self-DoS" to "moderate, requires a social/economic vector," similar in spirit to how the original Uniswap bug required an LP to approve an operator without realizing the implication.

### Recommendation
Bound the traversal in `object::root_owner()` with the same `MAXIMUM_OBJECT_NESTING` guard used by `owns()` and `verify_ungated_and_descendant()`, and/or reject a `transfer`/`transfer_raw` call whenever the object being moved is discovered while walking the destination's ownership chain (i.e., explicitly prevent cycle formation in `verify_ungated_and_descendant`), so ownership graphs are provably acyclic by construction rather than merely by convention.

### Proof of Concept
```move
// All actions performed by a single unprivileged account `you`.
let ctor_a = object::create_object(@you);
let a = object::object_from_constructor_ref<ObjectCore>(&ctor_a);
let a_addr = object::address_from_constructor_ref(&ctor_a);

let ctor_b = object::create_object(@you);
let b = object::object_from_constructor_ref<ObjectCore>(&ctor_b);
let b_addr = object::address_from_constructor_ref(&ctor_b);

// Step 1: A -> B (legal: B.owner == you)
object::transfer(&you_signer, a, b_addr);

// Step 2: B -> A (legal at check time: A.owner == b_addr, B.owner == you)
object::transfer(&you_signer, b, a_addr);

// Now A.owner == b_addr and B.owner == a_addr: a genuine ownership cycle.
// Any subsequent call loops forever / aborts on gas exhaustion:
let _ = object::address_to_object<ObjectCore>(a_addr).root_owner(); // never returns
```
This mirrors `init.move`'s own regression tests for legitimate ownership-transfer detection (`self_init_blocked_when_owner_transferred`, `self_init_blocked_when_ancestor_transferred`) [6](#0-5) , which assume `root_owner()` always terminates — an assumption this cycle violates.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/init.move (L70-100)
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

    /// The object root owner recorded for `module_id` at its last publish, or `none` if the module
    /// has no such record (an account module, or an object module never recorded).
    fun recorded_deploy_owner(addr: address, module_id: ModuleId): Option<address> {
        if (!exists<InitializationState>(addr)) return option::none();
        let modules = &InitializationState[addr].modules;
        if (modules.contains(&module_id)) modules.borrow(&module_id).deploy_owner else option::none()
    }

    /// Records `owner` as the object root owner of the module named `module_name` at (re)publish, to
    /// gate its later self-init (see `assert_may_self_initialize`). Called per module by
    /// `code::publish_package` for object addresses only.
    package fun record_deploy_owner(addr: address, module_name: vector<u8>, owner: address) {
        let module_id = module_id_from_name(module_name);
        ensure_module_state(addr, module_id);
        InitializationState[addr].modules.borrow_mut(&module_id).deploy_owner = option::some(owner);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/init.move (L196-224)
```text
    #[test]
    #[expected_failure(abort_code = EOWNER_CHANGED, location = Self)]
    fun self_init_blocked_when_owner_transferred() {
        let cref = object::create_object(@0xcafe);
        let addr = object::address_from_constructor_ref(&cref);
        record_current_owner(addr, b"m");
        object::transfer(
            &create_signer::create_signer(@0xcafe),
            object::object_from_constructor_ref<ObjectCore>(&cref),
            @0xbeef,
        );
        assert_may_init(addr, b"m");
    }

    #[test]
    #[expected_failure(abort_code = EOWNER_CHANGED, location = Self)]
    fun self_init_blocked_when_ancestor_transferred() {
        // Transferring the parent leaves the child's direct owner fixed but moves its root owner.
        let parent = object::create_object(@0xcafe);
        let parent_addr = object::address_from_constructor_ref(&parent);
        let child = object::address_from_constructor_ref(&object::create_object(parent_addr));
        record_current_owner(child, b"m");
        object::transfer(
            &create_signer::create_signer(@0xcafe),
            object::object_from_constructor_ref<ObjectCore>(&parent),
            @0xbeef,
        );
        assert_may_init(child, b"m");
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
