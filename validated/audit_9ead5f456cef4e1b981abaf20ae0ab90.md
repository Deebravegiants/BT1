[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L119-123)
```text
        let publisher_address = signer::address_of(publisher);
        assert!(
            object::is_owner(code_object, publisher_address),
            error::permission_denied(ENOT_CODE_OBJECT_OWNER),
        );
```

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L125-132)
```text
        let code_object_address = code_object.object_address();
        assert!(exists<ManagingRefs>(code_object_address), error::not_found(ECODE_OBJECT_DOES_NOT_EXIST));

        let extend_ref = &borrow_global<ManagingRefs>(code_object_address).extend_ref;
        let code_signer = &extend_ref.generate_signer_for_extending();
        code::publish_package_txn(code_signer, metadata_serialized, code);

        event::emit(Upgrade { object_address: signer::address_of(code_signer), });
```

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L149-154)
```text
    public fun get_code_object_signer(publisher: &signer, code_object: Object<PackageRegistry>): signer {
        let publisher_address = signer::address_of(publisher);
        assert!(
            object::is_owner(code_object, publisher_address),
            error::permission_denied(ENOT_CODE_OBJECT_OWNER),
        );
```
