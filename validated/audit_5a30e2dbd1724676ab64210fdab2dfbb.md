## Reduced Custody Invariant

The ENS bug boils down to: a *root-of-truth check* (whether an ETH2LD is actually wrapped) can be silently invalidated by an intermediate state change that a later "trusted" verification step never re-derives from scratch — it trusts a value that can be made stale/cyclical between check and use.

Aptos analog candidates considered:
1. `resource_account::create_resource_account` re-claiming a pre-existing unclaimed account — documented, intentional, not a broken invariant.
2. `multisig_account::create_with_existing_account*` leaving old signer-capability/auth-key control alive — explicitly documented caveat (admin/operator assumption, excluded by the custody gate).
3. `init.move` lazy module self-init gating via `object::root_owner()` comparison to a recorded deploy-time owner — this is the strongest candidate because it directly mirrors "verify true current authority state before granting privileged action," and its verification primitive (`root_owner()`) has an exploitable structural weakness not present in its sibling primitives.

## Title
Unbounded ownership-chain walk in `object::root_owner()` allows an attacker-created cyclic object to permanently hang any custody/authorization check built on it - (File: aptos-move/framework/aptos-framework/sources/object.move)

## Summary
`object::root_owner()` walks the object ownership chain (`while (is_object(obj_owner)) { obj_owner = ...owner() }`) with **no depth bound**, unlike the two structurally identical traversal functions in the same module, `owns()` and `verify_ungated_and_descendant()`, which both explicitly cap iteration with `MAXIMUM_OBJECT_NESTING`. Because Aptos objects can be made to own themselves (a documented, reachable state — see `test_cyclic_ownership_transfer_should_fail`), any caller of `root_owner()` on such an object loops until it exhausts gas and aborts, permanently and unrecoverably.

