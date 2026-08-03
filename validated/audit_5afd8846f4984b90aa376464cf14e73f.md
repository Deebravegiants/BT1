No vulnerability found for this question.

**Analysis:**

The `upgrade` entry function in `object_code_deployment.move` already gates the entire code-publishing action behind an ownership check: [1](#0-0) 

Once `object::is_owner(code_object, publisher_address)` passes, the caller is by definition the entity that already controls the code object's `ExtendRef`/signer, and can call `code::publish_package_txn` with whatever `metadata_serialized`/`code` they choose — including entirely new modules. The framework's `check_upgradability`/`check_coexistence` logic in `code.move` only restricts what happens across *different* packages coexisting in the same registry, and only forbids removing modules from the *existing* package on upgrade; it never restricted adding brand-new modules, because that's an intended, documented capability of upgradable packages, not a gap: [2](#0-1) 

This means the described "attack" requires the actor to already be the current object owner — i.e., pre-existing custody authority over the code object — which the review's Decision Standard explicitly excludes ("Reject anything that needs pre-existing permissions"). An owner who is trusted enough to upgrade a package's *existing* module logic already has the power to rewrite any function body in that module (add a backdoor withdraw path inside an existing "trusted" module), so restricting the addition of new module *names* would not close any real boundary — the boundary is ownership of the object, which is enforced identically for both cases.

The actual custody implication here is a pre-existing, well-known design constraint: any downstream system that "whitelists" a code-object address as trusted must treat that trust as valid only if the package is frozen/immutable via `freeze_code_object` (which sets `upgrade_policy_immutable()`): [3](#0-2) 

If the whitelisted package is left mutable, *any* owner-authorized upgrade (not specifically "adding a new module") can already change its logic arbitrarily. This is a property of upgradable objects, not a missing check in `upgrade`, and does not constitute a new custody boundary crossing by an unprivileged actor.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L119-130)
```text
        let publisher_address = signer::address_of(publisher);
        assert!(
            object::is_owner(code_object, publisher_address),
            error::permission_denied(ENOT_CODE_OBJECT_OWNER),
        );

        let code_object_address = code_object.object_address();
        assert!(exists<ManagingRefs>(code_object_address), error::not_found(ECODE_OBJECT_DOES_NOT_EXIST));

        let extend_ref = &borrow_global<ManagingRefs>(code_object_address).extend_ref;
        let code_signer = &extend_ref.generate_signer_for_extending();
        code::publish_package_txn(code_signer, metadata_serialized, code);
```

**File:** aptos-move/framework/aptos-framework/sources/code.move (L233-254)
```text
    public fun freeze_code_object(publisher: &signer, code_object: Object<PackageRegistry>) acquires PackageRegistry {
        let code_object_addr = code_object.object_address();
        assert!(exists<PackageRegistry>(code_object_addr), error::not_found(ECODE_OBJECT_DOES_NOT_EXIST));
        assert!(
            object::is_owner(code_object, signer::address_of(publisher)),
            error::permission_denied(ENOT_PACKAGE_OWNER)
        );

        let registry = borrow_global_mut<PackageRegistry>(code_object_addr);
        registry.packages.for_each_mut(|pack| {
            let package: &mut PackageMetadata = pack;
            package.upgrade_policy = upgrade_policy_immutable();
        });

        // We unfortunately have to make a copy of each package to avoid borrow checker issues as check_dependencies
        // needs to borrow PackageRegistry from the dependency packages.
        // This would increase the amount of gas used, but this is a rare operation and it's rare to have many packages
        // in a single code object.
        registry.packages.for_each(|pack| {
            check_dependencies(code_object_addr, &pack);
        });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/code.move (L266-295)
```text
    /// Checks whether the given package is upgradable, and returns true if a compatibility check is needed.
    fun check_upgradability(
        old_pack: &PackageMetadata, new_pack: &PackageMetadata, new_modules: &vector<String>) {
        assert!(old_pack.upgrade_policy.policy < upgrade_policy_immutable().policy,
            error::invalid_argument(EUPGRADE_IMMUTABLE));
        assert!(can_change_upgrade_policy_to(old_pack.upgrade_policy, new_pack.upgrade_policy),
            error::invalid_argument(EUPGRADE_WEAKER_POLICY));
        let old_modules = get_module_names(old_pack);

        old_modules.for_each_ref(|old_module| {
            assert!(
                vector::contains(new_modules, old_module),
                EMODULE_MISSING
            );
        });
    }

    /// Checks whether a new package with given names can co-exist with old package.
    fun check_coexistence(old_pack: &PackageMetadata, new_modules: &vector<String>) {
        // The modules introduced by each package must not overlap with `names`.
        old_pack.modules.for_each_ref(|old_mod| {
            let old_mod: &ModuleMetadata = old_mod;
            let j = 0;
            while (j < vector::length(new_modules)) {
                let name = vector::borrow(new_modules, j);
                assert!(&old_mod.name != name, error::already_exists(EMODULE_NAME_CLASH));
                j += 1;
            };
        });
    }
```
