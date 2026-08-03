No vulnerability found for this question.

**Reasoning:** The premise of "spoofing" the `origin` signer is not possible in Move's execution model. `origin: &signer` in `create_resource_account_and_publish_package` is the unforgeable capability granted only to the entity that authenticates the transaction (i.e., whoever signs with the private key controlling that account) — a signer reference cannot be constructed or substituted by an attacker for an account they don't control [1](#0-0) .

Inside `rotate_account_authentication_key_and_store_capability`, the code derives `origin_addr` via `signer::address_of(origin)` and stores the newly created resource account's `SignerCapability` in a `Container` keyed by `resource_addr` under `origin_addr`'s own account storage [2](#0-1) . Since `origin` is always the caller's genuine signer (there is no delegated/passed-in address parameter that could diverge from the actual signer), "the attacker" calling this entry function is necessarily also the "origin" — they can only ever create a resource account and store its capability under their *own* address, never under a legitimate victim's `Container`. There is no code path here where an unprivileged caller can inject an arbitrary `origin_addr` distinct from their own transaction signer.

The unit tests confirm this invariant: capability lookup is scoped to `borrow_global<Container>(user_addr)` matching the actual signer that created the resource account [3](#0-2) .

No custody boundary is crossed — the described attack would require forging another account's signer, which is outside Move's security model and not reachable from unprivileged transaction input.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L124-139)
```text
    public entry fun create_resource_account_and_publish_package(
        origin: &signer,
        seed: vector<u8>,
        metadata_serialized: vector<u8>,
        code: vector<vector<u8>>
    ) acquires Container {
        let (resource, resource_signer_cap) =
            account::create_resource_account(origin, seed);
        aptos_framework::code::publish_package_txn(&resource, metadata_serialized, code);
        rotate_account_authentication_key_and_store_capability(
            origin,
            resource,
            resource_signer_cap,
            ZERO_AUTH_KEY
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L141-154)
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
```

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L198-214)
```text
    #[test(user = @0x1111)]
    public entry fun test_create_account_and_retrieve_cap(user: signer) acquires Container {
        let user_addr = signer::address_of(&user);
        account::create_account(user_addr);

        let seed = x"01";

        create_resource_account(&user, copy seed, vector::empty());
        let container = borrow_global<Container>(user_addr);

        let resource_addr =
            aptos_framework::account::create_resource_address(&user_addr, seed);
        let resource_cap = container.store.borrow(&resource_addr);

        let resource = account::create_signer_with_capability(resource_cap);
        let _resource_cap = retrieve_resource_account_cap(&resource, user_addr);
    }
```