## Finding Description
`object.move` defines three chain-walking accessors:
- `owns()` [1](#0-0) 
- `verify_ungated_and_descendant()` [2](#0-1) 
- `root_owner()` [3](#0-2) 

The first two guard against unbounded/cyclic traversal with an explicit counter checked against `MAXIMUM_OBJECT_NESTING` on every loop iteration. `root_owner()` has no such counter — it only terminates when it reaches a non-object address:
```
public fun root_owner<T: key>(self: Object<T>): address {
    let obj_owner = self.owner();
    while (is_object(obj_owner)) {
        obj_owner = address_to_object<ObjectCore>(obj_owner).owner();
    };
    obj_owner
}
```
A self-owned object is a reachable, unprivileged state: `object::transfer(creator, obj1, obj1.object_address())` succeeds once (the framework's own test `test_cyclic_ownership_transfer_should_fail` demonstrates the *first* self-transfer succeeds — the second call is what aborts, because `verify_ungated_and_descendant` on the *next* transfer detects the now-existing cycle). After the first self-transfer, `obj1.owner == obj1` permanently (no further transfer is required for the DoS — the object is already self-owned and stuck).

`root_owner()` is the exact verification primitive used by the framework's own object-hosted lazy module self-initialization gate, which is the closest Aptos analog to the ENS "verify true wrapped/authority state" pattern:
```
fun assert_may_self_initialize(addr: address, module_id: ModuleId) {
    let recorded = recorded_deploy_owner(addr, module_id);
    let ok = if (recorded.is_some()) {
        object::is_object(addr)
            && recorded.destroy_some() == object::address_to_object<ObjectCore>(addr).root_owner()
    ...
``` [4](#0-3) 
and by `code::publish_package`'s owner-recording step used to arm this same gate:
```
if (features::is_lazy_module_initialization_enabled() && object::is_object(addr)) {
    let owner = object::address_to_object<object::ObjectCore>(addr).root_owner();
    ...
``` [5](#0-4) 

If an object anywhere in an ownership hierarchy above a code object (or any other object relying on `root_owner()`, e.g. custody logic that determines a "top-level" account) becomes self-owned/cyclic — which requires only an unprivileged, ungated `object::transfer` by *that object's own current owner* onto itself — every subsequent `root_owner()` call on any descendant hangs and the enclosing transaction aborts on out-of-gas. This is not merely "the object owning itself is a no-op state" — it is a **live landmine**: any code path (present or future) that calls `root_owner()` transitively on that address becomes permanently non-functional, with no recovery path, because undoing the self-ownership itself requires a `transfer()` whose `verify_ungated_and_descendant` call will itself hit the depth bound and abort (as shown by the framework's own test), and there is no "un-cycle" function exposed.

## Impact Explanation
Impact is scoped to whatever logic depends on `root_owner()`. Today this includes the framework's lazy-module self-initialization gate (`init.move`/`code.move`), meaning a code object nested under (or equal to) a self-owned ancestor can never complete lazy self-initialization — a permanent, non-recoverable lock of that module's initialization path, satisfying the "Permanent lock or non-recoverable loss of object-held ... value" custody-impact category, since object-hosted modules performing lazy init (e.g., to mint/register a fungible asset's stores, dispatch hooks, or metadata) can never run. Because `root_owner()` is a public framework API, any third-party contract that uses it for custody/authorization decisions (e.g., "only the ultimate account owner may act") inherits the same permanent-DoS exposure the moment an attacker (who need not be privileged — merely the current owner of some ancestor object, which can be attacker-controlled by construction) creates a self-owned node in the hierarchy.

## Likelihood Explanation
High likelihood of triggerability, but impact is currently gated by how widely `root_owner()` is relied upon (presently limited mainly to the lazy-init gate). Creating the self-owned object requires only a single `transfer` call by the object's own current owner — no privilege beyond normal object ownership is needed, and the framework's own test suite proves this initial self-transfer succeeds. This makes the trigger trivial and fully unprivileged; the missing bound is a straightforward code inspection finding (asymmetric with the two sibling functions in the same file).

## Recommendation
Add the same `MAXIMUM_OBJECT_NESTING` counter check used in `owns()` and `verify_ungated_and_descendant()` to `root_owner()`, aborting with `EMAXIMUM_NESTING` (or a similar explicit error) rather than looping unbounded. Additionally, consider rejecting self-referential transfers (`to == object_address`) at the `transfer`/`transfer_raw` layer outright, since a self-owned object is a degenerate state with no legitimate use case and currently can only be created (but never later corrected) once formed.

## Proof of Concept
```move
#[test(creator = @0x123)]
fun poc_root_owner_infinite_loop(creator: &signer) {
    let obj1 = create_simple_object(creator, b"1");
    // Single, unprivileged self-transfer by the object's own current owner succeeds
    // (framework's own test proves this call alone does not abort).
    object::transfer(creator, obj1, obj1.object_address());

    // obj1 is now permanently self-owned. Any call relying on root_owner() over this
    // hierarchy now loops forever / aborts on gas exhaustion, e.g.:
    let _ = object::address_to_object<object::ObjectCore>(obj1.object_address()).root_owner();
    // -> never returns; any transaction path through here (e.g. code::publish_package's
    // record_deploy_owner step, or init::assert_may_self_initialize) permanently fails.
}
```
Note: this PoC composes directly from code already present in `object.move`'s own test module (`create_simple_object`, and the transfer sequence proven safe by `test_cyclic_ownership_transfer_should_fail`); the missing bound in `root_owner()` itself was not independently executed against a live node, so the exact gas-exhaustion behavior (vs. a different abort) should be confirmed by running this test against the actual framework.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L710-736)
```text
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
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L742-748)
```text
    public fun root_owner<T: key>(self: Object<T>): address {
        let obj_owner = self.owner();
        while (is_object(obj_owner)) {
            obj_owner = address_to_object<ObjectCore>(obj_owner).owner();
        };
        obj_owner
    }
```

**File:** aptos-move/framework/aptos-framework/sources/init.move (L74-83)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/code.move (L182-187)
```text
        if (features::is_lazy_module_initialization_enabled() && object::is_object(addr)) {
            let owner = object::address_to_object<object::ObjectCore>(addr).root_owner();
            module_names.for_each_ref(|name| {
                init::record_deploy_owner(addr, *name.bytes(), owner);
            });
        };
```
