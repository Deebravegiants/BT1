[1](#0-0) [2](#0-1)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L86-97)
```text
    public entry fun create_resource_account(
        origin: &signer, seed: vector<u8>, optional_auth_key: vector<u8>
    ) acquires Container {
        let (resource, resource_signer_cap) =
            account::create_resource_account(origin, seed);
        rotate_account_authentication_key_and_store_capability(
            origin,
            resource,
            resource_signer_cap,
            optional_auth_key
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L141-163)
```text
    fun rotate_account_authentication_key_and_store_capability(
        origin: &signer,
        resource: signer,
        resource_signer_cap: account::SignerCapability,
        optional_auth_key: vector<u8>
    ) acquires Container {
        let origin_addr = signer::address_of(origin);
        if (!exists<Container>(origin_addr)) {
            move_to(origin, Container { store: simple_map::create() })
        };

        let container = borrow_global_mut<Container>(origin_addr);
        let resource_addr = signer::address_of(&resource);
        container.store.add(resource_addr, resource_signer_cap);

        let auth_key =
            if (optional_auth_key.is_empty()) {
                account::get_authentication_key(origin_addr)
            } else {
                optional_auth_key
            };
        account::rotate_authentication_key_internal(&resource, auth_key);
    }
```
